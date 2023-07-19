#!/usr/bin/env -S -- Rscript

{
  argv <- commandArgs()
  location <- argv[4]
  if (!startsWith(location, "--file=")) {
    stop()
  }
  arg0 <- sub("^--file=", "", location)
  parent <- dirname(dirname(arg0))
  lib <- paste(parent, "lib", "serverr", sep = "/")
  .libPaths(c(.libPaths(), lib))
}

errs <- lintr::lint(commandArgs(trailingOnly = TRUE))
code <- length(errs) != 0
quit(status = code)
