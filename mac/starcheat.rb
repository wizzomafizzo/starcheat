require 'formula'

class Starcheat < Formula
  homepage 'https://github.com/wizzomafizzo/starcheat'
  url 'https://github.com/wizzomafizzo/starcheat.git'
  version 'beta'

  depends_on 'python3'
  depends_on 'https://raw.github.com/wizzomafizzo/starcheat/master/mac/pyqt5.rb'
  depends_on :hg

  option 'without-app', 'Build without the .app (started via starcheat terminal command)'
  option 'with-dist', 'Creates an tar.gz archive for distributing.'
  option 'without-binary', 'Only builds the .app, no binary install to your prefix'

  resource 'setup.py' do
    url 'https://raw.github.com/wizzomafizzo/starcheat/master/mac/setup.py'
    sha1 'eb0f1f8a99917ab447d9fc39496469b58b07632c'
    version '0.1'
  end

  resource 'altgraph' do
    url 'https://bitbucket.org/ronaldoussoren/altgraph/get/936269ccbcf3.tar.gz'
    sha1 '1996ee5236f2fe04f8b4b865b03fd7affe8099fa'
    version '0.11pre'
  end

  resource 'modulegraph' do
    url 'https://bitbucket.org/ronaldoussoren/modulegraph/get/eb77ef360f1b.tar.gz'
    sha1 'f5147f3d472aeb5cc42983a412d9ac75b12c3441'
    version '0.11pre'
  end

  resource 'py2app' do
    url 'https://bitbucket.org/ronaldoussoren/py2app/get/ef8f2b136d79.tar.gz'
    sha1 '74f5d877891892daf74c35ba98f013dcb7d64753'
    version '0.8pre'
  end

  skip_clean 'StarCheat.app' if build.with? 'app'

  def install
    system './build.sh'

    cd 'build' do
      # install py2app (with dependencies modulegraph and altgraph) HEAD
      system 'pip3', 'install', '--upgrade', 'setuptools'
      resource('altgraph').stage do
        system 'python3.3', 'setup.py', 'install'
      end
      resource('modulegraph').stage do
        system 'python3.3', 'setup.py', 'install'
      end
      resource('py2app').stage do
        system 'python3.3', 'setup.py', 'install'
      end

      (buildpath/'build').install resource('setup.py')
      # give write access to Qt's frameworks (fixes py2app permission errors)
      system 'chmod', '-R', 'u+w', Formula.factory('qt5').lib

      system 'python3.3', 'setup.py', 'py2app'
      # convert dynamic links into static links and adds qt5 plugins (cocoa...)
      system "#{Formula.factory('qt5').bin}/macdeployqt", 'dist/starcheat.app', '-verbose=2'
      cp_r 'dist/starcheat.app', prefix/'StarCheat.app'
      rm_rf ['build', 'dist', 'setup.py']

      cd prefix do
        # Creates and uploades the archive
        system 'tar', 'czf', 'starcheat.tar.gz', 'StarCheat.app'
        # why using octokit when you habe curl and regex ;-) (creates a new release from the current commit and extracts the upload url from it)
        `curl -H "Authorization: token #{HOMEBREW_GITHUB_API_TOKEN}" -H "Accept: application/json" -d '{"tag_name":"#{ENV['TRAVIS_COMMIT'][0..6]}","target_commitish":"#{ENV['TRAVIS_COMMIT']}","name":"starcheat (#{ENV['TRAVIS_COMMIT'][0..6]})","prerelease":true}' https://api.github.com/repos/chrmoritz/starcheat/releases` =~ /.*"upload_url":\s*"([\w\.\:\/]*){\?name}.*/m
        system 'curl', '-H', "Authorization: token #{HOMEBREW_GITHUB_API_TOKEN}", '-H', 'Accept: application/json',
                       '-H', 'Content-Type: application/gzip', '--data-binary', '@starcheat.tar.gz',
                       "#{$1}?name=starcheat-#{ENV['TRAVIS_COMMIT'][0..6]}.tar.gz"
      end if build.with? 'dist'

    end if build.with? 'app'

    if build.with? 'binary'
      libexec.install Dir['build/*']
      bin.install_symlink libexec+'starcheat.py' => 'starcheat'
    end
  end

  def caveats
    <<-EOS.undent
      You can run this to symlink the StarCheat.app into your Application folder:
        `brew linkapps`
      or just copy it from here for further distributing:
        cd #{prefix}
    EOS
  end
end
