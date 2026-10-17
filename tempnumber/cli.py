"""
TempNumber CLI Entry Point
"""

import sys
import argparse
from .client import TempNumberClient
from .config import TempNumberConfig
from .tui import TempNumberTUI


def main():
    parser = argparse.ArgumentParser(
        prog="tempnumber",
        description="TempNumber CLI & TUI - Disposable phone numbers & SMS verification codes"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # tui command
    subparsers.add_parser("tui", help="Launch interactive Textual TUI")

    # countries command
    subparsers.add_parser("countries", help="List all 62 available countries")

    # list command
    list_p = subparsers.add_parser("list", help="List available numbers for a country")
    list_p.add_argument("--country", "-c", default="United States", help="Country name (default: 'United States')")
    list_p.add_argument("--limit", "-l", type=int, default=15, help="Number of items to fetch")

    # sms command
    sms_p = subparsers.add_parser("sms", help="Read incoming SMS messages for a number")
    sms_p.add_argument("number", help="Phone number with country code (e.g. +12544525112)")

    # code command
    code_p = subparsers.add_parser("code", help="Wait for incoming SMS and extract verification code")
    code_p.add_argument("number", help="Phone number with country code (e.g. +12544525112)")
    code_p.add_argument("--timeout", "-t", type=int, default=60, help="Polling timeout in seconds (default: 60)")

    args = parser.parse_args()

    if args.command == "tui" or args.command is None:
        app = TempNumberTUI()
        app.run()

    elif args.command == "countries":
        client = TempNumberClient()
        countries = client.get_countries()
        print(f"=== Supported Countries ({len(countries)}) ===")
        for c in countries:
            print(f"[{c.get('country_code', '-'):>6}] {c.get('Country_Name', '-')}")

    elif args.command == "list":
        client = TempNumberClient()
        nums = client.get_numbers(country_name=args.country, limit=args.limit)
        print(f"=== Available Numbers for {args.country} ({len(nums)}) ===")
        for n in nums:
            print(f"  {n.get('ToNumber')} (Released: {n.get('release_time', '-')})")

    elif args.command == "sms":
        client = TempNumberClient()
        msgs = client.get_messages(args.number)
        print(f"=== Incoming SMS for {args.number} ({len(msgs)}) ===")
        if not msgs:
            print("No messages received yet.")
        for m in msgs:
            print(f"\n[From: {m.get('FromNumber')} | {m.get('message_time')}]")
            print(f"  {m.get('Messagebody', '').strip()}")

    elif args.command == "code":
        client = TempNumberClient()
        print(f"Waiting up to {args.timeout}s for verification code on {args.number}...")
        otp_info = client.wait_for_otp(args.number, timeout_secs=args.timeout)
        if otp_info:
            print("\n[OK] VERIFICATION CODE EXTRACTED:")
            print(f"  Code:   {otp_info['code']}")
            print(f"  Sender: {otp_info['sender']}")
            print(f"  Body:   {otp_info['body'][:120]}...")
        else:
            print("Timed out waiting for SMS.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
