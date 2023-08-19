#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

Kernel.require("English")
Kernel.require("Pathname")

$ARGV => [filename, *argv]

Kernel
  .Pathname(filename)
  .parent
  .ascend
  .each do
    gem = _1 / "Gemfile"
    if gem.exist?
      Dir.chdir(_1)
      Kernel.exec(*%w[bundle exec -- rubocop], *argv)
    end
  end

cop = File.join(__dir__, *%w[.. modules rb_modules bin rubocop])
Kernel.exec(cop, *argv)
