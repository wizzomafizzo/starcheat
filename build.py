#!/usr/bin/env python3

import os, platform, shutil
from optparse import OptionParser

def main():
    desc = "builds starbound using pyqt5 and python3"
    if platform.system() == "Windows":
        desc += " (with cx_freeze if --with-exe is passed)"
    parser = OptionParser(description=desc)
    parser.add_option("-p", "--prefix", "-b", "--build", "--build-dir", dest="prefix", default="build",
                      help="build and install starboud to this prefix (default to build)")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="print status messages to stdout")
    if platform.system() == "Windows":
        parser.add_option("-e", "--exe", "--with-exe", "--enable-exe", action="store_true", dest="exe",
                          help="generates .exe (windows only)")
        parser.add_option("-d", "--dist", "--dist-dir", dest="dist", default="dist",
                          help="generates .exe to this dir (default to dist)")
    (options, args) = parser.parse_args()

    src_dir = os.path.dirname(os.path.realpath(__file__));
    templates = os.listdir(os.path.join(src_dir, "starcheat", "templates"))
    prefix = os.path.expanduser(options.prefix)
    if platform.system() == "Windows":
        from distutils.sysconfig import get_python_lib
        site_packages_dir = get_python_lib()
        pyqt5_dir = os.path.join(site_packages_dir, "PyQt5")
        cx_freeze_Path = os.path.join(os.path.dirname(os.path.dirname(site_packages_dir)), "Scripts", "cxfreeze")
        dist = os.path.expanduser(options.dist)

    if options.verbose:
        print("Starting building starcheat to " + prefix + " ...")

    if os.path.exists(prefix):
        if options.verbose:
            print("Removing existing build directory")
        shutil.rmtree(prefix)

    if options.verbose:
        print("Copying starcheat python scripts")
    shutil.copytree(os.path.join(src_dir, "starcheat"), prefix,
                    ignore=shutil.ignore_patterns("templates", "starbound", "images", "*.qrc"))

    if options.verbose:
        print("Copying py-starbound module")
    shutil.copytree(os.path.join(src_dir, "starcheat", "starbound", "starbound"),
                    os.path.join(prefix, "starbound"))

    if options.verbose:
        print("Generating python Qt templates...")
    for t in templates:
        temp = os.path.join(src_dir, "starcheat", "templates", t)
        pyname = "qt_"+t.lower().replace(".ui", ".py")
        if platform.system() == "Windows":
            os.system(os.path.join(pyqt5_dir, "pyuic5.bat") + " \"" + temp + "\" > " + os.path.join(prefix, pyname))
        else:
            os.system("pyuic5 \"" + temp + "\" > " + os.path.join(prefix, pyname))
        if options.verbose:
            print("Generated " + pyname)

    if options.verbose:
        print("Generating python Qt resource...")
    res_file = os.path.join(src_dir, "starcheat", "resources.qrc")
    pyname = "resources_rc.py"
    if platform.system() == "Windows":
        os.system(os.path.join(pyqt5_dir, "pyrcc5.exe") + " \"" + res_file + "\" > " + os.path.join(prefix, pyname))
    else:
        os.system("pyrcc5 \"" + res_file + "\" > " + os.path.join(prefix, pyname))
    if options.verbose:
        print("Generated " + pyname)

    if options.verbose:
        print("Script build is complete!")

    if platform.system() == "Windows" and options.exe:
        if options.verbose:
            print("Starting generating starcheat standalone Windows build to " + dist + " ...")

        if os.path.exists(dist):
            if options.verbose:
                print("Removing existing dist directory")
            shutil.rmtree(dist)

        if options.verbose:
            print("Launching cx_freeze...")
        icon_path = os.path.join(src_dir, "starcheat", "images", "starcheat.ico")
        os.system("python " + cx_freeze_Path + " \"" + os.path.join(prefix, "starcheat.py") + "\" --target-dir=\"" +
                  dist + "\" --base-name=Win32GUI --icon=\"" + icon_path +"\"")
        shutil.copy(os.path.join(pyqt5_dir, "libEGL.dll"), dist)

        if options.verbose:
            print("Standalone build is complete!")

if __name__ == "__main__":
    main()
