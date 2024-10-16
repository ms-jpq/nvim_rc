#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

require('English')
require('pathname')

$ARGV => [filename, *argv]

Pathname(filename)
  .parent
  .ascend
  .each do
  gem = _1 / 'Gemfile'
  if gem.exist?
    Dir.chdir(_1)
    exec(*%w[bundle exec -- rubocop], *argv)
  end
end

cop = File.join(__dir__, *%w[.. modules rb_modules bin rubocop])
exec(cop, *argv)
