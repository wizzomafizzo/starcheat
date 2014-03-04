require 'formula'

class Starcheat < Formula
  homepage 'https://github.com/wizzomafizzo/starcheat'
  url 'https://github.com/wizzomafizzo/starcheat.git', :tag => '0.11'

  head 'https://github.com/wizzomafizzo/starcheat.git', :branch => 'dev'

  depends_on :python3
  depends_on 'pyqt5'

  option 'without-app', 'Build without the .app (started via starcheat terminal command)'
  option 'without-binary', 'Only builds the .app, no binary install to your prefix'

  skip_clean 'StarCheat.app' if build.with? 'app'

  def install
    ENV["PYTHONPATH"] = lib/"python#{/\d\.\d/.match `python3 --version 2>&1`}/site-packages"
    system 'pip3', 'install', '--upgrade', 'setuptools'
    system 'pip3', 'install', 'Pillow'
    system 'python3', 'build.py', '-v'

    cd 'build' do
      system 'pip3', 'install', 'py2app'

      mv '../mac/setup.py', '.'
      # give write access to Qt's frameworks (fixes py2app permission errors)
      system 'chmod', '-R', 'u+w', Formula.factory('qt5').lib

      system 'python3', 'setup.py', 'py2app'
      # convert dynamic links into static links and adds qt5 plugins (cocoa...)
      system "#{Formula.factory('qt5').bin}/macdeployqt", 'dist/starcheat.app', '-verbose=2'

      cp_r 'dist/starcheat.app', prefix/'StarCheat.app'
      rm_rf ['build', 'dist', 'setup.py']
    end if build.with? 'app'

    if build.with? 'binary'
      libexec.install Dir['build/*']
      bin.install_symlink libexec+'starcheat.py' => 'starcheat'
    end
  end

  test do
    system bin/'starcheat', '-v' if build.with? 'binary'
    system prefix/'StarCheat.app/Contents/MacOS/starcheat', '-v' if build.with? 'app'
  end

  def caveats
    <<-EOS.undent
      You can run this to symlink the StarCheat.app into your Application folder:
        `brew linkapps`
      or just copy it from here for further distributing:
        #{prefix}/StarCheat.app
    EOS
  end
end
