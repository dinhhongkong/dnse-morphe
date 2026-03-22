from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
from datetime import UTC, datetime
from typing import Any
from urllib import parse
from uuid import uuid4

import httpx

from dnse_morphe._constants import BASE_URL, CONTENT_TYPE_JSON, DEFAULT_TIMEOUT, SENSITIVE_HEADERS
from dnse_morphe._utils._logs import setup_logging
from dnse_morphe.resources import Accounts, MarketData, Orders

logger = logging.getLogger("dnse-morphe")


class BaseDNSEClient:
    accounts: Accounts
    orders: Orders
    market_data: MarketData

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        hmac_nonce_enabled: bool = True,
    ) -> None:
        setup_logging()
        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._hmac_nonce_enabled = hmac_nonce_enabled

        self.accounts = Accounts(self)
        self.orders = Orders(self)
        self.market_data = MarketData(self)

    def _get_date_header_name(self) -> str:
        return os.getenv("DATE_HEADER", "Date")

    def _date_header(self) -> str:
        return datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S %z")

    def _build_signature(
        self,
        secret: str,
        method: str,
        path: str,
        date_value: str,
        algorithm: str = "hmac-sha256",
        nonce: str | None = None,
    ) -> tuple[str, str]:
        header_name = self._get_date_header_name()
        header_key = header_name.lower()
        signature_string = f"(request-target): {method.lower()} {path}\n{header_key}: {date_value}"
        if nonce:
            signature_string += f"\nnonce: {nonce}"

        if algorithm == "hmac-sha256":
            digestmod = hashlib.sha256
        elif algorithm == "hmac-sha384":
            digestmod = hashlib.sha384
        elif algorithm == "hmac-sha512":
            digestmod = hashlib.sha512
        else:
            digestmod = hashlib.sha1

        mac = hmac.new(secret.encode("utf-8"), signature_string.encode("utf-8"), digestmod)
        encoded = base64.b64encode(mac.digest()).decode("utf-8")
        escaped = parse.quote(encoded, safe="")
        return f"(request-target) {header_key}", escaped

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        dry_run: bool = False,
    ) -> tuple[int, str | None]:
        url = self._build_url(path, query)
        date_value = self._date_header()
        nonce = uuid4().hex if self._hmac_nonce_enabled else None
        headers_list, signature = self._build_signature(
            self._api_secret,
            method,
            path,
            date_value,
            nonce=nonce,
        )
        sig_header = (
            f'Signature keyId="{self._api_key}",algorithm="hmac-sha256",'
            f'headers="{headers_list}",signature="{signature}"'
        )
        if nonce:
            sig_header += f',nonce="{nonce}"'

        request_headers: dict[str, str] = {
            self._get_date_header_name(): date_value,
            "X-Signature": sig_header,
            "x-api-key": self._api_key,
        }
        if body is not None:
            request_headers["Content-Type"] = CONTENT_TYPE_JSON
        if headers:
            request_headers.update(headers)

        safe_headers = {
            k: ("<redacted>" if k.lower() in SENSITIVE_HEADERS else v)
            for k, v in request_headers.items()
        }
        logger.debug(f"HTTP {method} {url} headers={safe_headers} body={body}")

        if dry_run:
            return 0, None

        client = httpx.Client(timeout=self._timeout)
        try:
            req = client.build_request(method, url, json=body, headers=request_headers)
            response = client.send(req)
            body_text = response.text
            logger.debug(f"HTTP {response.status_code} {body_text[:500]}")
            return response.status_code, body_text
        except httpx.HTTPStatusError as e:
            body_text = e.response.text
            logger.error(f"HTTP error {e.response.status_code}: {body_text}")
            return e.response.status_code, body_text
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return 0, str(e)
        finally:
            client.close()

    def _build_url(self, path: str, query: dict[str, Any] | None) -> str:
        url = f"{self._base_url}{path}"
        if query:
            url = f"{url}?{parse.urlencode(query)}"
        return url
