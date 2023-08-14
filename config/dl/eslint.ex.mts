#!/usr/bin/env -S -- node

import { spawnSync } from "node:child_process";
import { randomBytes } from "node:crypto";
import { copyFileSync, existsSync, openSync, rmSync } from "node:fs";
import { basename, dirname, extname, join } from "node:path";
import { argv, cwd, execPath } from "node:process";

const _parents = function* (path = cwd()) {
  const parent = dirname(path);
  yield path;
  if (parent !== path) {
    yield* _parents(parent);
  }
};

const _tmp = function* (filename = "") {
  const ext = extname(filename);
  const base = basename(filename, ext);

  while (true) {
    const name = `${base}.${randomBytes(16).toString("hex")}${ext}`;
    const tmp = join(dirname(filename), name);
    if (!existsSync(tmp)) {
      try {
        yield tmp;
      } finally {
        try {
          rmSync(tmp, { recursive: true, force: true });
        } finally {
          break;
        }
      }
    }
  }
};

for (const path of _parents()) {
  const eslint = join(path, "node_modules", ".bin", "eslint");
  if (existsSync(eslint)) {
    const [, , filename, tempname] = argv;
    for (const tmp of _tmp(filename)) {
      copyFileSync(tempname, tmp);
      const fd = openSync(tmp, "r");

      const { error, status, signal } = spawnSync(
        execPath,
        [eslint, "--exit-on-fatal-error", "--fix", "--", tmp],
        {
          stdio: [fd, "inherit", "inherit"],
        },
      );
      if (error) {
        throw error;
      } else {
        process.exitCode = status ?? -(signal ?? -1);
        if (!process.exitCode) {
          copyFileSync(tmp, tempname);
        }
        break;
      }
    }
  }
}
