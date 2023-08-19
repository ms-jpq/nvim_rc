#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

Kernel.require("English")

ENV["SOLARGRAPH_CACHE"] = File.join(ENV.fetch("XDG_CACHE_HOME"), "solargraph")

bin = File.join(__dir__, *%w[.. modules rb_modules bin solargraph])
Kernel.exec(bin, *$ARGV)
