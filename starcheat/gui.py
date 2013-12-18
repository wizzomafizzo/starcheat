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

        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionQuit.triggered.connect(self.app.closeAllWindows)

        self.ui.main_bag.setHorizontalHeaderLabels(("Count", "Type"))

        self.open_file()

        for var in save_file.data_format:
            print(var[0], ":", self.player.data[var[0]])

        self.window.show()
        sys.exit(self.app.exec_())

    def save(self):
        self.player.data["name"] = self.ui.name.text()
        self.player.data["inv"]["pixels"] = (self.ui.pixels.value(),)
        self.player.data["description"] = self.ui.description.text()

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

        self.player.export_save(self.player.filename)
        self.ui.statusbar.showMessage("Saved " + self.player.filename, 3000)

    def update(self):
        self.ui.name.setText(self.player.data["name"])
        self.ui.race.setText(self.player.data["race"])
        self.ui.pixels.setValue(self.player.data["inv"]["pixels"][0])
        self.ui.description.setText(self.player.data["description"])

        if self.player.data["invulnerable"][0] == 1:
            self.ui.invulnerable.setChecked(True)

        if self.player.data["god_mode"][0] == 1:
            self.ui.godmode.setChecked(True)

        if self.player.data["gender"]:
            self.ui.male.toggle()
        else:
            self.ui.female.toggle()

        # TODO: sliders need max update when max val is changed
        self.ui.health.setMaximum(self.player.data["health"][1])
        self.ui.health.setValue(self.player.data["health"][0])
        self.ui.max_health.setValue(self.player.data["base_max_health"][0])

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

        self.ui.head.setText(self.player.data["head"][0])
        self.ui.head_glamor.setText(self.player.data["head_glamor"][0])

        self.ui.chest.setText(self.player.data["chest"][0])
        self.ui.chest_glamor.setText(self.player.data["chest_glamor"][0])

        self.ui.legs.setText(self.player.data["legs"][0])
        self.ui.legs_glamor.setText(self.player.data["legs_glamor"][0])

        self.ui.backpack.setText(self.player.data["back"][0])
        self.ui.backpack_glamor.setText(self.player.data["back_glamor"][0])

        self.ui.left_hand.setText(self.player.data["inv"]["wieldable"][0][0])
        self.ui.right_hand.setText(self.player.data["inv"]["wieldable"][1][0])

        # TODO: make a function
        main_bag = self.player.data["inv"]["main_bag"]
        self.ui.main_bag.setRowCount(len(main_bag))
        for i in range(len(main_bag)):
            count = QTableWidgetItem(str(main_bag[i][1]))
            item_type = QTableWidgetItem(main_bag[i][0])
            self.ui.main_bag.setItem(i, 0, count)
            self.ui.main_bag.setItem(i, 1, item_type)

        tile_bag = self.player.data["inv"]["tile_bag"]
        self.ui.tile_bag.setRowCount(len(tile_bag))
        for i in range(len(tile_bag)):
            count = QTableWidgetItem(str(tile_bag[i][1]))
            item_type = QTableWidgetItem(tile_bag[i][0])
            self.ui.tile_bag.setItem(i, 0, count)
            self.ui.tile_bag.setItem(i, 1, item_type)

        action_bar = self.player.data["inv"]["action_bar"]
        self.ui.action_bar.setRowCount(len(action_bar))
        for i in range(len(action_bar)):
            count = QTableWidgetItem(str(action_bar[i][1]))
            item_type = QTableWidgetItem(action_bar[i][0])
            self.ui.action_bar.setItem(i, 0, count)
            self.ui.action_bar.setItem(i, 1, item_type)

        equip_bag = self.player.data["inv"]["equipment"]
        self.ui.equip_bag.setRowCount(len(equip_bag))
        for i in range(len(equip_bag)):
            count = QTableWidgetItem(str(equip_bag[i][1]))
            item_type = QTableWidgetItem(equip_bag[i][0])
            self.ui.equip_bag.setItem(i, 0, count)
            self.ui.equip_bag.setItem(i, 1, item_type)

        wield_bag = self.player.data["inv"]["wieldable"]
        self.ui.wield_bag.setRowCount(len(wield_bag))
        for i in range(len(wield_bag)):
            count = QTableWidgetItem(str(wield_bag[i][1]))
            item_type = QTableWidgetItem(wield_bag[i][0])
            self.ui.wield_bag.setItem(i, 0, count)
            self.ui.wield_bag.setItem(i, 1, item_type)

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
