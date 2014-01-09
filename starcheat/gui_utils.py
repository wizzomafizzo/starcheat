"""
Utility dialogs for starcheat itself
"""

import os
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from config import Config
import save_file, assets
import qt_options, qt_openplayer

class OptionsDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_options.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.config = Config()

        # read the current config and prefill everything
        self.ui.assets_folder.setText(self.config.read("assets_folder"))
        self.ui.player_folder.setText(self.config.read("player_folder"))

        self.ui.assets_folder_button.clicked.connect(self.open_assets)
        self.ui.player_folder_button.clicked.connect(self.open_player)
        self.ui.rebuild_button.clicked.connect(self.rebuild_db)

        self.ui.buttonBox.accepted.connect(self.write)

    def write(self):
        self.config.set("assets_folder", self.ui.assets_folder.text())
        self.config.set("player_folder", self.ui.player_folder.text())

    def open_assets(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                               "Choose assets folder...",
                                               self.config.read("assets_folder"))
        if filename != "": self.ui.assets_folder.setText(filename)

    def open_player(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                               "Choose player save folder...",
                                               self.config.read("player_folder"))
        if filename != "": self.ui.player_folder.setText(filename)

    def validate_options(self):
        if os.path.isdir(self.ui.assets_folder.text()) == False:
            return False
        if os.path.isdir(self.ui.player_folder.text()) == False:
            return False
        return True

    def rebuild_db(self):
        self.write()
        assets.AssetsDb().rebuild_db()

# TODO: not sure the check for no players found is working? if user forgets
#       to set a player_folder on setup they will be forced to edit the ini
# TODO: support stuff like sorting by date (add column to table widget)
# TODO: disable the ok button until a valid item is selected
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
        for player in self.players.keys():
            self.ui.player_list.addItem(player)

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
            msg = "No compatible save files found in: %s" % (self.player_folder)
            dialog.setText(msg)
            dialog.exec()
            manual_player = self.manual_select()
            if manual_player[0] != "":
                self.selected = save_file.PlayerSave(manual_player[0])
        else:
            self.dialog.exec()
