#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

::Kernel.require('English')
::Kernel.require('Pathname')

::Pathname.pwd.ascend.each do
  gem = _1 / 'Gemfile'
  if gem.exist?
    Dir.chdir(_1)
    ::Kernel.exec(*%w[bundle exec -- rubocop], *$ARGV)
  end
end

cop = ::File.join(__dir__, *%w[.. modules rb_modules bin rubocop])
::Kernel.exec(cop, *$ARGV)
