require 'formula'

class Pyqt5 < Formula
  homepage 'http://www.riverbankcomputing.co.uk/software/pyqt/download5'
  url 'http://downloads.sf.net/project/pyqt/PyQt5/PyQt-5.1.1/PyQt-gpl-5.1.1.tar.gz'
  sha1 '90a3d6a805da7559ad83704866c1751d698f1873'

  option 'enable-debug', "Build with debug symbols"

  depends_on 'python3'
  depends_on 'qt5' => :build
  depends_on 'https://raw.github.com/wizzomafizzo/starcheat/master/mac/sip.rb'

  bottle do
    root_url 'https://github.com/chrmoritz/starcheat/releases/download/67d39a4'
    sha1 '80a58e23671775a4396a9cf1c4e1574f896ad7aa' => :lion_or_later
  end

  def install
    args = [ "--confirm-license",
             "--bindir=#{bin}",
             "--destdir=#{lib}/python3.3/site-packages",
             # To avoid conflicst with PyQt (for Qt4):
             "--sipdir=#{share}/sip3/Qt5/",
             # sip.h could not be found automatically
             "--sip-incdir=#{Formula.factory('sip').opt_prefix}/include",
             # Force deployment target to avoid libc++ issues
             "QMAKE_MACOSX_DEPLOYMENT_TARGET=#{MacOS.version}" ]
    args << '--debug' if build.include? 'enable-debug'

    system "python3.3", "./configure.py", *args
    system "make"
    system "make", "install"
  end

  test do
    (testpath/'test.py').write <<-EOS.undent
      import sys
      from PyQt5 import QtGui, QtCore, QtWidgets

      class Test(QtWidgets.QWidget):
          def __init__(self, parent=None):
              QtWidgets.QWidget.__init__(self, parent)
              self.setGeometry(300, 300, 400, 150)
              self.setWindowTitle('Homebrew')
              QtWidgets.QLabel("Python " + "{0}.{1}.{2}".format(*sys.version_info[0:3]) +
                               " working with PyQt5. Quitting now...", self).move(50, 50)
              QtCore.QTimer.singleShot(1500, QtWidgets.qApp.quit)

      app = QtWidgets.QApplication([])
      window = Test()
      window.show()
      sys.exit(app.exec_())
    EOS
    system "python3.3", "test.py"
  end
end
