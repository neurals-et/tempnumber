"""
TempNumber Core API Client
"""

import json
import re
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .config import TempNumberConfig, DEFAULT_BASE_URL, DEFAULT_USER_AGENT


class TempNumberClient:
    """Core API Client for Temp-Number disposable SMS service."""

    def __init__(self, config: Optional[TempNumberConfig] = None):
        self.config = config or TempNumberConfig()
        self.base_url = self.config.get("base_url", DEFAULT_BASE_URL).rstrip("/")
        self.active_number = self.config.get("active_number", "")

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.config.get("user_agent", DEFAULT_USER_AGENT),
            "X-Platform": "android",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _request(self, endpoint: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.config.get("mock_mode"):
            if "country" in endpoint:
                return {
                    "records": [
                        {"id": 72, "country_code": "+1", "Country_Name": "United States"},
                        {"id": 71, "country_code": "+44", "Country_Name": "United Kingdom"}
                    ]
                }
            elif "numbers" in endpoint:
                return {
                    "available_numbers": [
                        {"id": 101, "ToNumber": "+12544525112", "country_name": "United States", "release_time": "1 hour ago"},
                        {"id": 102, "ToNumber": "+12264550694", "country_name": "United States", "release_time": "2 hours ago"}
                    ]
                }
            elif "sms" in endpoint:
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

    # ------------------ Core Public Endpoints ------------------

    def get_countries(self) -> List[Dict[str, Any]]:
        """GET /api/country - List all supported countries."""
        res = self._request("api/country", method="GET")
        if isinstance(res, dict) and "records" in res:
            return res.get("records", [])
        return []

    def get_numbers(self, country_name: str = "United States", page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """POST /api/numbers - Fetch available active phone numbers for a country."""
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
        """POST /api/sms - Fetch incoming SMS messages for a phone number."""
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
                    # Extract 4 to 8 digit verification codes
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
