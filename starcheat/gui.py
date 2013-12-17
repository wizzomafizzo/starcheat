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

        self.ui.tableWidget.setHorizontalHeaderLabels(("Count", "Type"))

        self.open_file()

        for var in save_file.data_format:
            print(var[0], ":", self.player.data[var[0]])

        self.window.show()
        sys.exit(self.app.exec_())

    def save(self):
        self.player.data["name"] = self.ui.name.text()
        self.player.data["inv"]["pixels"] = (self.ui.pixels.value(),)
        self.player.data["description"] = self.ui.desc.text()

        for i in range(len(self.player.data["inv"]["main_bag"])):
            count = self.ui.tableWidget.item(i, 0).text()
            item_type = self.ui.tableWidget.item(i, 1).text()
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
        self.ui.statusbar.showMessage("Player saved: " + self.player.filename, 3000)

    def update(self):
        self.ui.name.setText(self.player.data["name"])
        self.ui.pixels.setValue(self.player.data["inv"]["pixels"][0])
        self.ui.desc.setText(self.player.data["description"])

        if self.player.data["gender"]:
            self.ui.male.toggle()
        else:
            self.ui.female.toggle()

        # TODO: make a function
        main_bag = self.player.data["inv"]["main_bag"]
        self.ui.tableWidget.setRowCount(len(main_bag))
        for i in range(len(main_bag)):
            count = QTableWidgetItem(str(main_bag[i][1]))
            item_type = QTableWidgetItem(main_bag[i][0])
            self.ui.tableWidget.setItem(i, 0, count)
            self.ui.tableWidget.setItem(i, 1, item_type)

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

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self.window,
                                               'Open save file...',
                                               '/opt/starbound/linux64/player',
                                               '*.player')
        self.player = save_file.PlayerSave(filename[0])
        self.update()
        self.ui.statusbar.showMessage("Opened player: " + self.player.filename, 3000)

if __name__ == '__main__':
    window = MainWindow()
