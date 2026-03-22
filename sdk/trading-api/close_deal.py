#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sdk.dnse import DNSEClient


def main():
    client = DNSEClient(
        api_key="replace-with-api-key",
        api_secret="replace-with-api-secret",
        base_url="https://openapi.dnse.com.vn",
    )

    payload = {}

    status, body = client.close_deal(
        account_no="replace-with-account-no",
        deal_id="replace-with-deal-id",
        market_type="DERIVATIVE",
        payload=payload,
        trading_token="replace-with-trading-token",
        dry_run=False,
    )
    print(status, body)


if __name__ == "__main__":
    main()
