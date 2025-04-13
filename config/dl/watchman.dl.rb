#!/usr/bin/env -S -- ruby
# frozen_string_literal: true
# typed: strong

require('fileutils')
require('open3')
require('pathname')

tmp, dst = ENV.fetch('TMP'), ENV.fetch('BIN')
bin = Pathname(dst).parent

case [RUBY_PLATFORM, RUBY_PLATFORM]
in [/linux/, /x86_64/]
  argv = %w[sudo -- apt install --no-install-recommends --yes -- watchman]
  system(*argv, exception: true)
in [/darwin/, _]
  exit
else
  exit

  uri = 'https://github.com/facebook/watchman/releases/download/v2025.02.24.00/watchman-v2025.02.24.00-windows.zip'
  stats = Open3.pipeline(['env', '--', 'get.sh', uri], ['env', '--', 'unpack.sh', tmp])

  raise unless stats.all?(&:success?)

  Pathname.glob("#{tmp}/bin/*").each do
    FileUtils.mv(_1, bin / _1.basename, verbose: true)
  end
end
