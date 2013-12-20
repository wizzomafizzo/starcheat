#!/usr/bin/python3

import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QFileDialog, QTableWidgetItem
from qt_mainwindow import Ui_MainWindow

import save_file

class MainWindow():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        for race in save_file.race_types:
            self.ui.race.addItem(race[0].upper() + race[1:])

        self.open_file()

        #for var in save_file.data_format:
        #    print(var[0], ":", self.player.data[var[0]])

        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionQuit.triggered.connect(self.app.closeAllWindows)

        self.ui.max_health.valueChanged.connect(self.update_max_health)

        self.ui.main_bag.setHorizontalHeaderLabels(("Count", "Type"))

        self.ui.health.valueChanged.connect(self.update_max_health)

        self.window.show()
        sys.exit(self.app.exec_())

    def update_max_health(self):
        self.ui.health.setMaximum(self.ui.max_health.value())
        self.ui.health_val.setText(str(self.ui.health.value()) + " /")

    def save(self):
        self.player.data["name"] = self.ui.name.text()
        self.player.data["race"] = self.ui.race.text()
        self.player.data["inv"]["pixels"] = (self.ui.pixels.value(),)
        self.player.data["description"] = self.ui.description.toPlainText()

        # gender
        if self.ui.male.isChecked():
            self.player.data["gender"] = (0,)
        else:
            self.player.data["gender"] = (1,)

        # health
        self.player.data["health"] = (self.ui.health.value(), int(self.ui.max_health.value()))
        self.player.data["base_max_health"] = (int(self.ui.max_health.value()),)

        # energy
        self.player.data["energy"] = (self.ui.energy.value(), int(self.ui.max_energy.value()))
        self.player.data["base_max_energy"] = (int(self.ui.max_energy.value()),)

        # hunger
        self.player.data["food"] = (self.ui.hunger.value(), self.player.data["food"][1])

        # warmth
        self.player.data["warmth"] = (self.player.data["warmth"][0], self.ui.warmth.value())

        # breath
        self.player.data["breath"] = (self.ui.breath.value(), self.ui.breath.maximum())

        # head
        # chest
        # legs
        # backpack

        # left hand
        # right hand

        for i in range(len(self.player.data["inv"]["main_bag"])):
            count = self.ui.main_bag.item(i, 0).text()
            item_type = self.ui.main_bag.item(i, 1).text()
            variant = self.player.data["inv"]["main_bag"][i][2]
            self.player.data["inv"]["main_bag"][i] = (item_type, int(count), variant)

        for i in range(len(self.player.data["inv"]["tile_bag"])):
            count = self.ui.tile_bag.item(i, 0).text()
            item_type = self.ui.tile_bag.item(i, 1).text()
            variant = self.player.data["inv"]["tile_bag"][i][2]
            self.player.data["inv"]["tile_bag"][i] = (item_type, int(count), variant)

        for i in range(len(self.player.data["inv"]["action_bar"])):
            count = self.ui.action_bar.item(i, 0).text()
            item_type = self.ui.action_bar.item(i, 1).text()
            variant = self.player.data["inv"]["action_bar"][i][2]
            self.player.data["inv"]["action_bar"][i] = (item_type, int(count), variant)

        # equipment
        # wieldable

        self.player.export_save(self.player.filename)
        self.ui.statusbar.showMessage("Saved " + self.player.filename, 3000)

    def update(self):
        self.ui.name.setText(self.player.data["name"])

        self.ui.race.setCurrentText(self.player.data["race"][0].upper() + self.player.data["race"][1:])

        self.ui.pixels.setValue(self.player.data["inv"]["pixels"][0])
        self.ui.description.setPlainText(self.player.data["description"])

        if self.player.data["gender"][0] == 0:
            self.ui.male.toggle()
        else:
            self.ui.female.toggle()

        # TODO: sliders need max update when max val is changed
        self.ui.health.setMaximum(self.player.data["health"][1])
        self.ui.health.setValue(self.player.data["health"][0])
        self.ui.max_health.setValue(self.player.data["base_max_health"][0])
        self.ui.health_val.setText(str(self.ui.health.value()) + " /")

        self.ui.energy.setMaximum(self.player.data["energy"][1])
        self.ui.energy.setValue(self.player.data["energy"][0])
        self.ui.max_energy.setValue(self.player.data["base_max_energy"][0])
        self.ui.energy_regen.setValue(self.player.data["energy_regen_rate"][0])

        self.ui.hunger.setMaximum(self.player.data["food"][1])
        self.ui.hunger.setValue(self.player.data["food"][0])

        self.ui.warmth.setMinimum(self.player.data["warmth"][0])
        # TODO: check this is right
        self.ui.warmth.setMaximum(100)
        self.ui.warmth.setValue(self.player.data["warmth"][1])

        self.ui.breath.setMaximum(self.player.data["breath"][1])
        self.ui.breath.setValue(self.player.data["breath"][0])

        # equipment
        head = QTableWidgetItem(self.player.data["head"][0])
        self.ui.head.setItem(0, 0, head)
        head_glamor = QTableWidgetItem(self.player.data["head_glamor"][0])
        self.ui.head.setItem(0, 1, head_glamor)

        chest = QTableWidgetItem(self.player.data["chest"][0])
        self.ui.chest.setItem(0, 0, chest)
        chest_glamor = QTableWidgetItem(self.player.data["chest_glamor"][0])
        self.ui.chest.setItem(0, 1, chest_glamor)

        legs = QTableWidgetItem(self.player.data["legs"][0])
        self.ui.legs.setItem(0, 0, legs)
        legs_glamor = QTableWidgetItem(self.player.data["legs_glamor"][0])
        self.ui.legs.setItem(0, 1, legs_glamor)

        back = QTableWidgetItem(self.player.data["back"][0])
        self.ui.back.setItem(0, 0, back)
        back_glamor = QTableWidgetItem(self.player.data["back_glamor"][0])
        self.ui.back.setItem(0, 1, back_glamor)

        left_hand = QTableWidgetItem(self.player.data["inv"]["wieldable"][0][0])
        self.ui.wielded.setItem(0, 0, left_hand)
        right_hand = QTableWidgetItem(self.player.data["inv"]["wieldable"][1][0])
        self.ui.wielded.setItem(0, 1, right_hand)

        main_bag_row = 0
        main_bag_column = 0
        main_bag = self.player.data["inv"]["main_bag"]
        for i in range(len(main_bag)):
            count = QTableWidgetItem(str(main_bag[i][1]))
            item_type = QTableWidgetItem(main_bag[i][0])
            self.ui.main_bag.setItem(main_bag_row, main_bag_column, item_type)
            main_bag_column += 1
            if (main_bag_column % 10) == 0:
                main_bag_row += 1
                main_bag_column = 0

        tile_bag_row = 0
        tile_bag_column = 0
        tile_bag = self.player.data["inv"]["tile_bag"]
        for i in range(len(tile_bag)):
            count = QTableWidgetItem(str(tile_bag[i][1]))
            item_type = QTableWidgetItem(tile_bag[i][0])
            self.ui.tile_bag.setItem(tile_bag_row, tile_bag_column, item_type)
            tile_bag_column += 1
            if (tile_bag_column % 10) == 0:
                tile_bag_row += 1
                tile_bag_column = 0

        action_bar = self.player.data["inv"]["action_bar"]
        for i in range(len(action_bar)):
            count = QTableWidgetItem(str(action_bar[i][1]))
            item_type = QTableWidgetItem(action_bar[i][0])
            self.ui.action_bar.setItem(0, i, item_type)

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self.window,
                                               'Open save file...',
                                               '/opt/starbound/linux64/player',
                                               '*.player')
        self.player = save_file.PlayerSave(filename[0])
        self.update()
        self.ui.statusbar.showMessage("Opened " + self.player.filename, 3000)

if __name__ == '__main__':
    window = MainWindow()
