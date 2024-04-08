#!/usr/bin/env -S -- node

import { ok } from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { randomBytes } from "node:crypto"
import { closeSync, existsSync, openSync, rmSync, symlinkSync } from "node:fs"
import { basename, dirname, extname, join } from "node:path"
import { argv, cwd, execPath } from "node:process"

/**
 * @return {IterableIterator<string>}
 */
const _parents = function* (path = cwd()) {
  const parent = dirname(path)
  yield path
  if (parent !== path) {
    yield* _parents(parent)
  }
}

const _tmp = function* (filename = "") {
  const ext = extname(filename)
  const base = basename(filename, ext)

  while (true) {
    const name = `${base}.${randomBytes(16).toString("hex")}${ext}`
    const tmp = join(dirname(filename), name)
    if (!existsSync(tmp)) {
      try {
        yield tmp
      } finally {
        try {
          rmSync(tmp, { recursive: true, force: true })
        } finally {
          break
        }
      }
    }
  }
}

const _eslint = (eslint = "", filename = "", tempname = "") => {
  for (const tmp of _tmp(filename)) {
    symlinkSync(tempname, tmp, "file")
    const { error, status, signal } = (() => {
      const fd = openSync(tmp, "r")
      try {
        return spawnSync(
          execPath,
          [eslint, "--exit-on-fatal-error", "--fix", "--", tmp],
          {
            stdio: [fd, "inherit", "inherit"],
          },
        )
      } finally {
        closeSync(fd)
      }
    })()

    if (error) {
      throw error
    } else {
      process.exitCode = status ?? -(signal ?? -1)
    }
  }
}

const [, , filename, tempname] = argv
ok(tempname)
for (const path of _parents()) {
  const eslint = join(path, "node_modules", ".bin", "eslint")
  if (existsSync(eslint)) {
    _eslint(eslint, filename, tempname)
    break
  }
}
