#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

require("optparse")
require("pathname")
require("shellwords")
require("tempfile")

Thread.tap do
  _1.abort_on_exception = true
  _1.report_on_exception = false
end

options, =
  {}.then do |into|
    parsed =
      OptionParser
        .new do
          _1.on("--src SRC", String)
          _1.on("--dst DST", String)
        end
        .parse(ARGV, into:)
    [into, parsed]
  end

options => { src:, dst: }
bins = Pathname(src) / "bin"
dst = Pathname(dst)
gem_path = Shellwords.shellescape(src)

[bins, dst].each(&:mkpath)
bins.each_child(false) do |path|
  bin = dst / path
  next if bin.extname == ".lock"

  stubbed = <<~BASH
  #!/bin/sh

  export -- MSYSTEM='MSYS' GEM_PATH=#{gem_path}
  exec #{Shellwords.shellescape((bins / path).to_s)} "$@"
  BASH

  Tempfile.create do |f|
    f => File
    f.chmod(0o755)
    f.write(stubbed)
    Pathname(f).rename(bin)
  end

  next unless /mswin|mingw|cygwin/ =~ RUBY_PLATFORM

  bin
    .sub_ext(".sh")
    .tap do
      _1.rmtree
      _1.make_symlink(bin)
    end
end
