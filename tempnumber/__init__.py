"""
TempNumber Unofficial Python Client & Interactive TUI
Reverse-engineered from Temp Number Android App (com.tempnumber.Temp_Number.Temp_Number)
"""

from .config import TempNumberConfig
from .client import TempNumberClient
from .tui import TempNumberTUI

__version__ = "0.1.0"
__author__ = "NeuralS"
__license__ = "MIT"

__all__ = ["TempNumberClient", "TempNumberConfig", "TempNumberTUI", "__version__"]
