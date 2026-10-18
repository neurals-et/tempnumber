import asyncio
import sys
sys.path.insert(0, r"C:\Users\user\Desktop\Dev\TempNumber")
from tempnumber.tui import TempNumberTUI

async def test_tui():
    app = TempNumberTUI()
    async with app.run_test() as pilot:
        print("Mounted, waiting 2s...")
        await pilot.pause(2.0)
        print("TUI ran successfully without crashing!")

if __name__ == "__main__":
    asyncio.run(test_tui())
