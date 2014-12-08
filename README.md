# starcheat [![Build Status](https://travis-ci.org/wizzomafizzo/starcheat.svg)](https://travis-ci.org/wizzomafizzo/starcheat)

starcheat is a [Starbound](http://playstarbound.com/) player save editor, you can get free pixels with this! (omg)

**An archive of the old starcheat wiki is located in the website_archive folder.**

![woohoo](https://raw.github.com/wizzomafizzo/starcheat/master/starcheat/images/screenshot.png)

## Building from source
Here is how to build starcheat from source. Make sure everything in the dependencies section is installed before you do a build.

### Dependencies
- [Python 3.3+](http://www.python.org/getit/)
- [PyQt5](http://www.riverbankcomputing.com/software/pyqt/download5)
- [Qt 5](http://qt-project.org/downloads) (don't need this on Windows)
- [Pillow](https://pypi.python.org/pypi/Pillow/)
- [py-starbound](https://github.com/blixt/py-starbound)

**NOTE:** py-starbound is included as a [git submodule](http://git-scm.com/docs/git-submodule) and needs to be cloned with the following commands:

- ```> cd <starcheat parent folder>/starcheat/starbound```
- ```> git submodule init```
- ```> git submodule update```

Applications such as [Sourcetree](http://www.sourcetreeapp.com/) should offer to clone it automatically.

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

## Release checklist
- [ ] Update version string in config.py
- [ ] Update version string in brew file
- [ ] Tag release
