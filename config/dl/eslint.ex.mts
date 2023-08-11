#!/usr/bin/env -S -- node

import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { argv, cwd, execPath, exit, stdin, stdout } from "node:process";

const _parents = function* (path = cwd()) {
  const parent = dirname(path);
  yield path;
  if (parent !== path) {
    yield* _parents(parent);
  }
};

for (const path of _parents()) {
  const eslint = join(path, "node_modules", ".bin", "eslint");
  if (existsSync(eslint)) {
    const [, , filename, tempname] = argv;
    const { error, status, signal } = spawnSync(
      execPath,
      [
        eslint,
        "--exit-on-fatal-error",
        "--stdin-filename",
        filename,
        "--fix",
        "--",
        tempname,
      ],
      {
        stdio: "inherit",
      },
    );
    if (error) {
      throw error;
    } else {
      exit(status ?? -(signal ?? -1));
    }
  }
}

stdin.pipe(stdout);
