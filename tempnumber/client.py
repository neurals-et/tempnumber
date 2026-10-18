"""
TempNumber Core API Client
Complete reverse-engineered implementation of com.tempnumber.Temp_Number.Temp_Number
"""

import json
import re
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .config import TempNumberConfig, DEFAULT_BASE_URL, DEFAULT_USER_AGENT


class TempNumberClient:
    """Complete API Client for Temp-Number disposable SMS & Coin rewards platform."""

    def __init__(self, config: Optional[TempNumberConfig] = None, token: Optional[str] = None):
        self.config = config or TempNumberConfig()
        self.base_url = self.config.get("base_url", DEFAULT_BASE_URL).rstrip("/")
        self.active_number = self.config.get("active_number", "")
        self.token = token or self.config.get("auth_token", "")

    def _headers(self) -> Dict[str, str]:
        h = {
            "User-Agent": self.config.get("user_agent", DEFAULT_USER_AGENT),
            "X-Platform": "android",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}" if not self.token.startswith("Bearer ") else self.token
        return h

    def _request(self, endpoint: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.config.get("mock_mode"):
            if "country" in endpoint:
                return {
                    "records": [
                        {"id": 72, "country_code": "+1", "Country_Name": "United States"},
                        {"id": 71, "country_code": "+44", "Country_Name": "United Kingdom"},
                        {"id": 73, "country_code": "+1", "Country_Name": "Canada"},
                        {"id": 76, "country_code": "+33", "Country_Name": "France"}
                    ]
                }
            elif "numbers" in endpoint:
                return {
                    "available_numbers": [
                        {"id": 101, "ToNumber": "+12544525112", "country_name": "United States", "release_time": "1 hour ago"},
                        {"id": 102, "ToNumber": "+12264550694", "country_name": "United States", "release_time": "2 hours ago"}
                    ]
                }
            elif "sms" in endpoint or "premium-sms" in endpoint:
                return {
                    "messages": [
                        {
                            "ToNumber": self.active_number or "+12544525112",
                            "FromNumber": "Google",
                            "Messagebody": "G-492019 is your Google verification code.",
                            "message_time": "1 minute ago"
                        }
                    ]
                }
            elif "getUserCoins" in endpoint:
                return {"status": "SUCCESS", "coins": 450, "balance": 450}
            elif "spinWheel" in endpoint:
                return {"status": "SUCCESS", "reward_coins": 50, "total_coins": 500}
            elif "performDailyCheck" in endpoint:
                return {"status": "SUCCESS", "reward_coins": 30, "total_coins": 530}
            elif "openSurpriseBox" in endpoint:
                return {"status": "SUCCESS", "reward_coins": 20, "total_coins": 550}
            elif "purchased-numbers" in endpoint:
                return {
                    "purchased_numbers": [
                        {"id": "p_01", "number": "+14155552671", "country": "United States", "expires": "2026-11-01"}
                    ]
                }
            elif "favorite-numbers" in endpoint:
                return {
                    "favorites": [
                        {"id": 1, "number": "+12544525112", "country": "United States"}
                    ]
                }
            return {"status": "SUCCESS"}

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        data = json.dumps(payload).encode() if payload else None
        req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", "replace")
                return json.loads(content)
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", "replace")
            try:
                return {"error": True, "http_code": e.code, "details": json.loads(err)}
            except Exception:
                return {"error": True, "http_code": e.code, "message": err}
        except Exception as e:
            return {"error": True, "message": str(e)}

    # ------------------ Free Numbers & Public SMS ------------------

    def get_countries(self) -> List[Dict[str, Any]]:
        """GET api/country - List 62 supported countries."""
        res = self._request("api/country", method="GET")
        if isinstance(res, dict) and "records" in res:
            return res.get("records", [])
        return []

    def get_numbers(self, country_name: str = "United States", page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """POST api/numbers - Fetch available active phone numbers for a country."""
        payload = {
            "countryName": country_name,
            "page": page,
            "limit": limit
        }
        res = self._request("api/numbers", method="POST", payload=payload)
        if isinstance(res, dict) and "available_numbers" in res:
            return res.get("available_numbers", [])
        return []

    def get_messages(self, phone_number: Optional[str] = None, page: int = 1) -> List[Dict[str, Any]]:
        """POST api/sms - Fetch incoming SMS messages for a public phone number."""
        num = phone_number or self.active_number
        if not num:
            return []
        payload = {
            "no": num,
            "page": str(page)
        }
        res = self._request("api/sms", method="POST", payload=payload)
        if isinstance(res, dict) and "messages" in res:
            return res.get("messages", [])
        return []

    def wait_for_otp(self, phone_number: str, timeout_secs: int = 90, interval: int = 3) -> Optional[Dict[str, Any]]:
        """Poll the SMS inbox of a phone number and extract the first OTP code."""
        start = time.time()
        seen_msgs = set()
        while time.time() - start < timeout_secs:
            msgs = self.get_messages(phone_number)
            for m in msgs:
                body = m.get("Messagebody", "")
                mid = f"{m.get('FromNumber')}_{body}"
                if mid not in seen_msgs:
                    seen_msgs.add(mid)
                    matches = re.findall(r"\b\d{4,8}\b", body)
                    if matches:
                        return {
                            "code": matches[0],
                            "sender": m.get("FromNumber"),
                            "body": body,
                            "time": m.get("message_time")
                        }
            time.sleep(interval)
        return None

    # ------------------ Coins & Rewards System ------------------

    def get_user_coins(self) -> Dict[str, Any]:
        """GET api/coins/getUserCoins - Query active coin balance."""
        return self._request("api/coins/getUserCoins", method="GET")

    def get_daily_status(self) -> Dict[str, Any]:
        """GET api/coins/displayDailyStatus - Check daily reward readiness."""
        return self._request("api/coins/displayDailyStatus", method="GET")

    def perform_daily_checkin(self) -> Dict[str, Any]:
        """POST api/coins/performDailyCheck - Claim daily attendance reward."""
        return self._request("api/coins/performDailyCheck", method="POST")

    def spin_wheel(self) -> Dict[str, Any]:
        """POST api/coins/spinWheel - Spin daily lucky wheel for coins."""
        return self._request("api/coins/spinWheel", method="POST")

    def open_surprise_box(self) -> Dict[str, Any]:
        """POST api/coins/openSurpriseBox - Open mystery box reward."""
        return self._request("api/coins/openSurpriseBox", method="POST")

    def farm_all_coins(self) -> Dict[str, Any]:
        """One-click automated farming: claims daily checkin, spins wheel, and opens box."""
        check = self.perform_daily_checkin()
        spin = self.spin_wheel()
        box = self.open_surprise_box()
        coins = self.get_user_coins()
        return {
            "daily_check": check,
            "spin_wheel": spin,
            "surprise_box": box,
            "balance": coins
        }

    # ------------------ Private / Purchased Numbers ------------------

    def get_purchased_numbers(self) -> List[Dict[str, Any]]:
        """GET api/purchased-numbers - List user's dedicated rented numbers."""
        res = self._request("api/purchased-numbers", method="GET")
        if isinstance(res, dict) and "purchased_numbers" in res:
            return res.get("purchased_numbers", [])
        return []

    def get_private_messages(self, phone_number: str, page: int = 1) -> List[Dict[str, Any]]:
        """POST api/premium-sms - Read private SMS messages for a rented number."""
        payload = {"number": phone_number, "page": str(page)}
        res = self._request("api/premium-sms", method="POST", payload=payload)
        if isinstance(res, dict) and "messages" in res:
            return res.get("messages", [])
        return []

    def rent_number_with_coins(self, inventory_id: str, product_id: str = "coins_rent_1") -> Dict[str, Any]:
        """POST api/purchase-number-android - Rent a dedicated private number using coins."""
        payload = {
            "platform": "android",
            "inventory_id": inventory_id,
            "purchase_token": "COIN_PURCHASE",
            "product_id": product_id,
            "request_type": "coins"
        }
        return self._request("api/purchase-number-android", method="POST", payload=payload)

    def delete_purchased_number(self, number_id: str) -> Dict[str, Any]:
        """POST api/purchased-number - Release/delete rented number."""
        payload = {"id": number_id}
        return self._request("api/purchased-number", method="POST", payload=payload)

    # ------------------ Favorite Numbers ------------------

    def get_favorites(self) -> List[Dict[str, Any]]:
        """GET api/favorite-numbers - List bookmarked numbers."""
        res = self._request("api/favorite-numbers", method="GET")
        if isinstance(res, dict) and "favorites" in res:
            return res.get("favorites", [])
        return []

    def add_favorite(self, phone_number: str, country_name: str = "United States") -> Dict[str, Any]:
        """POST api/favorite-numbers/add - Bookmark a number."""
        payload = {"number": phone_number, "country": country_name}
        return self._request("api/favorite-numbers/add", method="POST", payload=payload)

    # ------------------ Account & Authentication ------------------

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """POST api/login - User account login."""
        payload = {"email": email, "password": password}
        res = self._request("api/login", method="POST", payload=payload)
        if isinstance(res, dict) and "token" in res:
            self.token = res["token"]
            self.config.set("auth_token", self.token)
            self.config.save()
        return res

    def register(self, email: str, password: str, name: str = "User") -> Dict[str, Any]:
        """POST api/register - Create new user account."""
        payload = {"email": email, "password": password, "name": name}
        return self._request("api/register", method="POST", payload=payload)

    def logout(self) -> Dict[str, Any]:
        """POST api/logout - Revoke active session."""
        return self._request("api/logout", method="POST")

    # ------------------ Support Tickets & FAQs ------------------

    def get_faqs(self) -> List[Dict[str, Any]]:
        """GET api/faqs - Retrieve support FAQs."""
        res = self._request("api/faqs", method="GET")
        if isinstance(res, list):
            return res
        return []

    def create_ticket(self, subject: str, message: str) -> Dict[str, Any]:
        """POST api/ticket/create - File customer support inquiry."""
        payload = {"subject": subject, "message": message}
        return self._request("api/ticket/create", method="POST", payload=payload)
