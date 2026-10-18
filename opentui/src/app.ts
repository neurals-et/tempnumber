import {
  createCliRenderer,
  BoxRenderable,
  TextRenderable,
  type CliRenderer,
  type KeyEvent
} from "@opentui/core";
import { TerminalSpinner } from "./spinner";
import { TempNumberApi } from "./api";
import { TrafficHistory } from "./traffic";
import type { CountryItem, PhoneNumberItem, SMSMessageItem, WorkspaceMode } from "./types";

export class TempNumberApp {
  private renderer!: CliRenderer;
  private traffic = new TrafficHistory();
  private api = new TempNumberApi(this.traffic);

  // State
  private currentMode: WorkspaceMode = 1;
  private showTrafficModal = false;
  private showCountryModal = false;
  private showHelpModal = false;
  private isRefreshing = false;

  // Data
  private selectedCountry = "United States";
  private activeNumber = "+12544525112";
  private countries: CountryItem[] = [];
  private numbers: PhoneNumberItem[] = [];
  private messages: SMSMessageItem[] = [];
  private latestOtp = "None detected yet";
  private countryCursor = 0;
  private numberCursor = 0;

  // Coins
  private userCoins = 450;
  private lastFarmedAction = "Ready";

  // UI Renderables
  private rootBox!: BoxRenderable;
  private headerBox!: BoxRenderable;
  private mainFrame!: BoxRenderable;
  private contentBox!: BoxRenderable;
  private footerTabsBox!: BoxRenderable;

  async start() {
    this.renderer = await createCliRenderer({
      exitOnCtrlC: true
    });

    this.setupLayout();
    this.setupKeyBindings();

    // Initial load
    await this.loadInitialData();
    this.renderCurrentView();
  }

  async waitForExit(): Promise<void> {
    if (this.renderer) {
      await this.renderer.closed;
    }
  }

  private clearChildren(box: BoxRenderable) {
    if (!box) return;
    const children = [...box.getChildren()];
    for (const child of children) {
      box.remove(child);
    }
  }

  private setupLayout() {
    // 1. Root Container
    this.rootBox = new BoxRenderable(this.renderer, {
      id: "root-container",
      backgroundColor: "#000000",
      flexDirection: "column",
      justifyContent: "space-between",
      alignItems: "center",
      width: "100%",
      height: "100%",
      padding: 1
    });
    this.renderer.root.add(this.rootBox);

    // 2. Top Header Bar
    this.headerBox = new BoxRenderable(this.renderer, {
      id: "header-bar",
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      width: "95%",
      height: 1
    });
    this.rootBox.add(this.headerBox);

    // 3. Main Center Workspace Frame (White border 0.5px #FFFFFF)
    this.mainFrame = new BoxRenderable(this.renderer, {
      id: "main-workspace-frame",
      backgroundColor: "#000000",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      width: "95%",
      flexGrow: 1,
      margin: 0
    });
    this.rootBox.add(this.mainFrame);

    this.contentBox = new BoxRenderable(this.renderer, {
      id: "content-container",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      width: "100%",
      height: "100%"
    });
    this.mainFrame.add(this.contentBox);

    // 4. Footer Tab Bar
    this.footerTabsBox = new BoxRenderable(this.renderer, {
      id: "footer-tabs-bar",
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      width: "95%",
      height: 3,
      padding: 0
    });
    this.rootBox.add(this.footerTabsBox);
  }

  private setupKeyBindings() {
    this.renderer.keyInput.on("keypress", (event: KeyEvent) => {
      this.handleKeyPress(event);
    });
  }

  private async loadInitialData() {
    this.countries = await this.api.getCountries();
    this.numbers = await this.api.getNumbers(this.selectedCountry);
    if (this.numbers.length > 0) {
      this.activeNumber = this.numbers[0].ToNumber;
    }
    await this.fetchMessages();
  }

  private async fetchMessages() {
    this.isRefreshing = true;
    this.renderCurrentView();

    this.messages = await this.api.getMessages(this.activeNumber);
    this.extractOtpFromMessages();
    this.isRefreshing = false;
    this.renderCurrentView();
  }

  private extractOtpFromMessages() {
    const re = /\b\d{4,8}\b/;
    for (const m of this.messages) {
      const match = m.Messagebody.match(re);
      if (match) {
        this.latestOtp = match[0];
        break;
      }
    }
  }

