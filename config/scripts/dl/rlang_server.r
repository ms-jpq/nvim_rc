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
  ))
}

if (!require(languageserver)) {
  install.packages("languageserver")
  library(languageserver)
}
