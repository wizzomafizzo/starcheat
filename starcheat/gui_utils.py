"""
Utility dialogs for starcheat itself
"""

import os
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QListWidgetItem
from PyQt5 import QtGui

from config import Config
from gui_common import preview_icon
import save_file, assets, logging
import qt_options, qt_openplayer, qt_about

def save_modified_dialog():
    """Display a prompt asking user what to do about a modified file. Return button clicked."""
    dialog = QMessageBox()
    dialog.setText("This player has been modified.")
    dialog.setInformativeText("Do you want to save your changes?")
    dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
    dialog.setDefaultButton(QMessageBox.Save)
    dialog.setIcon(QMessageBox.Question)
    return dialog.exec()

def new_setup_dialog():
    """Run through an initial setup dialog for starcheat if it's required."""
    if os.path.isfile(Config().ini_file):
        return

    logging.info("First setup dialog")
    starbound_folder = Config().detect_starbound_folder()

    if starbound_folder == "":
        dialog = QMessageBox()
        dialog.setText("Unable to detect the main Starbound folder.")
        dialog.setInformativeText("Please select it in the next dialog.")
        dialog.setIcon(QMessageBox.Warning)
        dialog.exec()
        starbound_folder = QFileDialog.getExistingDirectory(self.window,
                                                            "Select Starbound Folder")
    else:
        dialog = QMessageBox()
        dialog.setText("Detected the following folder as the location of Starbound. Is this correct?")
        dialog.setInformativeText(starbound_folder)
        dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        dialog.setIcon(QMessageBox.Question)
        answer = dialog.exec()
        if answer == QMessageBox.No:
            starbound_folder = QFileDialog.getExistingDirectory(self.window,
                                                                "Select Starbound Folder")
    if starbound_folder == "":
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Critical)
        dialog.setText("starcheat needs Starbound installed to work properly.")
        dialog.exec()
        sys.exit()

    Config().create_config(starbound_folder)

    dialog = QMessageBox()
    dialog.setText("starcheat will now build a database of Starbound assets.")
    dialog.setInformativeText("This can take a little while, please be patient.")
    dialog.setIcon(QMessageBox.Information)
    dialog.exec()

    assets.AssetsDb()
    total_items = assets.Items().get_item_total()

    if total_items == 0:
        dialog = QMessageBox()
        dialog.setText("No assets were found. starcheat may not run correctly.")
        dialog.setInformativeText("Check the assets location is correct in the Options dialog.")
        dialog.setIcon(QMessageBox.Warning)
        dialog.exec()

class AboutDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_about.Ui_Dialog()
        self.ui.setupUi(self.dialog)

class OptionsDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_options.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.config = Config()

        # read the current config and prefill everything
        self.ui.starbound_folder.setText(self.config.read("starbound_folder"))
        self.ui.assets_folder.setText(self.config.read("assets_folder"))
        self.ui.player_folder.setText(self.config.read("player_folder"))

        self.ui.starbound_folder_button.clicked.connect(self.open_starbound)
        self.ui.assets_folder_button.clicked.connect(self.open_assets)
        self.ui.player_folder_button.clicked.connect(self.open_player)
        self.ui.rebuild_button.clicked.connect(self.rebuild_db)

        self.ui.buttonBox.accepted.connect(self.write)

    def write(self):
        self.config.set("starbound_folder", self.ui.starbound_folder.text())
        self.config.set("assets_folder", self.ui.assets_folder.text())
        self.config.set("player_folder", self.ui.player_folder.text())

    def open_starbound(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                                    "Select Starbound Folder",
                                                    self.config.read("starbound_folder"))
        if filename != "": self.ui.starbound_folder.setText(filename)

    def open_assets(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                                    "Select Assets Folder",
                                                    self.config.read("assets_folder"))
        if filename != "": self.ui.assets_folder.setText(filename)

    def open_player(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                                    "Select Player Save Folder",
                                                    self.config.read("player_folder"))
        if filename != "": self.ui.player_folder.setText(filename)

    def rebuild_db(self):
        self.write()
        assets.AssetsDb().rebuild_db()

# TODO: support stuff like sorting by date (needs to be a table widget)
class CharacterSelectDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_openplayer.Ui_OpenPlayer()
        self.ui.setupUi(self.dialog)

        self.player_folder = Config().read("player_folder")

        self.dialog.rejected.connect(self.dialog.close)
        self.dialog.accepted.connect(self.accept)
        # bizarre, if i set this to self.accept it just doesn't work...
        self.ui.player_list.itemDoubleClicked.connect(self.dialog.accept)

        self.get_players()
        self.populate()
        self.ui.player_list.setFocus()

    def accept(self):
        player = self.ui.player_list.currentItem().text()
        if player != "":
            self.selected = self.players[player]
            self.dialog.close()

    def get_players(self):
        players_found = {}

        try:
            for f in os.listdir(self.player_folder):
                if f.endswith(".player"):
                    try:
                        player = save_file.PlayerSave(os.path.join(self.player_folder, f))
                        players_found[player.get_name()] = player
                    except save_file.WrongSaveVer:
                        logging.info("Save file %s is not compatible", f)
        except FileNotFoundError:
            logging.exception("Could not open %s", self.player_folder)

        self.players = players_found

    def populate(self):
        total = 0
        self.ui.player_list.clear()
        for player in self.players.keys():
            list_item = QListWidgetItem(player)
            race = self.players[player].get_race()
            gender = self.players[player].get_gender()
            list_item.setIcon(QtGui.QIcon(preview_icon(race, gender)))
            self.ui.player_list.addItem(list_item)
            total += 1
        self.ui.total_label.setText(str(total) + " total")
        self.ui.player_list.setCurrentRow(0)

    def manual_select(self):
        manual_select = QFileDialog.getOpenFileName(None,
                                                    "Select player save file...",
                                                    self.player_folder,
                                                    "*.player")
        return manual_select

    def show(self):
        # quit if there are no players
        if len(self.players) == 0:
            dialog = QMessageBox()
            dialog.setText("No compatible save files found in:")
            dialog.setInformativeText(self.player_folder)
            dialog.setIcon(QMessageBox.Warning)
            dialog.exec()
            manual_player = self.manual_select()
            if manual_player[0] != "":
                self.selected = save_file.PlayerSave(manual_player[0])
        else:
            self.dialog.exec()
