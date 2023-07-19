#!/usr/bin/env -S -- Rscript

if (!Sys.getenv("R_LIBS")) {
  argv <- commandArgs()
  location <- argv[4]
  if (!startsWith(location, "--file=")) {
    stop()
  }

  parent <- dirname(dirname(sub("^--file=", "", location)))
  lib <- paste(parent, "lib", "R", sep = "/")
  Sys.setenv(R_LIBS = lib)
  system2(argv[1], argv[-1])
} else {
  library(styler, lib.loc = c(lib))
  styler::style_file(commandArgs(trailingOnly = TRUE))
}
