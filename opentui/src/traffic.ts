import type { TrafficCall } from "./types";

export class TrafficHistory {
  private calls: TrafficCall[] = [];
  private counter = 0;

  record(endpoint: string, code: string, desc: string, data: Record<string, any>) {
    this.counter++;
    const now = new Date();
    const timeStr = [
      String(now.getHours()).padStart(2, "0"),
      String(now.getMinutes()).padStart(2, "0"),
      String(now.getSeconds()).padStart(2, "0")
    ].join(":");

    this.calls.unshift({
      id: this.counter,
      time: timeStr,
      endpoint,
      code,
      desc,
      data
    });

    if (this.calls.length > 50) {
      this.calls.pop();
    }
  }

  getCalls(): TrafficCall[] {
    return this.calls;
  }

  formatOutput(): string {
    const lines: string[] = [];
    lines.push(`── API Traffic History (${this.calls.length} calls) ──`);
    for (const c of this.calls) {
      lines.push(
        `#${c.id} [${c.time}] ${c.endpoint} [${c.code}] ${c.desc}\n` +
        JSON.stringify(c.data, null, 2) + "\n"
      );
    }
    return lines.join("\n");
  }
}
