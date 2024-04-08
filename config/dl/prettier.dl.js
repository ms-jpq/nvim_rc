#!/usr/bin/env -S -- node

import { ok } from "node:assert/strict"
import { copyFile } from "node:fs/promises"
import { dirname, join } from "node:path"
import { env } from "node:process"
import { fileURLToPath } from "node:url"

ok(env.BIN)
const dir = dirname(fileURLToPath(import.meta.url))
const run = join(dir, "prettier.ex.js")
await copyFile(run, env.BIN)
