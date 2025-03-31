#!/usr/bin/env -S -- ruby
# frozen_string_literal: true
# typed: strong

require('English')
require('pathname')

$ARGV => [filename, *argv]

parents = Pathname(filename).parent.ascend.to_a

yml = '.rubocop.yml'
conf = parents.map { _1 / yml }.find(-> { File.join(__dir__, *%w[.. ..], yml) }, &:exist?)
argv += ['--config', conf.to_s]

parents.each do
  gem = _1 / 'Gemfile'
  if gem.exist? && gem.read.match?(/rubocop/)
    Dir.chdir(_1)
    exec(*%w[bundle exec -- rubocop], *argv)
  end
end

cop = File.join(__dir__, *%w[.. modules rb_modules bin rubocop])
exec(cop, *argv)
