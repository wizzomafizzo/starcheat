#!/usr/bin/env bash

[[ -d build/ ]] && rm -rf build/
mkdir build/

for f in $(ls starcheat/*.py); do
	cp $f build/
done

for t in $(ls starcheat/templates/*.ui); do
	pyuic5 $t > build/qt_$(basename $t | tr '[:upper:]' '[:lower:]' | sed 's/ui$/py/')
done
