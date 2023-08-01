#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar
//usr/bin/true && rustc --edition=2021 -o "${TMPFILE:="$(mktemp)"}" -- "$0" && "$TMPFILE" "$0" "$@" && exec -- rm -v -fr -- "$TMPFILE"

#![deny(clippy::all, clippy::cargo, clippy::pedantic)]

use std::{
    env::{args, consts::ARCH, var_os},
    error::Error,
    fs::{create_dir_all, read_dir, rename},
    path::PathBuf,
    process::{Command, Stdio},
};

fn main() -> Result<(), Box<dyn Error>> {
    let mut argv = args();
    argv.next();
    let arg0 = argv.next().ok_or(format!("{}", line!()))?;
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

    let mut proc = Command::new("get.py")
        .arg("--")
        .arg(uri)
        .stdout(Stdio::piped())
        .spawn()?;
    let status = Command::new("unpack.py")
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
            }

            rename(entry.path(), var_os("BIN").ok_or(format!("{}", line!()))?)?;
            return Ok(());
        }
    }

    Err(format!("{}", line!()).into())
}
