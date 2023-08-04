#!/usr/bin/env -S -- Rscript

argv <- commandArgs()
location <- argv[4]
if (!startsWith(location, "--file=")) {
  stop()
}

parent <- dirname(sub("^--file=", "", location))
r <- paste(parent, "lsr.ex.r", sep = "/")
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
} else if (Sys.getenv("CI") != "") {
  quit(status = 0)
}

repos <- c("https://cloud.r-project.org")
pkgs <- c("languageserver")

dir.create(lib, recursive = TRUE)
.libPaths(c(.libPaths(), lib))

if (Sys.getenv("NO_R") != "") {
  quit()
}

if (Sys.getenv("CI") != "" && sample(1:100, 1) >= c(10)) {
  quit()
}

for (pkg in pkgs) {
  if (!require(pkg, lib.loc = c(lib), character.only = TRUE)) {
    install.packages(c(pkg), lib = c(lib), repos = repos)
  } else {
    update.packages(c(lib), oldPkgs = c(pkg), repos = repos)
  }
  library(pkg, lib.loc = c(lib), character.only = TRUE)
}

file.copy(r, bin, overwrite = TRUE)
