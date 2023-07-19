#!/usr/bin/env -S -- Rscript

if (Sys.getenv("Rscript") != "Rscript") {
  argv <- commandArgs()
  location <- argv[4]
  if (!startsWith(location, "--file=")) {
    stop()
  }

  arg0 <- sub("^--file=", "", location)
  libs <- Sys.getenv("R_LIBS_SITE")
  parent <- dirname(dirname(arg0))
  lib <- paste(getwd(), parent, "lib", "R", sep = "/")
  libs <- paste(libs, lib, sep = ":")

  env <- c(paste("R_LIBS_SITE", libs, sep = "="), "Rscript=Rscript")
  system2(arg0, commandArgs(trailingOnly = TRUE), env = env)
} else {
  styler::style_file(commandArgs(trailingOnly = TRUE))
}
