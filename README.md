# starcheat [![Travis build (OS X)](https://img.shields.io/travis/wizzomafizzo/starcheat.svg?label=Travis build (OS X))](https://travis-ci.org/wizzomafizzo/starcheat) [![AppVeyor build (Windows)](https://img.shields.io/appveyor/ci/wizzomafizzo/starcheat.svg?label=AppVeyor build (Windows))](https://ci.appveyor.com/project/wizzomafizzo/starcheat)

starcheat is a [Starbound](http://playstarbound.com/) player save editor, you can get free pixels with this! (omg)

![woohoo](https://raw.github.com/wizzomafizzo/starcheat/master/starcheat/images/screenshot.png)

## Downloads

Starbound          | starcheat
------------------ | ---------
Nightly            | [dev branch](#building-from-source)
**Upbeat Giraffe** | [0.20](https://github.com/wizzomafizzo/starcheat/releases/tag/0.20)
Enraged Koala      | [0.17](https://github.com/wizzomafizzo/starcheat/releases/tag/0.17)

## Reporting a Issue
Please read and follow these [instructions](CONTRIBUTING.md) when reporting an issue. This will help us fix your issue faster, because we don't need to ask you for additional informations.

## Building from source
Here is how to build starcheat from source. Make sure everything in the dependencies section is installed before you do a build.

### Dependencies
- [Python 3.3+](http://www.python.org/getit/)
- [PyQt5](http://www.riverbankcomputing.com/software/pyqt/download5)
- [Qt 5](http://qt-project.org/downloads) (included in PyQt5 binaries on Windows)
- [Pillow](https://pypi.python.org/pypi/Pillow/)
- [py-starbound](https://github.com/blixt/py-starbound)

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

##### Install
- Install [homebrew](http://brew.sh/)
- ```$ brew update```
- ```$ brew tap chrmoritz/starcheat```
- ```$ brew install starcheat``` (optionally pass ```--without-app``` to not create a `.app`)
- ```brew linkapps starcheat``` (symlinks the `.app` into your Applications folder)

##### Update
- ```$ brew update``` (check if starcheat is in the updated formula list)
- ```$ brew upgrade starcheat``` (if its in the list above or in `brew outdated`)

## Release checklist
- [ ] Update version string in [config.py](starcheat/config.py)
- [ ] Update version string in starcheat tap's [brew file](https://github.com/chrmoritz/homebrew-starcheat/blob/master/starcheat.rb)
- [ ] Update storage name in [config.py](starcheat/config.py) and [assets.py](starcheat/assets.py)
- [ ] Tag release
