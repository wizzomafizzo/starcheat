"""
Qt ship management dialog
"""

import logging

from gui.common import ListEdit

import qt_ship

from PyQt5.QtWidgets import QDialog


class Ship():
    def __init__(self, main_window):
        self.dialog = QDialog(main_window.window)
        self.ui = qt_ship.Ui_Dialog()
        self.ui.setupUi(self.dialog)
        self.main_window = main_window

        self.assets = main_window.assets
        self.player = main_window.player

        self.ship_upgrades = self.player.get_ship_upgrades()
        self.ai = self.player.get_ai()

        self.ui.capabilities_button.clicked.connect(self.edit_capabilities)
        self.ui.available_missions_button.clicked.connect(self.edit_available)
        self.ui.completed_missions_button.clicked.connect(self.edit_completed)
        self.ui.enabled_commands_button.clicked.connect(self.edit_enabled)

        self.update()

    def update(self):
        self.ui.upgrade_level.setValue(self.ship_upgrades["shipLevel"])
        self.ui.max_fuel.setValue(self.ship_upgrades["maxFuel"])
        self.ui.capabilities.setText(", ".join(self.ship_upgrades["capabilities"]))

        self.ui.command_level.setValue(self.ai["commandLevel"])
        self.ui.available_missions.setText(", ".join(self.ai["availableMissions"]))
        self.ui.completed_missions.setText(", ".join(self.ai["completedMissions"]))
        self.ui.enabled_commands.setText(", ".join(self.ai["enabledCommands"]))

    def edit_capabilities(self):
        edit = ListEdit(self.dialog, self.ship_upgrades["capabilities"])
        ok = edit.dialog.exec()
        if ok == 1:
            self.ship_upgrades["capabilities"] = edit.get_list()
            self.update()

    def edit_available(self):
        edit = ListEdit(self.dialog, self.ai["availableMissions"])
        ok = edit.dialog.exec()
        if ok == 1:
            self.ai["availableMissions"] = edit.get_list()
            self.update()

    def edit_completed(self):
        edit = ListEdit(self.dialog, self.ai["completedMissions"])
        ok = edit.dialog.exec()
        if ok == 1:
            self.ai["completedMissions"] = edit.get_list()
            self.update()

    def edit_enabled(self):
        edit = ListEdit(self.dialog, self.ai["enabledCommands"])
        ok = edit.dialog.exec()
        if ok == 1:
            self.ai["enabledCommands"] = edit.get_list()
            self.update()

    def write_ship(self):
        self.ship_upgrades["maxFuel"] = self.ui.max_fuel.value()
        self.ship_upgrades["shipLevel"] = self.ui.upgrade_level.value()
        self.ai["commandLevel"] = self.ui.command_level.value()
        self.player.set_ship_upgrades(self.ship_upgrades)
        self.player.set_ai(self.ai)
        logging.debug("Wrote ship/ai")
        self.main_window.window.setWindowModified(True)
