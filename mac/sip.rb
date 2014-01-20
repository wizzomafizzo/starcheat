require 'formula'

class Sip < Formula
  homepage 'http://www.riverbankcomputing.co.uk/software/sip'
  url 'http://download.sf.net/project/pyqt/sip/sip-4.15.4/sip-4.15.4.tar.gz'
  sha1 'a5f6342dbb3cdc1fb61440ee8acb805f5fec3c41'

  head 'http://www.riverbankcomputing.co.uk/hg/sip', :using => :hg
  
  depends_on 'python3'
  
  bottle do
    root_url 'https://github.com/chrmoritz/starcheat/releases/download/67d39a4'
    sha1 'd5f7345f3d42ccc9ea0ea2dba8528666ad6406a3' => :lion_or_later
  end

  def install
    if build.head?
      # Link the Mercurial repository into the download directory so
      # buid.py can use it to figure out a version number.
      ln_s downloader.cached_location + '.hg', '.hg'
      system "python3.3", "build.py", "prepare"
    end

    # The python block is run once for each python (2.x and 3.x if requested)
    # Note the binary `sip` is the same for python 2.x and 3.x
    # Set --destdir such that the python modules will be in the HOMEBREWPREFIX/lib/pythonX.Y/site-packages
    system "python3.3", "configure.py",
                            "--deployment-target=#{MacOS.version}",
                            "--destdir=#{lib}/python3.3/site-packages",
                            "--bindir=#{bin}",
                            "--incdir=#{include}",
                            "--sipdir=#{HOMEBREW_PREFIX}/share/sip3"
    system "make"
    system "make install"
    system "make clean"
  end

  def caveats
    "The sip-dir for Python 2.x is #{HOMEBREW_PREFIX}/share/sip."
  end
end
