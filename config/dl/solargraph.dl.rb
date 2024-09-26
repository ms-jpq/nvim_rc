#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

require('fileutils')

FileUtils.cp(File.join(__dir__, 'solargraph.ex.rb'), ENV.fetch('BIN'))
