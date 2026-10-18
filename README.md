# tempnumber-client

> Python client and interactive Terminal User Interface (TUI) for temporary disposable phone numbers, SMS verification codes, and coin rewards (`com.tempnumber.Temp_Number.Temp_Number`).

Maintained by [NeuralS](https://github.com/neurals-et).

---

## Features

- **62 Countries**: Free temporary phone numbers across United States, United Kingdom, Canada, France, Netherlands, Sweden, etc.
- **Live SMS Feed**: Real-time incoming SMS messages for receiving verification texts.
- **Automated OTP Extractor**: Integrated regex engine that extracts 4–8 digit verification codes automatically.
- **Coin Rewards & Farming**: Check-in daily, spin the lucky wheel, and open mystery boxes to earn coins.
- **Private Numbers**: Rent dedicated, private numbers using earned coins.
- **Favorites**: Bookmark frequently used phone numbers.
- **Interactive TUI**: 8-tab terminal dashboard powered by Textual.
- **CLI Commands**: Terminal utilities (`tempnumber list`, `tempnumber sms`, `tempnumber code`, `tempnumber farm`).

---

## Installation

```bash
pip install .
```

---

## Quickstart

### Terminal Dashboard
```bash
tempnumber
```

### CLI Commands
```bash
# List supported countries
tempnumber countries

# List available active numbers for a country
tempnumber list --country "United States"

# View SMS inbox for a number
tempnumber sms +12544525112

# Wait for and print the next OTP code
tempnumber code +12544525112 --timeout 60

# Check coin balance
tempnumber coins

# Automated one-click coin farming
tempnumber farm

# View private rented numbers
tempnumber private

# Manage bookmarked favorites
tempnumber fav
tempnumber fav --add +12544525112
```

### Python SDK
```python
from tempnumber import TempNumberClient

client = TempNumberClient()

# 1. Fetch available US numbers
numbers = client.get_numbers(country_name="United States")
phone = numbers[0]["ToNumber"]
print(f"Selected Phone: {phone}")

# 2. Check incoming SMS messages
messages = client.get_messages(phone)
for m in messages:
    print(f"[{m['FromNumber']}] {m['Messagebody']}")

# 3. Automatically wait for an OTP verification code
otp = client.wait_for_otp(phone, timeout_secs=60)
if otp:
    print(f"Extracted OTP: {otp['code']} from {otp['sender']}")

# 4. Automate daily coin farming
farm = client.farm_all_coins()
print("Farmed Coins Balance:", farm["balance"])
```

---

## Endpoints

| Category | Endpoint | Method | Description |
|---|---|---|---|
| **Public** | `/api/country` | `GET` | List 62 supported countries |
| **Public** | `/api/numbers` | `POST` | Query available active numbers |
| **Public** | `/api/sms` | `POST` | Read real-time incoming SMS messages |
| **Coins** | `/api/coins/getUserCoins` | `GET` | Check coin balance |
| **Coins** | `/api/coins/performDailyCheck` | `POST` | Claim daily attendance reward |
| **Coins** | `/api/coins/spinWheel` | `POST` | Spin lucky wheel for coins |
| **Coins** | `/api/coins/openSurpriseBox` | `POST` | Open mystery box reward |
| **Private**| `/api/purchased-numbers` | `GET` | List user's dedicated rented numbers |
| **Private**| `/api/purchase-number-android` | `POST` | Rent number using earned coins |
| **Private**| `/api/premium-sms` | `POST` | Read private number SMS |
| **Favs** | `/api/favorite-numbers` | `GET` / `POST` | Manage bookmarked numbers |

---

## License

MIT
