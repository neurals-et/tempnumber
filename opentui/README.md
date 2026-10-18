# tempnumber-tui

> Modern Terminal User Interface for Temp-Number disposable phone numbers and SMS verification codes, built with [OpenTUI](https://github.com/anomalyco/opentui) and [opentui-spinner](https://opentui.com/packages/opentui-spinner/) on Bun.

---

## Features

- **OpenTUI Native Engine**: Built on `@opentui/core` with native terminal buffers.
- **Animated Spinners**: Integrates `opentui-spinner` (`dots` animation) for asynchronous number and SMS polling.
- **Pixel-Matched Theme**:
  - Pure black background (`#000000`) with thin white borders
  - Active tab indicators in `#353535` with `#FFFFFF` text
  - Live `<Ctrl-R>` API Traffic History overlay (`#1E1E1E`)
  - Green OTP received alert banner (`#A6FF86` on `#353535`)
- **6 Dedicated Workspaces**:
  1. `1: number` - Active disposable phone number and selection list
  2. `2: sms inbox` - Real-time incoming SMS feed
  3. `3: otp code` - Automated verification code parser
  4. `4: countries` - Directory of all 62 supported countries
  5. `5: coins` - Coin balance and automated one-click farming (`f` key)
  6. `6: private` - Dedicated private rented numbers

---

## Running the TUI

```bash
cd C:\Users\user\Desktop\Dev\tempnumber-tui
bun start
```

Or directly:

```bash
bun C:\Users\user\Desktop\Dev\tempnumber-tui\index.ts
```

---

## Keyboard Controls

| Key | Action |
|---|---|
| `q` | Quit application |
| `r` | Reload active SMS inbox (with spinner) |
| `<Ctrl-R>` | Toggle live API Traffic History overlay |
| `c` | Open country selection modal |
| `1` - `6` | Switch between workspace modes |
| `f` | Farm all daily coins (in Mode 5) |
| `Up` / `Down` | Navigate numbers or countries |
| `Enter` | Select number / country |
| `Escape` | Close any open modal |

---

## License

MIT
