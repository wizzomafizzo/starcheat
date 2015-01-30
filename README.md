# starcheat [![Build Status](https://travis-ci.org/wizzomafizzo/starcheat.svg)](https://travis-ci.org/wizzomafizzo/starcheat) [![Build status](https://ci.appveyor.com/api/projects/status/j2rbv526aq4r64jl?svg=true)](https://ci.appveyor.com/project/chrmoritz/starcheat-354)

starcheat is a [Starbound](http://playstarbound.com/) player save editor, you can get free pixels with this! (omg)

![woohoo](https://raw.github.com/wizzomafizzo/starcheat/master/starcheat/images/screenshot.png)

## Downloads

Starbound          | starcheat
------------------ | ---------
Nightly            | [dev branch](#building-from-source)
**Upbeat Giraffe** | [0.18](https://github.com/wizzomafizzo/starcheat/releases/tag/0.18)
Enraged Koala      | [0.17](https://github.com/wizzomafizzo/starcheat/releases/tag/0.17)

## Building from source
Here is how to build starcheat from source. Make sure everything in the dependencies section is installed before you do a build.

### Dependencies
- [Python 3.3+](http://www.python.org/getit/)
- [PyQt5](http://www.riverbankcomputing.com/software/pyqt/download5)
- [Qt 5](http://qt-project.org/downloads) (included in PyQt5 binaries on Windows)
- [Pillow](https://pypi.python.org/pypi/Pillow/)
- [py-starbound](https://github.com/blixt/py-starbound)
- 
**NOTE:** py-starbound is included as a [git submodule](http://git-scm.com/docs/git-submodule) and needs to be cloned with the following commands:

- ```cd <starcheat top folder>```
- ```git submodule sync```
- ```git submodule update --init```

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

- [Arch Linux (AUR)](https://aur.archlinux.org/packages/starcheat/)

### Mac
- Install [homebrew](http://brew.sh/)
- ```$ brew update```
- ```$ brew install https://raw.github.com/wizzomafizzo/starcheat/master/mac/starcheat.rb``` (optionally pass ```--without-app``` (create no .app) or ```--without-binary``` (creates no binary linked into your prefix) )
- ```brew linkapps``` (symlinks the .app into your Applications folder)

## Release checklist
- [ ] Update version string in config.py
- [ ] Update version string in brew file
- [ ] Tag release
