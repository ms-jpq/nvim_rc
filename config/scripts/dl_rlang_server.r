#!/usr/bin/env Rscript

if (Sys.which("apt") != "") {
  system2("apt", c(
    "install", "--yes", "--",
    "libcurl4-openssl-dev",
    "libssl-dev",
    "libxml2-dev"
  ))
}

if (!require(languageserver)) {
  install.packages("languageserver")
  library(languageserver)
}
