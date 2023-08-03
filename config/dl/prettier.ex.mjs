#!/usr/bin/env -S -- node

import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { argv, exit } from "node:process";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
const node_modules = join(dirname(dir), "modules", "node_modules");
const bin = join(node_modules, ".bin", "prettier");

const [, , filetype, filename, tabsize] = argv;

const plugins = (function* () {
  if (filetype === "xml") {
    yield join("@prettier", "plugin-xml");
  }
  if (filetype.match(/^(html|((java|type)scriptreact))$/)) {
    yield join("prettier-plugin-tailwindcss", "dist", "index.js");
  }
  if (filetype.match(/^(java|type)script/)) {
    yield join("prettier-plugin-organize-imports", "index.js");
  }
})();

const args = (function* () {
  yield `--stdin-filepath=${filename}`;
  yield `--tab-width=${tabsize}`;
  for (const plugin of plugins) {
    yield `--plugin=${join(node_modules, plugin)}`;
  }
})();

const { error, status, signal } = spawnSync(bin, [...args], {
  stdio: "inherit",
});

if (error) {
  throw error;
} else {
  exit(status ?? -(signal ?? -1));
}
