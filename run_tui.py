#!/usr/bin/env python3
"""Launcher for TempNumber TUI."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tempnumber.tui import TempNumberTUI

if __name__ == "__main__":
    TempNumberTUI().run()
