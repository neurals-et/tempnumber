import asyncio
import sys
sys.path.insert(0, r"C:\Users\user\Desktop\Dev\CBEMobile")
sys.path.insert(0, r"C:\Users\user\Desktop\Dev\TempMail")
sys.path.insert(0, r"C:\Users\user\Desktop\Dev\TempNumber")

from cbe.tui import CBEMobileTUI
from tempmail.tui import TempMailTUI
from tempnumber.tui import TempNumberTUI

async def test_all():
    print("[1] Testing CBEMobileTUI headless run...")
    app1 = CBEMobileTUI()
    async with app1.run_test() as p:
        await p.pause(1.0)
    print("    [OK] CBEMobileTUI ran with 0 errors!")

    print("\n[2] Testing TempMailTUI headless run...")
    app2 = TempMailTUI()
    async with app2.run_test() as p:
        await p.pause(1.0)
    print("    [OK] TempMailTUI ran with 0 errors!")

    print("\n[3] Testing TempNumberTUI headless run...")
    app3 = TempNumberTUI()
    async with app3.run_test() as p:
        await p.pause(1.0)
    print("    [OK] TempNumberTUI ran with 0 errors!")

    print("\nALL 3 TUIS TESTED AND VERIFIED WORKING!")

if __name__ == "__main__":
    asyncio.run(test_all())
