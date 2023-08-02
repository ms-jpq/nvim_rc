#!/usr/bin/env -S -- node

import { argv, exit } from "node:process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const dir = dirname(fileURLToPath(import.meta.url));
const bin = join(dirname(dir), "modules", "node_modules", ".bin", "prettier");
const [, , ...args] = argv;

// - --plugin=@prettier/plugin-xml
// - --plugin=prettier-plugin-tailwindcss
// - --plugin=prettier-plugin-organize-imports

const { error, status, signal } = spawnSync(bin, args, { stdio: "inherit" });
if (error) {
  throw error;
} else {
  exit(status ?? -(signal ?? -1));
}
