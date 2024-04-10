#!/usr/bin/env -S -- bash -Eeuo pipefail
// || rustc --edition=2021 -o "${T:="$(mktemp)"}" -- "$0" && exec -a "$0" -- "$T" "$0" "$@"

#![deny(clippy::all, clippy::cargo, clippy::pedantic)]

use std::{
  backtrace::Backtrace,
  env::{consts::ARCH, var_os},
  error::Error,
  fs::{read_dir, rename},
  path::PathBuf,
  process::{Command, Stdio},
};

#[cfg(target_family = "unix")]
use std::{
  ffi::OsString,
  fs::{set_permissions, Permissions},
  os::unix::{ffi::OsStringExt, fs::PermissionsExt},
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

  let tmp = var_os("TMP")
    .map(PathBuf::from)
    .ok_or_else(|| format!("{}", Backtrace::capture()))?;

  let bin = var_os("BIN")
    .map(PathBuf::from)
    .ok_or_else(|| format!("{}", Backtrace::capture()))?;

  #[cfg(target_family = "windows")]
  let bin = {
    let mut bin = bin;
    bin.set_extension("exe");
    bin
  };

  let output = Command::new("env")
    .arg("--")
    .arg("get.sh")
    .arg(uri)
    .stdout(Stdio::piped())
    .output()?;
  assert!(output.status.success());

  #[cfg(target_family = "unix")]
  let os_str = OsString::from_vec(output.stdout);
  #[cfg(target_family = "windows")]
  let os_str = String::from_utf8(output.stdout)?;

  let status = Command::new("env")
    .arg("--")
    .arg("unpack.sh")
    .arg(&tmp)
    .arg(os_str)
    .status()?;
  assert!(status.success());

  for entry in read_dir(&tmp)? {
    let entry = entry?;
    if entry
      .file_name()
      .into_string()
      .map_err(|p| format!("{p:?}"))?
      .starts_with("rust-analyzer-")
    {
      let path = entry.path();
      #[cfg(target_family = "unix")]
      set_permissions(&path, Permissions::from_mode(0o755))?;

      rename(&path, &bin)?;
      return Ok(());
    }
  }

  Err(format!("{}", line!()).into())
}
