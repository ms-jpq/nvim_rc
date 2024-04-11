#!/usr/bin/env -S -- node

import { ok } from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { randomBytes } from "node:crypto"
import { existsSync } from "node:fs"
import { rm, symlink } from "node:fs/promises"
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

const _tmp = async function* (filename = "") {
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
          await rm(tmp, { recursive: true, force: true })
        } finally {
          break
        }
      }
    }
  }
}

const _eslint = (eslint = "", tmp = "") => {
  const { error, status, signal } = spawnSync(
    execPath,
    [eslint, "--exit-on-fatal-error", "--fix", "--", tmp],
    {
      stdio: "inherit",
    },
  )
  if (error) {
    throw error
  } else if (signal) {
    throw signal
  } else if (status && status !== 1) {
    process.exitCode = status
  }
}

const [, , filename, tempname] = argv
ok(tempname)

for (const path of _parents()) {
  const eslint = join(path, "node_modules", ".bin", "eslint")
  if (existsSync(eslint)) {
    for await (const tmp of _tmp(filename)) {
      await symlink(tempname, tmp, "file")
      _eslint(eslint, tmp)
    }
    break
  }
}
