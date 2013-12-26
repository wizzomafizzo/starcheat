@echo off
setlocal enableDelayedExpansion
SET files=assets.py config.py gui.py save_file.py starcheat.py starcheat.ini
SET templates=ItemEdit.ui Blueprints.ui MainWindow.ui ItemBrowser.ui

IF exist build rd /s /q build
mkdir build

for %%F in (%files%) do (
    copy starcheat\%%F build\%%F
)

for %%F in (%templates%) do (
	set "name=%%~nF"
	for %%C in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do set "name=!name:%%C=%%C!"
	call pyuic5 starcheat\templates\%%F > build\qt_!name!.py
)