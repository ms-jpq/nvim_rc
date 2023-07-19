#!/usr/bin/env -S -- Rscript

argv <- commandArgs()
location <- argv[4]
if (!startsWith(location, "--file=")) {
  stop()
}

parent <- dirname(sub("^--file=", "", location))
r <- paste(parent, "serverr.ex.r", sep = "/")
lib <- Sys.getenv("LIB")
bin <- Sys.getenv("BIN")

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
pkgs <- c("ps", "languageserver")

dir.create(lib, recursive = TRUE)

for (pkg in pkgs) {
  if (!require(pkg, lib.loc = c(lib), character.only = TRUE)) {
    install.packages(c(pkg), lib = c(lib), repos = repos)
  } else {
    update.packages(c(lib), oldPkgs = c(pkg), repos = repos)
  }
  library(pkg, lib.loc = c(lib), character.only = TRUE)
}

file.copy(r, bin, overwrite = TRUE)
