#!/usr/bin/env -S -- node

import { copyFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { env } from "node:process";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
const run = join(dir, "eslint.ex.mts");
await copyFile(run, env.BIN);
