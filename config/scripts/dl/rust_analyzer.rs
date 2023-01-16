#!/usr/bin/env -S bash
//usr/bin/true; set -Eeuo pipefail; rustc --edition=2021 -o "${TMPFILE:="$(mktemp)"}" -- "$0"; exec -- "$TMPFILE" "$@"

#![deny(clippy::all, clippy::cargo, clippy::pedantic)]

use std::{
    env::{temp_dir, var_os},
    error::Error,
    fs::{create_dir_all, read_dir, rename},
    process::{Command, Stdio},
};

fn main() -> Result<(), Box<dyn Error>> {
    let tmp = temp_dir().join("rust-analyzer-dl");
    create_dir_all(&tmp)?;

    #[cfg(target_os = "macos")]
    let var = "DARWIN_URI";
    #[cfg(target_os = "linux")]
    let var = "LINUX_URI";
    #[cfg(target_os = "windows")]
    let var = "NT_URI";

    let uri = var_os(var).ok_or(format!("{}", line!()))?;

    let mut proc = Command::new("get")
        .arg("--")
        .arg(uri)
        .stdout(Stdio::piped())
        .spawn()?;
    let status = Command::new("unpack")
        .arg("--dest")
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
                use std::os::unix::fs::PermissionsExt;
                entry.metadata()?.permissions().set_mode(0o755);
            }

            rename(entry.path(), var_os("BIN").ok_or(format!("{}", line!()))?)?;
            return Ok(());
        }
    }

    Err(format!("{}", line!()).into())
}
