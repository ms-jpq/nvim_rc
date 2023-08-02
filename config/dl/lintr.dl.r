#!/usr/bin/env -S -- Rscript

argv <- commandArgs()
location <- argv[4]
if (!startsWith(location, "--file=")) {
  stop()
}

parent <- dirname(sub("^--file=", "", location))
r <- paste(parent, "lintr.ex.r", sep = "/")
bin <- Sys.getenv("BIN")

file.copy(r, bin, overwrite = TRUE)
