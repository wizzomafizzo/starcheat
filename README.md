# starcheat [![Build Status](https://travis-ci.org/wizzomafizzo/starcheat.svg?branch=master)](https://travis-ci.org/wizzomafizzo/starcheat) [![Build status](https://ci.appveyor.com/api/projects/status/raaumvqaeryq08tf/branch/master?svg=true)](https://ci.appveyor.com/project/wizzomafizzo/starcheat/branch/master)

## Where to download starcheat

**[DOWNLOAD HERE](https://starcheat.net/)**

This GitHub is no longer maintained. You can download a working version of starcheat from [starcheat.net](https://starcheat.net/) or the [patched GitHub repo](https://github.com/gen3vra/starcheat-patched-bin/releases/latest).

Thanks to [@gen3vra](https://github.com/gen3vra) for creating this new working build.

## What is this

starcheat is a [Starbound](http://playstarbound.com/) player save editor, you can get free pixels with this! (omg)

![woohoo](https://raw.github.com/wizzomafizzo/starcheat/master/starcheat/images/screenshot.png)

## Downloads

**[Download working starcheat](https://starcheat.net/)**

### Nightlies

You can try out the latest in development version (which may not be stable) by following these steps.

#### Windows: Appveyor artifacts

You can download prebuild nightlies for the latest commit from our Appveyor build bot. Go to https://ci.appveyor.com/project/wizzomafizzo/starcheat/branch/dev or https://ci.appveyor.com/project/wizzomafizzo/starcheat/history for 1.0 nightlies (the ones labeled with `Pull request #288 - Starbound 1.0 Support`) choose the build matching your architecture (win32 or win64) and download the latest snapshot from the Artifacts tab.

#### Mac: Homebrew HEAD build

Follow [the steps below](#mac) to set up our Homebrew tap but instead of installing the stable version run `brew install chrmoritz/starcheat/starcheat --HEAD` to install the latest nightly or `brew install chrmoritz/starcheat/starcheat --devel` for the nightly with 1.0 support.

#### Linux + all Platforms: Build from source

Follow [the steps below](#building-from-source) to build the dev branch from source.

## Reporting an issue
Please read and follow these [instructions](CONTRIBUTING.md) when reporting an issue. This will help us fix your issue faster, because we don't need to ask you for additional information.

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
- ```$ brew install chrmoritz/starcheat/starcheat``` (optionally pass ```--without-app``` to not create a `.app` or pass ```--HEAD``` to build the nightly version (or ```--devel``` for the 1.0 nightly) instead of the latest stable release)
- ```brew linkapps starcheat``` (symlinks the `.app` into your Applications folder)

##### Update
- ```$ brew update``` (check if starcheat is in the updated formula list)
- ```$ brew upgrade starcheat``` (if its in the list above or in `brew outdated`)

## Release checklist
- [ ] Update item metadata to match current Starbound version in [saves.py](starcheat/saves.py)
- [ ] Update storage name in [config.py](starcheat/config.py) and [assets.py](starcheat/assets.py)
- [ ] Update version string in [config.py](starcheat/config.py)
- [ ] Update version string in starcheat tap's [brew file](https://github.com/chrmoritz/homebrew-starcheat/blob/master/starcheat.rb)
- [ ] Tag release
