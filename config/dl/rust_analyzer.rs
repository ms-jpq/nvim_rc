#!/usr/bin/env -S -- bash -Eeuo pipefail
// || rustc --edition=2021 -o "${T:="$(mktemp)"}" -- "$0" && exec -a "$0" -- "$T" "$0" "$@"

#![deny(clippy::all, clippy::cargo, clippy::pedantic)]

use std::{
  backtrace::Backtrace,
  env::{args_os, consts::ARCH, var_os},
  error::Error,
  fs::{copy, create_dir_all, read_dir, remove_dir_all, rename},
  io::ErrorKind,
  path::{Path, PathBuf},
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

  let tmp = args_os()
    .next()
    .map(PathBuf::from)
    .ok_or_else(|| format!("{}", Backtrace::capture()))?
    .parent()
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
  #[cfg(target_family = "windows")]
  let bin = {
    let mut bin = PathBuf::from(bin);
    bin.set_extension("exe");
    bin
  };

  create_dir_all(&tmp)?;
  let output = Command::new("env")
    .arg("--")
    .arg(libexec.join("get.sh"))
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
    .arg(libexec.join("unpack.sh"))
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

      if let Err(e) = rename(&path, &bin) {
        // TODO: ErrorKind::CrossesDevices
        // if e.kind() != ErrorKind::CrossesDevices {
        //   return Err(e.into());
        // }
        copy(path, bin)?;
      }

      return Ok(());
    }
  }

  remove_dir_all(tmp)?;
  Err(format!("{}", line!()).into())
}
