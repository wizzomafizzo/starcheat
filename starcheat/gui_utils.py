"""
Utility dialogs for starcheat itself
"""

import sys, os
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

import save_file, assets, config
import qt_options, qt_openplayer

class OptionsDialog():
    def __init__(self, parent):
        # TODO: all the other dialogs should match this naming style
        self.dialog = QDialog(parent)
        self.ui = qt_options.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        # read the current config and prefill everything
        self.config = config.Config().read()
        self.ui.assets_folder.setText(self.config["assets_folder"])
        self.ui.player_folder.setText(self.config["player_folder"])
        # TODO: do backups
        self.ui.backup_folder.setText(self.config["backup_folder"])

        self.ui.assets_folder_button.clicked.connect(self.open_assets)
        self.ui.player_folder_button.clicked.connect(self.open_player)
        self.ui.backup_folder_button.clicked.connect(self.open_backup)
        self.ui.rebuild_button.clicked.connect(self.rebuild_db)

    def write(self):
        self.config["assets_folder"] = self.ui.assets_folder.text()
        self.config["player_folder"] = self.ui.player_folder.text()
        self.config["backup_folder"] = self.ui.backup_folder.text()
        config.Config().write(self.config)

    # TODO: windows doesn't like when these default to empty str
    def open_assets(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                               "Choose assets folder...",
                                               self.config["assets_folder"])
        if filename != "": self.ui.assets_folder.setText(filename)

    def open_player(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                               "Choose player save folder...",
                                               self.config["player_folder"])
        if filename != "": self.ui.player_folder.setText(filename)

    def open_backup(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                               "Choose backup location...",
                                               self.config["backup_folder"])
        if filename != "": self.ui.backup_folder.setText(filename)

    # TODO: this doesn't work in windows at all because of file locks
    #       need to make a function to drop and recreate the databases
    #       instead of just trashing the file
    def rebuild_db(self):
        self.write()
        if os.path.isfile(self.config["assets_db"]):
            os.remove(self.config["assets_db"])
        assets.AssetsDb()
        # TODO: i want some feedback here

# TODO: not sure the check for no players found is working? if user forgets
#       to set a player_folder on setup they will be forced to edit the ini
# TODO: put error messages in quick dialogs?
# TODO: support stuff like sorting by date (add column to table widget)
# TODO: disable the ok button until a valid item is selected
class CharacterSelectDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_openplayer.Ui_OpenPlayer()
        self.ui.setupUi(self.dialog)

        self.player_folder = config.Config().read()["player_folder"]

        self.dialog.rejected.connect(sys.exit)
        self.dialog.accepted.connect(self.accept)
        # bizarre, if i set this to self.accpet it just doesn't work...
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
        for root, dirs, files in os.walk(self.player_folder):
            for f in files:
                # is there need for regular expressions at this point?
                if f.endswith(".player"):
                    try:
                        player = save_file.PlayerSave(os.path.join(root, f))
                        players_found[player.get_name()] = player
                    except save_file.WrongSaveVer:
                        # ignores players that cannot be loaded
                        print("%s could not be loaded due to being incompatible with this version of starcheat." % (player.get_name(),))
                        # pop the player if it's incompatible
                        # I didn't expect the dictionary to still hold the player if execution hits the exception block
                        # I still don't expect it, hence the try. Just in case this is odd behavior.
                        try:
                            players_found.pop(player.get_name())
                        except KeyError:
                            pass

        self.players = players_found

    def populate(self):
        for player in self.players.keys():
            self.ui.player_list.addItem(player)

    def show(self):
        # quit if there are no players
        if len(self.players) == 0:
            # TODO: what if we popped up an options dialog?
            dialog = QMessageBox()
            msg = "No compatible save files found in: %s" % (self.player_folder)
            dialog.setText(msg)
            dialog.exec()
            sys.exit();
        else:
            self.dialog.exec()
