#!/usr/bin/env -S -- node

import { ok } from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { dirname, join } from "node:path"
import { argv, execPath } from "node:process"
import { fileURLToPath } from "node:url"

const node_modules = join(
  dirname(dirname(fileURLToPath(import.meta.url))),
  "modules",
  "node_modules",
)
const bin = join(node_modules, ".bin", "prettier")

const [, , filetype, filename, tabsize] = argv
ok(filetype)

const plugins = {
  [join("@prettier", "plugin-php", "src", "index.js")]: /^php$/,
  [join("@prettier", "plugin-xml", "src", "plugin.js")]: /^xml$/,
  [join("prettier-plugin-awk")]: /^awk$/,
  [join("prettier-plugin-nginx", "dist", "index.js")]: /^nginx$/,
  [join("prettier-plugin-organize-imports", "index.js")]: /^(java|type)script/,
  [join("prettier-plugin-tailwindcss", "dist", "index.mjs")]:
    /^(html|((java|type)scriptreact))$/,
}

const args = (function* () {
  yield `--stdin-filepath=${filename}`
  yield `--tab-width=${tabsize}`
  for (const [plugin, re] of Object.entries(plugins)) {
    if (filetype.match(re)) {
      yield `--plugin=${join(node_modules, plugin)}`
    }
  }
  yield "--"
})()

const { error, status, signal } = spawnSync(execPath, [bin, ...args], {
  stdio: "inherit",
})

if (error) {
  throw error
} else if (signal) {
  throw signal
} else {
  process.exitCode = status ?? undefined
}
