#!/usr/bin/env -S -- Rscript

argv <- commandArgs()
location <- argv[4]
if (!startsWith(location, "--file=")) {
  stop()
}

parent <- dirname(sub("^--file=", "", location))
r <- paste(parent, "/lintr.ex.r", sep = "")

bin <- {
  bin <- Sys.getenv("BIN")
  if (.Platform$OS.type == "windows") paste(bin, ".r", sep = "") else bin
}

file.copy(r, bin, overwrite = TRUE)
