#!/usr/bin/env bun
import { TempNumberApp } from "./src/app";

const app = new TempNumberApp();
try {
  await app.start();
  await app.waitForExit();
} catch (err) {
  console.error("Fatal error:", err);
  process.exit(1);
}
