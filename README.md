# starcheat

starcheat is a Starbound player save editor, you can get free pixels with this (omg)

*if you're looking for a windows or mac version, check the first post of the [discussion thread](http://community.playstarbound.com/index.php?threads/starcheat-player-save-editor-and-python-library.60174/)*

- mod db: http://community.playstarbound.com/index.php?resources/starcheat.699/

![woohoo](https://raw.github.com/wizzomafizzo/starcheat/master/screen.png)

## build
here is how to install it. make sure everything in the dependencies section is installed before you do a build

### dependencies
- [python 3](http://www.python.org/getit/)
- [qt 5](http://qt-project.org/downloads) (if you're using Windows you probably don't need this)
- [pyqt5](http://www.riverbankcomputing.com/software/pyqt/download5)

### windows
lines starting with PS> are to be run in powershell. don't forget to [set your execution policy](http://technet.microsoft.com/en-us/library/ee176961.aspx) if it's the first time you're using powershell

- PS> cd \<starcheat top folder\>
- PS> ./build.ps1
- browse to newly created build/ folder
- double click starcheat.py

#### standalone build
standalone build makes an executable and includes all python and qt dependencies

- install [cx_freeze](http://cx-freeze.sourceforge.net/)
- PS> cd \<starcheat top folder\>
- PS> ./build.ps1 -Standalone
- browse to newly created dist/ folder
- double click starcheat.exe

if windows complains about a system error (re: missing msvcr100.dll) you probably need to install the [vs c++ 2010 runtime update](http://www.microsoft.com/en-au/download/details.aspx?id=14632)

### linux
- $ cd \<starcheat top folder\>
- $ ./build.sh
- $ cd build/
- $ ./starcheat.py

#### arch linux
install [starcheat-git](https://aur.archlinux.org/packages/starcheat-git/) from AUR

### mac
- install [homebrew](http://brew.sh/)
- $ brew install https://gist.github.com/chrmoritz/8177384/raw/starcheat.rb; brew linkapps
