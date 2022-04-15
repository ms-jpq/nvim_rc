#![deny(clippy::all, clippy::cargo, clippy::nursery, clippy::pedantic)]
#![allow(clippy::cargo_common_metadata)]

use {
    cbindgen::{Builder, Language},
    std::{env::var_os, error::Error, fs::create_dir_all, path::PathBuf},
};

fn main() -> Result<(), Box<dyn Error>> {
    let crate_dir = PathBuf::from(var_os("CARGO_MANIFEST_DIR").ok_or("")?);
    let tmp = crate_dir.join("temp");
    create_dir_all(&tmp)?;

    Builder::new()
        .with_crate(crate_dir)
        .with_language(Language::C)
        .generate()?
        .write_to_file(tmp.join("bindings.h"));

    Ok(())
}
