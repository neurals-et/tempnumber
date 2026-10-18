import { TextRenderable } from "@opentui/core";

export const SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];

export class TerminalSpinner {
  private frameIndex = 0;
  private timer: any = null;
  public renderable: TextRenderable;

  constructor(renderer: any, public label: string = "Refreshing...") {
    this.renderable = new TextRenderable(renderer, {
      content: `${SPINNER_FRAMES[0]} ${label}`
    });
  }

  start() {
    if (this.timer) return;
    this.timer = setInterval(() => {
      this.frameIndex = (this.frameIndex + 1) % SPINNER_FRAMES.length;
      this.renderable.content = `${SPINNER_FRAMES[this.frameIndex]} ${this.label}`;
    }, 80);
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}
