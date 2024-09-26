#!/usr/bin/env -S -- ruby
# frozen_string_literal: true

require('fileutils')

FileUtils.cp(File.join(__dir__, 'rubocop.ex.rb'), ENV.fetch('BIN'))
