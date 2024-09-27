#!/usr/bin/env -S -- node

import { ok } from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { dirname, join } from "node:path"
import { execPath } from "node:process"
import { fileURLToPath } from "node:url"
import { parseArgs } from "node:util"

const {
  values: { filename, filetype, sort, tabsize },
  positionals,
} = parseArgs({
  options: {
    filename: { type: "string" },
    filetype: { type: "string" },
    sort: { type: "boolean" },
    tabsize: { type: "string" },
  },
})
ok(filename)
ok(filetype)
ok(tabsize)

const node_modules = join(
  dirname(dirname(fileURLToPath(import.meta.url))),
  "modules",
  "node_modules",
)
const bin = join(node_modules, ".bin", "prettier")

const plugins = {
  [join("@prettier", "plugin-php", "standalone.js")]: /^php$/,
  [join("@prettier", "plugin-xml", "src", "plugin.js")]: /^xml$/,
  [join("prettier-plugin-awk", "out", "index.js")]: /^awk$/,
  [join("prettier-plugin-nginx", "dist", "index.js")]: /^nginx$/,
  [join("prettier-plugin-tailwindcss", "dist", "index.mjs")]:
    /^(html|((java|type)scriptreact))$/,
}

if (sort) {
  plugins[join("prettier-plugin-organize-imports", "index.js")] =
    /^(java|type)script/
}

const argv = (function* () {
  yield `--stdin-filepath=${filename}`
  yield `--tab-width=${tabsize}`
  for (const [plugin, re] of Object.entries(plugins)) {
    if (filetype.match(re)) {
      yield `--plugin=${join(node_modules, plugin)}`
    }
  }
})()

const { error, status, signal } = spawnSync(
  execPath,
  [bin, ...argv, ...positionals],
  {
    stdio: "inherit",
  },
)

if (error) {
  throw error
} else if (signal) {
  throw signal
} else {
  process.exitCode = status ?? undefined
}
