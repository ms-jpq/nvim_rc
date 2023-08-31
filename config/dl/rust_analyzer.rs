#!/usr/bin/env -S -- bash -Eeuo pipefail
// || rustc --edition=2021 -o "${T:="$(mktemp)"}" -- "$0" && exec -a "$0" -- "$T" "$0" "$@"

#![deny(clippy::all, clippy::cargo, clippy::pedantic)]

use std::{
  env::{args_os, consts::ARCH, var_os},
  error::Error,
  fs::{create_dir_all, read_dir, rename},
  path::PathBuf,
  process::{Command, Stdio},
};

fn main() -> Result<(), Box<dyn Error>> {
  let arg0 = args_os().next().ok_or(format!("{}", line!()))?;
  let tmp = PathBuf::from(arg0)
    .parent()
    .ok_or(format!("{}", line!()))?
    .parent()
    .ok_or(format!("{}", line!()))?
    .parent()
    .ok_or(format!("{}", line!()))?
    .parent()
    .ok_or(format!("{}", line!()))?
    .join("var")
    .join("tmp")
    .join("rust-analyzer-dl");
  create_dir_all(&tmp)?;

  let base = "https://github.com/rust-lang/rust-analyzer/releases/latest/download/rust-analyzer";

  #[cfg(target_os = "macos")]
  let uri = format!("{base}-{ARCH}-apple-darwin.gz");
  #[cfg(target_os = "linux")]
  let uri = format!("{base}-{ARCH}-unknown-linux-gnu.gz");
  #[cfg(target_os = "windows")]
  let uri = format!("{base}-{ARCH}-pc-windows-msvc.gz");

  let py = var_os("PYTHON").ok_or(format!("{}", line!()))?;
  let libexec = var_os("LIBEXEC")
    .ok_or(format!("{}", line!()))
    .map(PathBuf::from)?;
  let bin = var_os("BIN").ok_or(format!("{}", line!()))?;

  let mut proc = Command::new(&py)
    .arg(libexec.join("get.py"))
    .arg("--")
    .arg(uri)
    .stdout(Stdio::piped())
    .spawn()?;
  let status = Command::new(&py)
    .arg(libexec.join("unpack.py"))
    .arg("--dst")
    .arg(&tmp)
    .stdin(proc.stdout.take().ok_or(format!("{}", line!()))?)
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
