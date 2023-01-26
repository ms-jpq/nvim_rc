#!/usr/bin/env -S -- Rscript

apt <- Sys.which("apt-get")
if (apt != "") {
  system2(apt, c(
    "install",
    "--yes",
    "--",
    "libcurl4-openssl-dev",
    "libssl-dev",
    "libxml2-dev"
  ), env = c("DEBIAN_FRONTEND=noninteractive"))
}

repos <- c("https://cloud.r-project.org")
pkgs <- c("languageserver", "httpgd")

for (pkg in pkgs) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(c(pkg), repos = repos)
  } else {
    update.packages(oldPkgs = c(pkg), repos = repos)
  }
  library(pkg, character.only = TRUE)
}
