# starcheat

Starbound player save editor, you can get free pixels with this (omg)

![woohoo](https://raw.github.com/wizzomafizzo/starcheat/master/screen1.png)

## install
here is how to install it

### requirements
- [python 3](http://www.python.org/getit/)
- [qt5](http://qt-project.org/downloads)
- [pyqt5](http://www.riverbankcomputing.com/software/pyqt/download5)

### before setup
- update starcheat/starcheat.ini with your own Starbound folders

### windows
- install python 3 and pyqt5 (you don't need qt5)
- > cd \<starcheat top folder\>
- > ./build.bat
- browse to newly created build/ folder
- double click starcheat.py

#### standalone build
standalone build makes an executable and includes all python and qt dependencies

- install [cx_freeze](http://cx-freeze.sourceforge.net/)
- PS> cd \<starcheat top folder\>
- PS> ./build.ps1 -Standalone
- browse to newly created dist/ folder
- double click starcheat.exe

END USERS: if Windows complains about a system error (re: missing msvcr100.dll), you probably need to install the [vs c++ 2010 runtime package](http://www.microsoft.com/en-au/download/details.aspx?id=14632)

### linux
- install python 3, qt5 and pyqt5 from your distro repos
- $ cd \<starcheat top folder\>
- $ ./build.sh
- $ cd build/
- $ ./starcheat.py
