#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

require('fileutils')
require('open3')

repo = 'fables-tales/rubyfmt'
tmp, dst = ENV.fetch('TMP'), ENV.fetch('BIN')
version, stat = Open3.capture2(*%w[env -- gh-latest.sh .], repo)
raise unless stat.success?

os, arch =
  case RUBY_PLATFORM
  in /linux/
    arch = case RUBY_PLATFORM
           in /x86_64/
             'x86_64'
           else
             'aarch64'
           end
    ['Linux', arch]
  in /darwin/
    %w[Darwin arm64]
  else
    exit
  end

uri = "https://github.com/#{repo}/releases/latest/download/rubyfmt-#{version.chomp}-#{os}-#{arch}.tar.gz"
src = File.join(tmp, 'tmp', 'releases', "#{version}-#{os}", 'rubyfmt')
stats = Open3.pipeline(['env', '--', 'get.sh', uri], ['env', '--', 'unpack.sh', tmp])

raise unless stats.all?(&:success?)

FileUtils.rm(dst, force: true, verbose: true)
FileUtils.mv(src, dst, verbose: true)
