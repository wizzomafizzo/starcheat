#!/usr/bin/env bash

files=(assets.py config.py save_file.py starcheat.py)

[[ -d build/ ]] && rm -rf build/
mkdir build/

for f in ${files[*]}; do
	cp starcheat/$f build/
done

for f in $(ls starcheat/gui*.py); do
	cp $f build/
done

for t in $(ls starcheat/templates/*.ui); do
	pyuic5 $t > build/qt_$(echo $(basename $t) | tr '[:upper:]' '[:lower:]' | sed 's/ui$/py/')
done
