#!/usr/bin/env -S -- ruby
# frozen_string_literal: true
# typed: strong

require('fileutils')
require('open3')
require('pathname')

prefix = 'https://github.com/facebook/watchman/releases/download/'
tmp, dst = ENV.fetch('TMP'), ENV.fetch('BIN')
bin = Pathname(dst).parent

postfix =
  case [RUBY_PLATFORM, RUBY_PLATFORM]
  in [/linux/, /x86_64/]
    'v2025.03.24.00/watchman-v2025.03.24.00-linux.zip'
  in [/darwin/, _]
    exit
  else
    'v2025.02.24.00/watchman-v2025.02.24.00-windows.zip'
  end

uri = prefix + postfix
stats = Open3.pipeline(['env', '--', 'get.sh', uri], ['env', '--', 'unpack.sh', tmp])

raise unless stats.all?(&:success?)

Pathname.glob("#{tmp}/*/bin/*").each do
  FileUtils.mv(_1, bin / _1.basename, verbose: true)
end
