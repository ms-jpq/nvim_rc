#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

Kernel.require("English")

ENV["SOLARGRAPH_CACHE"] = File.join(ENV.fetch("XDG_CACHE_HOME"), "solargraph")
Kernel.exec(
  File.join(__dir__, "..", "modules", "rb_modules", "bin", "solargraph"),
  *$ARGV,
)
