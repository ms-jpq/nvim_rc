#!/usr/bin/env Rscript

apt <- Sys.which("apt")
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
pkgs <- c("languageserver")

if (!require(languageserver)) {
  install.packages(pkgs, repos = repos)
} else {
  update.packages(oldPkgs = pkgs, repos = repos)
}

library(languageserver)