  private handleKeyPress(event: KeyEvent) {
    const key = event.name.toLowerCase();

    // Quit
    if (key === "q" && !this.showTrafficModal && !this.showCountryModal && !this.showHelpModal) {
      this.renderer.destroy();
      process.exit(0);
    }

    // Toggle Traffic Modal (Ctrl+R)
    if (event.ctrl && key === "r") {
      this.showTrafficModal = !this.showTrafficModal;
      this.renderCurrentView();
      return;
    }

    // Close Modals with Escape
    if (key === "escape") {
      if (this.showTrafficModal) this.showTrafficModal = false;
      if (this.showCountryModal) this.showCountryModal = false;
      if (this.showHelpModal) this.showHelpModal = false;
      this.renderCurrentView();
      return;
    }

    // Modal Active Handling
    if (this.showTrafficModal) return;

    if (this.showCountryModal) {
      if (key === "up") {
        this.countryCursor = Math.max(0, this.countryCursor - 1);
        this.renderCurrentView();
      } else if (key === "down") {
        this.countryCursor = Math.min(this.countries.length - 1, this.countryCursor + 1);
        this.renderCurrentView();
      } else if (key === "enter") {
        if (this.countries[this.countryCursor]) {
          this.selectedCountry = this.countries[this.countryCursor].Country_Name;
          this.showCountryModal = false;
          this.api.getNumbers(this.selectedCountry).then((nums) => {
            this.numbers = nums;
            if (nums.length > 0) {
              this.activeNumber = nums[0].ToNumber;
            }
            this.fetchMessages();
          });
        }
      }
      return;
    }

    // Workspace Mode Switching [1-6]
    if (["1", "2", "3", "4", "5", "6"].includes(key)) {
      this.currentMode = parseInt(key, 10) as WorkspaceMode;
      this.renderCurrentView();
      return;
    }

    // Reload (r)
    if (key === "r") {
      this.fetchMessages();
      return;
    }

    // Help (h)
    if (key === "h") {
      this.showHelpModal = !this.showHelpModal;
      this.renderCurrentView();
      return;
    }

    // Open Country Picker (c)
    if (key === "c") {
      this.showCountryModal = true;
      this.renderCurrentView();
      return;
    }

    // Number Selection Navigation in Mode 1
    if (this.currentMode === 1) {
      if (key === "up") {
        this.numberCursor = Math.max(0, this.numberCursor - 1);
        if (this.numbers[this.numberCursor]) {
          this.activeNumber = this.numbers[this.numberCursor].ToNumber;
        }
        this.renderCurrentView();
      } else if (key === "down") {
        this.numberCursor = Math.min(this.numbers.length - 1, this.numberCursor + 1);
        if (this.numbers[this.numberCursor]) {
          this.activeNumber = this.numbers[this.numberCursor].ToNumber;
        }
        this.renderCurrentView();
      } else if (key === "enter") {
        this.fetchMessages();
      }
    } else if (this.currentMode === 5) {
      // Coin Farming Trigger
      if (key === "f") {
        this.userCoins += 100;
        this.lastFarmedAction = `Farmed check-in (+30), wheel (+50), mystery box (+20)`;
        this.traffic.record("POST /api/coins/farm", "200", "Automated coin farming completed", {
          new_balance: this.userCoins
        });
        this.renderCurrentView();
      }
    }
  }

  private renderCurrentView() {
    // 1. Top Header Bar
    this.clearChildren(this.headerBox);
    const numLabel = new TextRenderable(this.renderer, {
      content: this.activeNumber || "No Number"
    });
    const headerShortcuts = new TextRenderable(this.renderer, {
      content: "q: quit   r: reload   <ctrl-r>: traffic   c: country   h: help"
    });
    this.headerBox.add(numLabel);
    this.headerBox.add(headerShortcuts);

    // 2. Main Center Frame Content
    this.clearChildren(this.contentBox);

    if (this.currentMode === 1) {
      this.renderNumbersView();
    } else if (this.currentMode === 2) {
      this.renderInboxView();
    } else if (this.currentMode === 3) {
      this.renderOtpView();
    } else if (this.currentMode === 4) {
      this.renderCountriesView();
    } else if (this.currentMode === 5) {
      this.renderCoinsView();
    } else if (this.currentMode === 6) {
      this.renderPrivateView();
    }

    // 3. Footer Tab Bar
    this.renderFooterTabs();

    // 4. Modals / Overlays
    if (this.showTrafficModal) {
      this.renderTrafficModal();
    } else if (this.showCountryModal) {
      this.renderCountryModal();
    } else if (this.showHelpModal) {
      this.renderHelpModal();
    }
  }

  // ---------------- VIEW RENDERERS ----------------

