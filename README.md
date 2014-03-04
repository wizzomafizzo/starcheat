# starcheat [![Build Status](https://travis-ci.org/wizzomafizzo/starcheat.png?branch=master)](https://travis-ci.org/wizzomafizzo/starcheat)

starcheat is a [Starbound](http://playstarbound.com/) player save editor, you can get free pixels with this! (omg)

**[starcheat.org](http://starcheat.org) wiki is now up with the latest downloads, guides and troubleshooting info.**

![woohoo](https://raw.github.com/wizzomafizzo/starcheat/master/starcheat/images/screenshot.png)

If you're not trying to build starcheat yourself, here be dragons.

## Building from source
Here is how to build starcheat from source. Make sure everything in the dependencies section is installed before you do a build.

### Dependencies
- [Python 3.3+](http://www.python.org/getit/)
- [PyQt5](http://www.riverbankcomputing.com/software/pyqt/download5)
- [Qt 5](http://qt-project.org/downloads) (don't need this on Windows)
- [Pillow](https://pypi.python.org/pypi/Pillow/)
- [py-starbound](https://github.com/blixt/py-starbound) (this is included as a [git submodule](http://git-scm.com/docs/git-submodule))

### Windows
Lines starting with ```>``` can be run in PowerShell or cmd.exe.

- ```> cd <starcheat top folder>```
- ```> C:\Python33\python.exe .\build.py```
- Browse to newly created ```build\``` folder
- Double click ```starcheat.py```

#### Standalone Build
The standalone build makes an executable which includes all Python and Qt dependencies.

- Install [cx_freeze](http://cx-freeze.sourceforge.net/)
- ```> cd <starcheat top folder>```
- ```> C:\Python33\python.exe .\build.py -e```
- Browse to newly created ```dist\``` folder
- Double click ```starcheat.exe```

### Linux
```
$ cd <starcheat top folder>
$ ./build.py
$ ./build/starcheat.py
```

### Mac
- Install [homebrew](http://brew.sh/)
- ```$ brew update```
- ```$ brew install https://raw.github.com/wizzomafizzo/starcheat/master/mac/starcheat.rb``` (optionally pass ```--without-app``` (create no .app) or ```--without-binary``` (creates no binary linked into your prefix) )
- ```brew linkapps``` (symlinks the .app into your Applications folder)
