#!/usr/bin/env python3
"""
Test suite for TempNumber SDK & TUI.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tempnumber import TempNumberConfig, TempNumberClient, TempNumberTUI

def main():
    print("[1] Testing TempNumberConfig...")
    cfg = TempNumberConfig()
    print("    Base URL:", cfg.get("base_url"))
    print("    Default Country:", cfg.get("default_country"))

    print("\n[2] Testing Live Countries Query...")
    client = TempNumberClient(cfg)
    countries = client.get_countries()
    print(f"    Loaded {len(countries)} countries.")
    assert len(countries) >= 10, "Expected at least 10 countries"

    print("\n[3] Testing Live Available Numbers Query (US)...")
    numbers = client.get_numbers("United States", limit=5)
    print(f"    Loaded {len(numbers)} US numbers:")
    for n in numbers[:3]:
        print(f"      - {n.get('ToNumber')} (Released: {n.get('release_time')})")
    assert len(numbers) > 0, "Expected at least 1 US number"

    print("\n[4] Testing Live SMS Inbox Query...")
    test_num = numbers[0].get("ToNumber")
    msgs = client.get_messages(test_num)
    print(f"    Queried SMS for {test_num}: {len(msgs)} messages found.")

    print("\n[5] Testing TempNumberTUI Initialization...")
    tui = TempNumberTUI()
    print("    TUI class instance created:", type(tui).__name__)

    print("\n" + "=" * 55)
    print("ALL TEMPNUMBER TESTS PASSED SUCCESSFULLY! (100% LIVE)")
    print("=" * 55)

if __name__ == "__main__":
    main()
