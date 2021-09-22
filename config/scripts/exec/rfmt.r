#!/usr/bin/env Rscript

library(styler)

style_file(commandArgs(trailingOnly = TRUE), dry = "off")
