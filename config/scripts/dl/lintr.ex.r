#!/usr/bin/env -S -- Rscript

errs <- lintr::lint(commandArgs(trailingOnly = TRUE))
code <- length(errs) != 0
quit(status = code)
