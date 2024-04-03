#!/usr/bin/env -S -- bash -Eeuo pipefail
// || rustc --edition=2021 -o "${T:="$(mktemp)"}" -- "$0" && exec -a "$0" -- "$T" "$0" "$@"

#![deny(clippy::all, clippy::cargo, clippy::pedantic)]

use std::{
  backtrace::Backtrace,
  env::{args_os, consts::ARCH, var_os},
  error::Error,
  fs::{create_dir_all, read_dir, rename},
  path::{Path, PathBuf},
  process::{Command, Stdio},
};

fn main() -> Result<(), Box<dyn Error>> {
  let uri = {
    let base = "https://github.com/rust-lang/rust-analyzer/releases/latest/download/rust-analyzer";
    #[cfg(target_os = "macos")]
    {
      format!("{base}-{ARCH}-apple-darwin.gz")
    }
    #[cfg(target_os = "linux")]
    {
      format!("{base}-{ARCH}-unknown-linux-gnu.gz")
    }
    #[cfg(target_os = "windows")]
    {
      format!("{base}-{ARCH}-pc-windows-msvc.gz")
    }
  };

  let tmp = args_os()
    .next()
    .map(PathBuf::from)
    .ok_or_else(|| format!("{}", Backtrace::capture()))?
    .parent()
    .and_then(Path::parent)
    .and_then(Path::parent)
    .and_then(Path::parent)
    .ok_or_else(|| format!("{}", Backtrace::capture()))?
    .join("var")
    .join("tmp")
    .join("rust-analyzer-dl");
  let libexec = var_os("LIBEXEC")
    .map(PathBuf::from)
    .ok_or_else(|| format!("{}", Backtrace::capture()))?;
  let bin = var_os("BIN").ok_or_else(|| format!("{}", Backtrace::capture()))?;

  create_dir_all(&tmp)?;
  let mut proc = Command::new("env")
    .arg("--")
    .arg(libexec.join("get.sh"))
    .arg(uri)
    .stdout(Stdio::piped())
    .spawn()?;
  let stdin = proc
    .stdout
    .take()
    .ok_or_else(|| format!("{}", Backtrace::capture()))?;
  let status = Command::new("env")
    .arg("--")
    .arg(libexec.join("unpack.sh"))
    .arg(&tmp)
    .stdin(stdin)
    .status()?;

  assert!(proc.wait()?.success());
  assert!(status.success());

  for entry in read_dir(&tmp)? {
    let entry = entry?;
    if entry
      .file_name()
      .into_string()
      .map_err(|p| format!("{p:?}"))?
      .starts_with("rust-analyzer-")
    {
      #[cfg(target_family = "unix")]
      {
        use std::{
          fs::{set_permissions, Permissions},
          os::unix::fs::PermissionsExt,
        };
        set_permissions(entry.path(), Permissions::from_mode(0o755))?;
        rename(entry.path(), bin)?;
      }

      #[cfg(target_os = "windows")]
      {
        return Ok(());
      }

      return Ok(());
    }
  }

  Err(format!("{}", line!()).into())
}
