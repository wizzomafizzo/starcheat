#!/usr/bin/env ruby

require 'fileutils'

def system cmd, *args
  print "==> ", cmd, " ", *args.join(' '), "\n"
  raise "error" unless Kernel.system cmd, *args
end

system 'python3', 'build.py', '-v'
FileUtils.cd 'build'
system './starcheat.py', '-v' 
# run some other unit test here
unless ENV['TRAVIS_BUILD_ID'].nil? || ENV['TRAVIS_SECURE_ENV_VARS'] == 'false'
  FileUtils.mv '../mac/setup.py', '.'
  system 'python3', 'setup.py', 'py2app'
  system '/usr/local/opt/qt5/bin/macdeployqt', 'dist/starcheat.app', '-verbose=2'
  FileUtils.mv 'dist/starcheat.app', 'StarCheat.app'
  system 'StarCheat.app/Contents/MacOS/starcheat', '-v'
  system 'tar', 'czf', 'starcheat.tar.gz', 'StarCheat.app'
  puts '==> Uploading'
  `curl -H "Authorization: token #{ENV['HOMEBREW_GITHUB_API_TOKEN']}" -H "Accept: application/json" -d '{"tag_name":"#{ENV['TRAVIS_COMMIT'][0..6]}","target_commitish":"#{ENV['TRAVIS_COMMIT']}","name":"starcheat (#{ENV['TRAVIS_COMMIT'][0..6]})","prerelease":true}' https://api.github.com/repos/wizzomafizzo/starcheat/releases` =~ /.*"upload_url":\s*"([\w\.\:\/]*){\?name}.*/m
  `curl -H "Authorization: token #{ENV['HOMEBREW_GITHUB_API_TOKEN']}" -H "Accept: application/json" -H "Content-Type: application/gzip" --data-binary @starcheat.tar.gz #{$1}?name=starcheat-#{ENV['TRAVIS_COMMIT'][0..6]}.tar.gz` unless $1.nil?
  raise "Skipping uploading build because tag is already in use" if $1.nil?
end
