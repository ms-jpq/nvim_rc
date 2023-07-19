#!/usr/bin/env -S -- Rscript

apt <- Sys.which("apt-get")
if (apt != "") {
  system2("sudo", c(
    "--",
    apt,
    "install",
    "--no-install-recommends",
    "--yes",
    "--",
    "libcurl4-openssl-dev",
    "libssl-dev",
    "libxml2-dev"
  ), env = c("DEBIAN_FRONTEND=noninteractive"))
}

repos <- c("https://cloud.r-project.org")
pkgs <- c("languageserver", "httpgd")

lib <- Sys.getenv("LIB")
dir.create(lib, recursive = TRUE)

for (pkg in pkgs) {
  if (!require(pkg, lib.loc = c(lib), character.only = TRUE)) {
    install.packages(c(pkg), lib = c(lib), repos = repos)
  } else {
    update.packages(c(lib), oldPkgs = c(pkg), repos = repos)
  }
  library(pkg, lib.loc = c(lib), character.only = TRUE)
}
