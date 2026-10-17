# tempnumber-client

> Python client and interactive Terminal User Interface (TUI) for temporary disposable phone numbers and SMS verification codes (`com.tempnumber.Temp_Number.Temp_Number`).

Maintained by [NeuralS](https://github.com/neurals-et).

---

## Features

- **62 Countries**: Free temporary phone numbers across United States, United Kingdom, Canada, France, Netherlands, Sweden, and more.
- **Instant SMS Inbox**: Live incoming SMS feed for receiving activation and verification texts.
- **Automated OTP Extractor**: Integrated regex parser to extract 4–8 digit verification codes from incoming SMS.
- **Interactive TUI**: Built with Textual for country selection, number browsing, and real-time OTP monitoring.
- **CLI Commands**: CLI tools (`tempnumber list`, `tempnumber sms`, `tempnumber code`) ready for CI/CD and script automation.

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
# or
tempnumber tui
```

### CLI Commands
```bash
# List supported countries
tempnumber countries

# List available active numbers for a country
tempnumber list --country "United States"

# View SMS inbox for a number
tempnumber sms +12544525112

# Wait for and print the next OTP code (automation ready)
tempnumber code +12544525112 --timeout 60
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
```

---

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/country` | List 62 supported countries |
| `POST` | `/api/numbers` | Query available active numbers for a country |
| `POST` | `/api/sms` | Query real-time incoming SMS messages for a number |

---

## License

MIT
