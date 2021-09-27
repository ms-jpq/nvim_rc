#!/usr/bin/env Rscript

code <- length(lintr::lint(commandArgs(trailingOnly = TRUE)))
quit(save = "no", status = code)
