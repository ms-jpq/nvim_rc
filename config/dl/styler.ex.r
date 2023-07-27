#!/usr/bin/env -S -- Rscript

{
  argv <- commandArgs()
  location <- argv[4]
  if (!startsWith(location, "--file=")) {
    stop()
  }
  arg0 <- sub("^--file=", "", location)
  parent <- dirname(dirname(arg0))
  lib <- paste(parent, "lib", "lsr", sep = "/")
  .libPaths(c(.libPaths(), lib))
}

styler::style_file(commandArgs(trailingOnly = TRUE))
