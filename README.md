# starcheat [![Build Status](https://travis-ci.org/wizzomafizzo/starcheat.png?branch=master)](https://travis-ci.org/wizzomafizzo/starcheat)

starcheat is a Starbound player save editor, you can get free pixels with this! (omg)

**Downloads for starcheat are [here](#downloads).**

![woohoo](https://raw.github.com/wizzomafizzo/starcheat/master/starcheat/images/screenshot.png)

## Table of Contents

- [Downloads](#downloads)
	- [Windows](#windows)
	- [Mac](#mac)
- [Building from source](#building-from-source)
	- [Dependencies](#dependencies)
	- [Windows](#windows-1)
	- [Linux](#linux)
	- [Mac](#mac-1)
- [Help](#help)
	- [Reset all settings](#reset-all-settings)
	- [How to get logs](#how-to-get-logs)
	- [Unpacking Starbound assets](#unpacking-starbound-assets)

## Downloads
These are builds of the latest development version. They should work fine, but may be unstable. **Don't forget to back up your save files before using them.**

**NOTE:** starcheat is not a normal mod, it's a separate program. You don't need to put it in the Starbound mods folder.

### Windows
[Download here](http://callan.io/builds/starcheat-latest.zip) ([mirror](http://mcsi.mp/starcheat/))

If the latest version isn't working for you, you can try [this older version](http://callan.io/builds/starcheat-win32-89cc2b92b419950fda068210a513cd5cd9faf129.zip) of starcheat. Please report in the discussion thread if you end up needing to use it!

**NOTE:** If Windows complains about a system error (re: missing msvcr100.dll), you probably need to install the [Microsoft Visual C++ 2010 Redistributable Package](http://www.microsoft.com/en-au/download/details.aspx?id=5555).

#### How to run
* Download the starcheat .zip file above
* Extract all files into a folder somewhere (not the mods folder)
* Go into the newly created folder
* Run ```starcheat.exe```
* Follow the prompts to configure starcheat (only happens once)
* Open a player

### Mac
[Download here](https://github.com/wizzomafizzo/starcheat/releases) (get the newest release)

## Building from source
Here is how to build starcheat from source. Make sure everything in the dependencies section is installed before you do a build. **You don't need to build from source if you're on Windows or Mac.**

### Dependencies
- [Python 3.3](http://www.python.org/getit/)
- [Qt 5](http://qt-project.org/downloads) (Windows users don't need this)
- [PyQt5](http://www.riverbankcomputing.com/software/pyqt/download5)
- [Pillow](https://pypi.python.org/pypi/Pillow/)
- [StarDB](https://github.com/McSimp/StarDB)

### Windows
Lines starting with ```PS>``` are to be run in PowerShell.

- ```PS> cd <starcheat top folder>```
- ```PS> C:\Python33\python.exe .\build.py```
- Browse to newly created ```build\``` folder
- Double click ```starcheat.py```

#### Standalone Build
The standalone build makes an executable which includes all Python and Qt dependencies.

- Install [cx_freeze](http://cx-freeze.sourceforge.net/)
- ```PS> cd <starcheat top folder>```
- ```PS> C:\Python33\python.exe .\build.py -e```
- Browse to newly created ```dist\``` folder
- Double click ```starcheat.exe```

### Linux
```
$ cd <starcheat top folder>
$ ./build.py
$ ./build/starcheat.py
```

#### Arch Linux
Install [starcheat](https://aur.archlinux.org/packages/starcheat/) from AUR.

### Mac
- Install [homebrew](http://brew.sh/)
- ```$ brew update```
- ```$ brew install https://raw.github.com/wizzomafizzo/starcheat/master/mac/starcheat.rb``` (optionally pass ```--without-app``` (create no .app) or ```--without-binary``` (creates no binary linked into your prefix) )
- ```brew linkapps```(symlinks the .app into your Applications folder)

## Help
Stuff you can do when starcheat stops working. Clearing local settings and checking you did the setup correctly is always a good first step.

### Reset all settings
This will remove all locally stored data for starcheat and force a new setup dialog next run.

#### Windows
- Press the Windows key and R (```Win+R```) to bring up the Run... dialog
- Type ```%APPDATA%\starcheat``` and press Enter
- Delete ```assets.db``` and ```starcheat.ini``` from the folder that pops up

#### Linux
In a terminal:
- ```$ rm ~/.starcheat/assets.db```
- ```$ rm ~/.starcheat/starcheat.ini```

#### Mac
In Finder:
- Open the ```Go``` menu and click ```Go to Folder``` (or press ```Cmd+Shift+G```)
- Type ```~/Library/Application Support/starcheat``` and press Enter
- Delete ```assets.db``` and ```starcheat.ini``` from the folder that pops up

### How to get logs
This will point you to where the starcheat logs are stored. If you're trying to report an error, you only need to upload the latest log file.

#### Windows
- Press the Windows key and R (```Win+R```) to bring up the Run... dialog
- Type ```%APPDATA%\starcheat``` and press Enter

#### Linux
In a terminal:
- ```$ cd ~/.starcheat```

#### Mac
In Finder:
- Open the ```Go``` menu and click ```Go to Folder``` (or press ```Cmd+Shift+G```)
- Type ```~/Library/Application Support/starcheat``` and press Enter

### Unpacking Starbound assets
**NOTE:** You shouldn't have to do this at all in the latest versions of starcheat.

starcheat will try its best to unpack the vanilla assets for you during setup. If you need to include mods or if the vanilla unpack doesn't work, you can try these manual methods. If they don't work for you either, check out [this post](http://community.playstarbound.com/index.php?threads/how-to-successfully-pack-and-unpack-pak-files.66649/) on the forums for more options.

#### Windows
- Press the Windows key and R (```Win+R```) to bring up the Run... dialog
- Enter the following text into the prompt and press Enter:
  - "C:\Program Files (x86)\Steam\SteamApps\common\Starbound\win32\asset_unpacker.exe" "C:\Program Files (x86)\Steam\SteamApps\common\Starbound\assets\packed.pak" "C:\Program Files (x86)\Steam\SteamApps\common\Starbound\assets"
  - If Steam is not installed to the default location, change the paths above to match your Steam/Starbound location

#### Linux
**NOTE:** If you're on 32 bit, change the path to asset_unpacker.

In a terminal:
- ```$ cd ~/.steam/root/SteamApps/common/Starbound```
- ```$ linux64/asset_unpacker assets/packed.pak assets/```

#### Mac
In a terminal:
- ```$ cd ~/Library/Application\ Support/Steam/SteamApps/common/Starbound```
- ```$ Starbound.app/Contents/MacOS/asset_unpacker assets/packed.pak assets```
