"""
TempNumber Textual TUI Application
Complete terminal interface for public/private numbers, SMS, and Coin farming
"""

import re
import time
import sys
import os

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Input, Static, Label, TabbedContent, TabPane,
    Select, DataTable, Switch, Log
)
from textual.binding import Binding

try:
    from .client import TempNumberClient
    from .config import TempNumberConfig
except (ImportError, ValueError):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tempnumber.client import TempNumberClient
    from tempnumber.config import TempNumberConfig


class TempNumberTUI(App):
    """Modern Terminal User Interface for Disposable Phone Numbers & SMS."""

    CSS = """
    Screen {
        background: #090e17;
        color: #f1f5f9;
    }

    Header {
        background: #0d9488;
        color: #ffffff;
        text-style: bold;
    }

    Footer {
        background: #0f172a;
        color: #94a3b8;
    }

    .card {
        background: #1e293b;
        border: solid #334155;
        padding: 1 2;
        margin: 1;
    }

    .card-title {
        text-style: bold;
        color: #2dd4bf;
        margin-bottom: 1;
    }

    .num-banner {
        background: #134e4a;
        border: solid #14b8a6;
        padding: 1 2;
        margin: 1;
        text-align: center;
    }

    .num-val {
        color: #5eead4;
        text-style: bold;
    }

    .otp-banner {
        background: #022c22;
        border: solid #10b981;
        padding: 1;
        margin: 1;
        text-align: center;
    }

    .otp-val {
        color: #34d399;
        text-style: bold;
    }

    .coin-banner {
        background: #78350f;
        border: solid #f59e0b;
        padding: 1 2;
        margin: 1;
        text-align: center;
    }

    .coin-val {
        color: #fde68a;
        text-style: bold;
    }

    Button {
        margin-top: 1;
        width: 100%;
        background: #0d9488;
        color: white;
    }

    Button:hover {
        background: #14b8a6;
    }

    Button.accent {
        background: #2563eb;
    }

    Button.accent:hover {
        background: #3b82f6;
    }

    Button.gold {
        background: #d97706;
    }

    Button.gold:hover {
        background: #f59e0b;
    }

    Button.success {
        background: #059669;
    }

    Button.success:hover {
        background: #10b981;
    }

    Input {
        margin-bottom: 1;
        border: solid #475569;
        background: #0f172a;
        color: #f8fafc;
    }

    DataTable {
        height: 10;
        border: solid #334155;
        background: #020617;
    }

    Log {
        height: 12;
        border: solid #334155;
        background: #020617;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh_all", "Refresh SMS", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = TempNumberConfig()
        self.client = TempNumberClient(self.config)
        self.numbers = []
        self.messages = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="tab-main"):

            # 1. MAIN NUMBERS & SMS
            with TabPane("Numbers & SMS", id="tab-main"):
                with ScrollableContainer():
                    with Vertical(classes="num-banner"):
                        yield Label("Active Disposable Number:", classes="card-title")
                        yield Label(self.client.active_number or "Select a number below", id="lbl-active-number", classes="num-val")
                        with Horizontal():
                            yield Button("Check Messages (SMS)", id="btn-check-sms", classes="accent")
                            yield Button("Bookmark as Favorite", id="btn-fav-add")

                    with Vertical(classes="otp-banner"):
                        yield Label("Latest Extracted OTP / Verification Code:", classes="card-title")
                        yield Label("------", id="lbl-otp-val", classes="otp-val")

                    with Container(classes="card"):
                        yield Label("Select Country:", classes="card-title")
                        yield Select([("United States (+1)", "United States"), ("United Kingdom (+44)", "United Kingdom"), ("Canada (+1)", "Canada"), ("France (+33)", "France"), ("Netherlands (+31)", "Netherlands")], id="sel-country")
                        yield Label("Available Numbers for Selected Country:", classes="card-title")
                        yield DataTable(id="tbl-numbers")

                    with Container(classes="card"):
                        yield Label("Incoming SMS Inbox:", classes="card-title")
                        yield DataTable(id="tbl-sms")

            # 2. MESSAGE INSPECTOR
            with TabPane("Message Viewer", id="tab-viewer"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("SMS Message Details", classes="card-title")
                        yield Label("Sender: -", id="lbl-sms-from")
                        yield Label("Recipient: -", id="lbl-sms-to")
                        yield Label("Time: -", id="lbl-sms-time")
                        yield Label("Message Content:", classes="card-title")
                        yield Static("Select an incoming message to read full text.", id="lbl-sms-body")

            # 3. COINS & FARMING
            with TabPane("Coins & Rewards", id="tab-coins"):
                with ScrollableContainer():
                    with Vertical(classes="coin-banner"):
                        yield Label("Current Coin Balance:", classes="card-title")
                        yield Label("450 Coins", id="lbl-coin-balance", classes="coin-val")
                        yield Button("Automate All Farming (Check-in + Spin + Box)", id="btn-farm-all", classes="gold")

                    with Container(classes="card"):
                        yield Label("Individual Reward Actions", classes="card-title")
                        with Horizontal():
                            yield Button("Daily Check-in (+30)", id="btn-daily-check")
                            yield Button("Spin Lucky Wheel (+50)", id="btn-spin-wheel")
                            yield Button("Open Surprise Box (+20)", id="btn-surprise-box")

            # 4. PRIVATE NUMBERS
            with TabPane("Private Numbers", id="tab-private"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("My Dedicated Rented Numbers", classes="card-title")
                        yield DataTable(id="tbl-private-numbers")
                        yield Button("Refresh Rented Numbers", id="btn-refresh-private")

                    with Container(classes="card"):
                        yield Label("Rent a Private Number with Coins", classes="card-title")
                        yield Label("Inventory ID:")
                        yield Input(placeholder="inv_us_01", id="inp-rent-inv")
                        yield Button("Rent with Coins", id="btn-rent-submit", classes="success")

            # 5. FAVORITES
            with TabPane("Favorites", id="tab-favs"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("Saved Favorite Numbers", classes="card-title")
                        yield DataTable(id="tbl-favorites")
                        yield Button("Refresh Favorites", id="btn-refresh-favs")

            # 6. ALL COUNTRIES
            with TabPane("All Countries (62)", id="tab-countries"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("Supported Country Directory", classes="card-title")
                        yield DataTable(id="tbl-all-countries")
                        yield Button("Reload Countries List", id="btn-reload-countries")

            # 7. SETTINGS
            with TabPane("Settings", id="tab-settings"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("Gateway & Configuration", classes="card-title")
                        yield Label("API Gateway Base URL:")
                        yield Input(value=self.config.get("base_url"), id="inp-cfg-base")
                        yield Label("User Agent:")
                        yield Input(value=self.config.get("user_agent"), id="inp-cfg-ua")
                        yield Label("Saved Active Number:")
                        yield Input(value=self.config.get("active_number"), id="inp-cfg-num")
                        with Horizontal():
                            yield Label("Mock Mode: ")
                            yield Switch(value=self.config.get("mock_mode"), id="sw-cfg-mock")
                        yield Button("Save Configuration", id="btn-cfg-save")

            # 8. LOG
            with TabPane("Activity Log", id="tab-log"):
                with Container(classes="card"):
                    yield Label("Live Request & OTP Log", classes="card-title")
                    yield Log(id="log-main")

        yield Footer()

    def on_mount(self) -> None:
        tbl_num = self.query_one("#tbl-numbers", DataTable)
        tbl_num.add_columns("ID", "Phone Number", "Country", "Release")

        tbl_sms = self.query_one("#tbl-sms", DataTable)
        tbl_sms.add_columns("From", "Message Preview", "Time")

        tbl_all_c = self.query_one("#tbl-all-countries", DataTable)
        tbl_all_c.add_columns("Code", "Country Name", "ID")

        tbl_priv = self.query_one("#tbl-private-numbers", DataTable)
        tbl_priv.add_columns("Number", "Country", "Expires")

        tbl_fav = self.query_one("#tbl-favorites", DataTable)
        tbl_fav.add_columns("Number", "Country")

        self.action_load_countries()
        self.action_load_numbers("United States")
        self.action_refresh_coins()
        self.log_msg("TempNumber TUI initialized.")

    def log_msg(self, msg: str) -> None:
        try:
            self.query_one("#log-main", Log).write_line(f"[{time.strftime('%H:%M:%S')}] {msg}")
        except Exception:
            pass

    def action_load_countries(self) -> None:
        countries = self.client.get_countries()
        tbl = self.query_one("#tbl-all-countries", DataTable)
        tbl.clear()
        for c in countries:
            tbl.add_row(c.get("country_code", "-"), c.get("Country_Name", "-"), str(c.get("id", "-")))
        self.log_msg(f"Loaded {len(countries)} countries.")

    def action_load_numbers(self, country: str) -> None:
        nums = self.client.get_numbers(country_name=country, page=1, limit=20)
        self.numbers = nums
        tbl = self.query_one("#tbl-numbers", DataTable)
        tbl.clear()
        for n in nums:
            nid = str(n.get("id", "-"))
            num = n.get("ToNumber", "-")
            cname = n.get("country_name", "-")
            rel = n.get("release_time", "-")
            tbl.add_row(nid, num, cname, rel, key=num)

        if nums and not self.client.active_number:
            first = nums[0].get("ToNumber")
            self.set_active_number(first)

        self.log_msg(f"Loaded {len(nums)} numbers for {country}.")

    def set_active_number(self, num: str) -> None:
        self.client.active_number = num
        self.config.set("active_number", num)
        self.config.save()
        self.query_one("#lbl-active-number", Label).update(num)
        self.query_one("#inp-cfg-num", Input).value = num
        self.log_msg(f"Active number set to: {num}")
        self.action_check_sms()

    def action_check_sms(self) -> None:
        if not self.client.active_number:
            return
        msgs = self.client.get_messages(self.client.active_number)
        self.messages = msgs
        tbl = self.query_one("#tbl-sms", DataTable)
        tbl.clear()

        re_otp = re.compile(r"\b\d{4,8}\b")
        latest_otp = None

        for m in msgs:
            mfrom = m.get("FromNumber", "Unknown")
            body = m.get("Messagebody", "")
            mtime = m.get("message_time", "-")
            preview = body.replace("\n", " ")[:60]
            tbl.add_row(mfrom, preview, mtime)

            if not latest_otp:
                mat = re_otp.findall(body)
                if mat:
                    latest_otp = mat[0]

        if latest_otp:
            self.query_one("#lbl-otp-val", Label).update(f"CODE: {latest_otp}")
            self.log_msg(f"Extracted OTP: {latest_otp}")

        self.log_msg(f"SMS Inbox refreshed: {len(msgs)} messages.")

    def action_refresh_coins(self) -> None:
        res = self.client.get_user_coins()
        coins = res.get("coins") or res.get("balance", 0)
        self.query_one("#lbl-coin-balance", Label).update(f"{coins} Coins")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-check-sms":
            self.action_check_sms()
        elif bid == "btn-fav-add":
            if self.client.active_number:
                self.client.add_favorite(self.client.active_number)
                self.log_msg(f"Bookmarked {self.client.active_number} to favorites.")
        elif bid == "btn-farm-all":
            self.log_msg("Running automated coin farming...")
            r = self.client.farm_all_coins()
            self.action_refresh_coins()
            self.log_msg("Farmed daily check-in, wheel spin, and surprise box!")
        elif bid == "btn-daily-check":
            r = self.client.perform_daily_checkin()
            self.action_refresh_coins()
            self.log_msg("Daily check-in claimed.")
        elif bid == "btn-spin-wheel":
            r = self.client.spin_wheel()
            self.action_refresh_coins()
            self.log_msg("Lucky wheel spun!")
        elif bid == "btn-surprise-box":
            r = self.client.open_surprise_box()
            self.action_refresh_coins()
            self.log_msg("Surprise box opened!")
        elif bid == "btn-refresh-private":
            privs = self.client.get_purchased_numbers()
            tbl = self.query_one("#tbl-private-numbers", DataTable)
            tbl.clear()
            for p in privs:
                tbl.add_row(p.get("number", "-"), p.get("country", "-"), p.get("expires", "-"))
            self.log_msg(f"Loaded {len(privs)} private numbers.")
        elif bid == "btn-rent-submit":
            inv = self.query_one("#inp-rent-inv", Input).value or "inv_01"
            r = self.client.rent_number_with_coins(inv)
            self.log_msg(f"Rented number with coins: {r.get('status')}")
        elif bid == "btn-refresh-favs":
            favs = self.client.get_favorites()
            tbl = self.query_one("#tbl-favorites", DataTable)
            tbl.clear()
            for f in favs:
                tbl.add_row(f.get("number", "-"), f.get("country", "-"))
            self.log_msg(f"Loaded {len(favs)} favorites.")
        elif bid == "btn-reload-countries":
            self.action_load_countries()
        elif bid == "btn-cfg-save":
            self.config.set("base_url", self.query_one("#inp-cfg-base", Input).value)
            self.config.set("user_agent", self.query_one("#inp-cfg-ua", Input).value)
            self.config.set("active_number", self.query_one("#inp-cfg-num", Input).value)
            self.config.set("mock_mode", self.query_one("#sw-cfg-mock", Switch).value)
            self.config.save()
            self.log_msg("Configuration saved successfully.")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        tbl_id = event.data_table.id
        if tbl_id == "tbl-numbers":
            selected_num = str(event.row_key.value)
            self.set_active_number(selected_num)
        elif tbl_id == "tbl-sms":
            idx = event.cursor_row
            if 0 <= idx < len(self.messages):
                m = self.messages[idx]
                self.query_one("#lbl-sms-from", Label).update(f"Sender: {m.get('FromNumber')}")
                self.query_one("#lbl-sms-to", Label).update(f"Recipient: {m.get('ToNumber')}")
                self.query_one("#lbl-sms-time", Label).update(f"Time: {m.get('message_time')}")
                self.query_one("#lbl-sms-body", Static).update(m.get("Messagebody", "(Empty Message)"))
        elif tbl_id == "tbl-favorites" or tbl_id == "tbl-private-numbers":
            pass


if __name__ == "__main__":
    app = TempNumberTUI()
    app.run()