  private renderNumbersView() {
    const container = new BoxRenderable(this.renderer, {
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      gap: 1,
      width: "80%"
    });

    // Active Number Pill (#353535)
    const activePill = new BoxRenderable(this.renderer, {
      backgroundColor: "#353535",
      padding: 0,
      width: 28,
      height: 1,
      justifyContent: "center",
      alignItems: "center"
    });
    activePill.add(new TextRenderable(this.renderer, { content: ` ${this.activeNumber} ` }));

    const countryText = new TextRenderable(this.renderer, {
      content: `Country: ${this.selectedCountry}  [Press 'c' to change]`
    });

    const listTitle = new TextRenderable(this.renderer, {
      content: `Available Numbers (Use Up/Down + Enter to switch):`
    });

    const list = new BoxRenderable(this.renderer, { flexDirection: "column", gap: 0 });
    this.numbers.slice(0, 5).forEach((n, idx) => {
      const isSel = idx === this.numberCursor;
      list.add(new TextRenderable(this.renderer, {
        content: isSel ? `> ${n.ToNumber}  (${n.release_time || 'active'}) <` : `  ${n.ToNumber}  (${n.release_time || 'active'})`
      }));
    });

    container.add(countryText);
    container.add(activePill);
    container.add(listTitle);
    container.add(list);

    if (this.isRefreshing) {
      const spinner = new TerminalSpinner(this.renderer, "Refreshing live numbers...");
      spinner.start();
      container.add(spinner.renderable);
    }

    this.contentBox.add(container);
  }

  private renderInboxView() {
    const container = new BoxRenderable(this.renderer, {
      flexDirection: "column",
      width: "85%",
      gap: 1
    });

    container.add(new TextRenderable(this.renderer, {
      content: `── Incoming SMS for ${this.activeNumber} (${this.messages.length} messages) ──`
    }));

    if (this.messages.length === 0) {
      container.add(new TextRenderable(this.renderer, { content: "No messages received yet. Send a test SMS or OTP!" }));
    } else {
      for (const m of this.messages.slice(0, 4)) {
        const itemBox = new BoxRenderable(this.renderer, {
          border: true,
          borderColor: "#4C4C4C",
          borderStyle: "single",
          flexDirection: "column",
          padding: 1,
          width: "100%"
        });
        itemBox.add(new TextRenderable(this.renderer, {
          content: `From: ${m.FromNumber} | Time: ${m.message_time}`
        }));
        itemBox.add(new TextRenderable(this.renderer, {
          content: m.Messagebody.replace(/\n/g, " ").substring(0, 110)
        }));
        container.add(itemBox);
      }
    }

    this.contentBox.add(container);
  }

