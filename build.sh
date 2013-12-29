#!/usr/bin/env bash

files=(assets.py config.py gui.py save_file.py starcheat.py)
templates=(ItemEdit.ui Blueprints.ui MainWindow.ui ItemBrowser.ui Options.ui OpenPlayer.ui)

[[ -d build/ ]] && rm -rf build/
mkdir build/

for f in ${files[*]}; do
	cp starcheat/$f build/
done

for t in ${templates[*]}; do
	pyuic5 starcheat/templates/$t > build/qt_$(echo $t | tr '[:upper:]' '[:lower:]' | sed 's/ui$/py/')
done
