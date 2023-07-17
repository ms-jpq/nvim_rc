#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

Kernel.require("English")
Kernel.require("fileutils")
Kernel.require("pathname")

FileUtils.cp(Pathname(__dir__).join("solargraph.ex.rb"), ENV.fetch("BIN"))