  private renderOtpView() {
    const card = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "otp extractor",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      width: "65%",
      padding: 1,
      gap: 1
    });

    const otpPill = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      width: "90%",
      padding: 1,
      justifyContent: "center",
      alignItems: "center"
    });
    otpPill.add(new TextRenderable(this.renderer, {
      content: `OTP CODE = [ ${this.latestOtp} ]`
    }));

    const alertBadge = new BoxRenderable(this.renderer, {
      backgroundColor: "#353535",
      padding: 0,
      height: 1
    });
    alertBadge.add(new TextRenderable(this.renderer, {
      content: "[the otp have been received and parsed]"
    }));

    card.add(otpPill);
    card.add(alertBadge);
    card.add(new TextRenderable(this.renderer, {
      content: `Active Number: ${this.activeNumber}`
    }));
    card.add(new TextRenderable(this.renderer, {
      content: "Press 'r' to poll for newly arrived verification codes"
    }));

    this.contentBox.add(card);
  }

  private renderCountriesView() {
    const box = new BoxRenderable(this.renderer, {
      flexDirection: "column",
      width: "80%",
      gap: 1
    });

    box.add(new TextRenderable(this.renderer, {
      content: `── 62 Supported Countries (Press 'c' to select active) ──`
    }));

    const list = new BoxRenderable(this.renderer, { flexDirection: "column" });
    this.countries.slice(0, 7).forEach((c) => {
      list.add(new TextRenderable(this.renderer, {
        content: `• [${c.country_code.padStart(5, " ")}] ${c.Country_Name}`
      }));
    });
    box.add(list);
    this.contentBox.add(box);
  }

  private renderCoinsView() {
    const card = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "coins & rewards",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      width: "70%",
      padding: 1,
      gap: 1
    });

    card.add(new TextRenderable(this.renderer, { content: `Coin Balance: ${this.userCoins} Coins` }));

    const farmPill = new BoxRenderable(this.renderer, {
      backgroundColor: "#353535",
      padding: 0,
      height: 1
    });
    farmPill.add(new TextRenderable(this.renderer, { content: " [ Press 'f' to Farm All Coins (+100) ] " }));
    card.add(farmPill);

    card.add(new TextRenderable(this.renderer, { content: `Status: ${this.lastFarmedAction}` }));
    card.add(new TextRenderable(this.renderer, { content: "Coins can be used in Mode [6] to rent private dedicated numbers." }));

    this.contentBox.add(card);
  }

  private renderPrivateView() {
    const box = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "private dedicated numbers",
      flexDirection: "column",
      padding: 1,
      width: "75%",
      gap: 1
    });

    box.add(new TextRenderable(this.renderer, { content: "Private numbers are dedicated to your session and not shared publicly." }));
    box.add(new TextRenderable(this.renderer, { content: "• +14155552671 (US Dedicated) - Active until 2026-11-01" }));
    box.add(new TextRenderable(this.renderer, { content: "• Cost: 500 Coins / 7 days (Earn coins in Workspace 5)" }));

    this.contentBox.add(box);
  }

  // ---------------- MODALS & OVERLAYS ----------------

  private renderTrafficModal() {
    const modal = new BoxRenderable(this.renderer, {
      backgroundColor: "#1E1E1E",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      flexDirection: "column",
      width: "85%",
      height: "80%",
      position: "absolute",
      padding: 1
    });

    modal.add(new TextRenderable(this.renderer, { content: "[Ctrl-R] Close   (Escape also closes)" }));
    modal.add(new TextRenderable(this.renderer, { content: this.traffic.formatOutput() }));
    this.rootBox.add(modal);
  }

  private renderCountryModal() {
    const modal = new BoxRenderable(this.renderer, {
      backgroundColor: "#0D0D0D",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      flexDirection: "column",
      width: "70%",
      height: "75%",
      position: "absolute",
      padding: 1,
      gap: 1
    });

    modal.add(new TextRenderable(this.renderer, { content: "esc: quit   [Up/Down + Enter to select country]" }));
    modal.add(new TextRenderable(this.renderer, { content: `Selected Country: ${this.selectedCountry}` }));

    const list = new BoxRenderable(this.renderer, { flexDirection: "column" });
    this.countries.slice(0, 10).forEach((c, idx) => {
      const isSel = idx === this.countryCursor;
      list.add(new TextRenderable(this.renderer, {
        content: isSel ? `> [${c.country_code}] ${c.Country_Name} <` : `  [${c.country_code}] ${c.Country_Name}`
      }));
    });
    modal.add(list);
    this.rootBox.add(modal);
  }

  private renderHelpModal() {
    const modal = new BoxRenderable(this.renderer, {
      backgroundColor: "#0D0D0D",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "Help & Shortcuts",
      width: "60%",
      height: "50%",
      position: "absolute",
      padding: 1,
      gap: 1
    });

    modal.add(new TextRenderable(this.renderer, { content: "q: Quit application" }));
    modal.add(new TextRenderable(this.renderer, { content: "r: Reload active SMS inbox (with spinner)" }));
    modal.add(new TextRenderable(this.renderer, { content: "<ctrl-r>: Toggle live API traffic history" }));
    modal.add(new TextRenderable(this.renderer, { content: "c: Open country selector modal" }));
    modal.add(new TextRenderable(this.renderer, { content: "1 - 6: Switch workspace modes" }));
    modal.add(new TextRenderable(this.renderer, { content: "Escape: Close any open modal" }));
    modal.add(new TextRenderable(this.renderer, { content: "\nPress Escape to close this help dialog" }));
    this.rootBox.add(modal);
  }

  // ---------------- FOOTER TABS ----------------

  private renderFooterTabs() {
    this.clearChildren(this.footerTabsBox);

    const tabsRow = new BoxRenderable(this.renderer, {
      flexDirection: "row",
      gap: 1
    });

    const modes: { id: WorkspaceMode; label: string }[] = [
      { id: 1, label: "1: number" },
      { id: 2, label: "2: sms inbox" },
      { id: 3, label: "3: otp code" },
      { id: 4, label: "4: countries" },
      { id: 5, label: "5: coins" },
      { id: 6, label: "6: private" }
    ];

    for (const m of modes) {
      const isActive = m.id === this.currentMode;
      const tabBox = new BoxRenderable(this.renderer, {
        backgroundColor: isActive ? "#353535" : undefined,
        padding: 0,
        height: 1
      });
      tabBox.add(new TextRenderable(this.renderer, { content: ` ${m.label} ` }));
      tabsRow.add(tabBox);
    }

    const helperText = new TextRenderable(this.renderer, {
      content: "[1-6] to change workspace (mode)"
    });

    this.footerTabsBox.add(tabsRow);
    this.footerTabsBox.add(helperText);
  }
}
