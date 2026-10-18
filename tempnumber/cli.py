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
        description="TempNumber CLI & TUI - Disposable phone numbers, SMS verification & Coin rewards"
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

    # coins command
    subparsers.add_parser("coins", help="Check coin balance and daily status")

    # farm command
    subparsers.add_parser("farm", help="One-click automated coin farming (check-in + spin + box)")

    # private command
    subparsers.add_parser("private", help="View your rented private numbers")

    # rent command
    rent_p = subparsers.add_parser("rent", help="Rent a private number using coins")
    rent_p.add_argument("inventory_id", help="Inventory ID of the number to rent")

    # fav command
    fav_p = subparsers.add_parser("fav", help="Manage favorite bookmarked numbers")
    fav_p.add_argument("--add", help="Phone number to bookmark")
    fav_p.add_argument("--country", default="United States", help="Country of the number")

    # auth commands
    login_p = subparsers.add_parser("login", help="Log in to TempNumber account")
    login_p.add_argument("--email", "-e", required=True, help="Account email")
    login_p.add_argument("--password", "-p", required=True, help="Account password")

    reg_p = subparsers.add_parser("register", help="Create a TempNumber account")
    reg_p.add_argument("--email", "-e", required=True, help="Account email")
    reg_p.add_argument("--password", "-p", required=True, help="Account password")
    reg_p.add_argument("--name", default="User", help="Display name")

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
            sender = m.get('FromNumber', 'Unknown').encode('ascii', 'replace').decode('ascii')
            mtime = m.get('message_time', '-').encode('ascii', 'replace').decode('ascii')
            body = m.get('Messagebody', '').encode('ascii', 'replace').decode('ascii').strip()
            print(f"\n[From: {sender} | {mtime}]")
            print(f"  {body}")

    elif args.command == "code":
        client = TempNumberClient()
        print(f"Waiting up to {args.timeout}s for verification code on {args.number}...")
        otp_info = client.wait_for_otp(args.number, timeout_secs=args.timeout)
        if otp_info:
            print("\n[OK] VERIFICATION CODE EXTRACTED:")
            print(f"  Code:   {otp_info['code']}")
            print(f"  Sender: {otp_info['sender']}")
            body_clean = otp_info['body'][:120].encode('ascii', 'replace').decode('ascii')
            print(f"  Body:   {body_clean}...")
        else:
            print("Timed out waiting for SMS.", file=sys.stderr)
            sys.exit(1)

    elif args.command == "coins":
        client = TempNumberClient()
        c = client.get_user_coins()
        status = client.get_daily_status()
        print("=== TempNumber Coins Balance ===")
        print(f"  Total Coins:  {c.get('coins') or c.get('balance', 0)}")
        print(f"  Daily Status: {status.get('status', 'OK')}")

    elif args.command == "farm":
        client = TempNumberClient()
        print("Starting automated coin farming...")
        res = client.farm_all_coins()
        print("  Daily Check-in:", res.get("daily_check", {}).get("status", "SUCCESS"))
        print("  Lucky Wheel:   ", res.get("spin_wheel", {}).get("status", "SUCCESS"))
        print("  Surprise Box:  ", res.get("surprise_box", {}).get("status", "SUCCESS"))
        print(f"\n[OK] Farming complete! Total Coins: {res.get('balance', {}).get('coins', 0)}")

    elif args.command == "private":
        client = TempNumberClient()
        nums = client.get_purchased_numbers()
        print(f"=== My Private Rented Numbers ({len(nums)}) ===")
        for p in nums:
            print(f"  {p.get('number')} ({p.get('country')}) - Expires: {p.get('expires', 'N/A')}")

    elif args.command == "rent":
        client = TempNumberClient()
        r = client.rent_number_with_coins(args.inventory_id)
        print(f"[OK] Rented number: {r.get('status')} | Inv ID: {args.inventory_id}")

    elif args.command == "fav":
        client = TempNumberClient()
        if args.add:
            r = client.add_favorite(args.add, args.country)
            print(f"[OK] Added to favorites: {args.add} ({r.get('status')})")
        else:
            favs = client.get_favorites()
            print(f"=== Favorite Numbers ({len(favs)}) ===")
            for f in favs:
                print(f"  * {f.get('number')} ({f.get('country')})")

    elif args.command == "login":
        client = TempNumberClient()
        r = client.login(args.email, args.password)
        if "token" in r:
            print("[OK] Logged in successfully! Session token saved.")
        else:
            print(f"Login failed: {r}")

    elif args.command == "register":
        client = TempNumberClient()
        r = client.register(args.email, args.password, args.name)
        print(f"Registration response: {r.get('status', 'OK')}")


if __name__ == "__main__":
    main()
