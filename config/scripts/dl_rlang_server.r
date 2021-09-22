#!/usr/bin/env Rscript

if (!require(languageserver)) {
  install.packages("languageserver")
  library(languageserver)
}
