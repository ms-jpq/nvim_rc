#!/usr/bin/env -S -- Rscript

argv <- commandArgs()
location <- argv[4]
if (!startsWith(location, "--file=")) {
  stop()
}

parent <- dirname(dirname(sub("^--file=", "", location)))
lib <- paste(parent, "lib", "R", sep = "/")


library(lintr, lib.loc = c(lib))
errs <- lintr::lint(commandArgs(trailingOnly = TRUE))
code <- length(errs) != 0
quit(status = code)
