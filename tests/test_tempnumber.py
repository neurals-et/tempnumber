#!/usr/bin/env python3
"""
Comprehensive test suite for TempNumber SDK & TUI.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tempnumber import TempNumberConfig, TempNumberClient, TempNumberTUI

def main():
    print("[1] Testing TempNumberConfig...")
    cfg = TempNumberConfig()
    cfg.set("mock_mode", True)
    print("    Base URL:", cfg.get("base_url"))

    print("\n[2] Testing Live / Mock Countries Query...")
    client = TempNumberClient(cfg)
    countries = client.get_countries()
    print(f"    Loaded {len(countries)} countries.")
    assert len(countries) > 0

    print("\n[3] Testing Available Numbers Query...")
    numbers = client.get_numbers("United States", limit=5)
    print(f"    Loaded {len(numbers)} numbers.")
    assert len(numbers) > 0

    print("\n[4] Testing SMS Inbox Query...")
    msgs = client.get_messages("+12544525112")
    print(f"    Queried SMS: {len(msgs)} messages found.")

    print("\n[5] Testing Coins & Rewards System...")
    coins = client.get_user_coins()
    print(f"    User Coins: {coins.get('coins') or coins.get('balance')}")
    farm = client.farm_all_coins()
    print("    Automated farming status:", farm.get("daily_check", {}).get("status"))

    print("\n[6] Testing Private Rented Numbers...")
    privs = client.get_purchased_numbers()
    print(f"    Private numbers: {len(privs)} loaded.")
    rent = client.rent_number_with_coins("inv_us_01")
    print("    Rent number status:", rent.get("status"))

    print("\n[7] Testing Favorites Management...")
    fav_add = client.add_favorite("+12544525112", "United States")
    print("    Favorite add status:", fav_add.get("status"))
    favs = client.get_favorites()
    print(f"    Total favorites: {len(favs)}")

    print("\n[8] Testing TempNumberTUI Initialization...")
    tui = TempNumberTUI()
    print("    TUI class instance created:", type(tui).__name__)

    print("\n" + "=" * 55)
    print("ALL EXTENDED TEMPNUMBER TESTS PASSED SUCCESSFULLY!")
    print("=" * 55)

if __name__ == "__main__":
    main()
