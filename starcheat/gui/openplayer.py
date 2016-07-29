"""
Open player save file dialog
"""

import os
import logging
import shutil
import datetime

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5 import QtGui

from PIL.ImageQt import ImageQt

import saves
import qt_openplayer
from config import Config
from gui.utils import new_setup_dialog


class PlayerWidget(QListWidgetItem):
    def __init__(self, text, name):
        QListWidgetItem.__init__(self, text)
        self.name = name


# TODO: support stuff like sorting by date (needs to be a table widget)
class CharacterSelectDialog():
    def __init__(self, parent, assets):
        self.dialog = QDialog(parent.window)
        self.ui = qt_openplayer.Ui_OpenPlayer()
        self.ui.setupUi(self.dialog)

        self.parent = parent

        if self.parent.players is not None:
            self.players = self.parent.players
        else:
            self.players = None

        self.player_folder = Config().read("player_folder")
        self.backup_folder = Config().read("backup_folder")
        self.selected = None
        self.assets = assets

        self.dialog.rejected.connect(self.dialog.close)
        self.dialog.accepted.connect(self.accept)
        self.ui.player_list.itemDoubleClicked.connect(self.dialog.accept)
        self.ui.trash_button.clicked.connect(self.trash_player)
        self.ui.refresh_button.clicked.connect(self.get_players)

        if self.players is None:
            self.get_players()
        else:
            self.populate()

        self.ui.player_list.setFocus()

    def accept(self):
        try:
            player = self.ui.player_list.currentItem().name
        except AttributeError:
            player = ""

        if player != "":
            self.selected = self.players[player]["player"]
            self.dialog.close()

    def get_players(self):
        players_found = {}

        try:
            file_list = os.listdir(self.player_folder)
        except FileNotFoundError:
            dialog = QMessageBox(self.dialog)
            dialog.setWindowTitle("Missing Player Folder")
            dialog.setText("Starbound player folder does not exist.")
            dialog.setInformativeText("You may need to run Starbound for the first time.")
            dialog.setStandardButtons(QMessageBox.Close)
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec()
            self.players = []
            return

        player_files = [x for x in file_list if x.endswith(".player")]

        total = 0
        progress = QProgressDialog("Reading player files...",
                                   None, 0, len(player_files),
                                   self.dialog)

        progress.setWindowTitle("Reading...")
        progress.setWindowModality(QtCore.Qt.ApplicationModal)
        progress.forceShow()
        progress.setValue(total)

        try:
            for f in player_files:
                try:
                    player = saves.PlayerSave(os.path.join(self.player_folder, f))
                    uuid = player.get_uuid()
                    preview = self.assets.species().render_player(player)
                    players_found[uuid] = {}
                    players_found[uuid]["player"] = player
                    players_found[uuid]["preview"] = preview
                    players_found[uuid]["playTime"] = player.get_play_time()
                except:
                    logging.exception("Save file not compatible: %s", f)
                total += 1
                progress.setValue(total)
        except FileNotFoundError:
            logging.exception("Could not open %s", self.player_folder)

        self.players = players_found
        self.populate()

    def populate(self):
        total = 0
        self.ui.player_list.clear()

        names = []
        for uuid in self.players.keys():
            try:
                names.append((uuid, self.players[uuid]["player"].get_name()))
            except TypeError:
                logging.exception("Could not read %s", uuid)

        for name in sorted(names, key=lambda x: x[1]):
            player = self.players[name[0]]["player"]
            preview = self.players[name[0]]["preview"]
            pixmap = QPixmap.fromImage(ImageQt(preview))
            played = datetime.timedelta(seconds=int(player.get_play_time()))
            list_item = PlayerWidget("%s [%s]" % (name[1], played), name[0])

            list_item.setIcon(QtGui.QIcon(pixmap))
            self.ui.player_list.addItem(list_item)

            total += 1

        self.ui.total_label.setText(str(total) + " total")
        self.ui.player_list.setCurrentRow(0)

    def show(self):
        # quit if there are no players
        if len(self.players) == 0:
            dialog = QMessageBox(self.dialog)
            dialog.setWindowTitle("No Player Files")
            dialog.setText("No player files detected. Reselect the Starbound folder?")
            dialog.setInformativeText(self.player_folder)
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            answer = dialog.exec()

            if answer == QMessageBox.Yes:
                Config().remove_config()
                new_setup_dialog(self.dialog)
                dialog = QMessageBox(self.dialog)
                dialog.setWindowTitle("Restart Starcheat")
                dialog.setText("Please restart Starcheat to see changes.")
                dialog.setIcon(QMessageBox.Information)
                dialog.exec()
        else:
            self.dialog.exec()

    def trash_player(self):
        """Move all player files to backup folder set in config file."""
        player = self.ui.player_list.currentItem().name
        uuid = self.players[player]["player"].get_uuid()
        player_files = []

        # are you sure?
        dialog = QMessageBox(self.dialog)
        dialog.setWindowTitle("Trash Player")
        dialog.setText("Trash this player?")
        dialog.setInformativeText("Player files will be moved to: %s" % self.backup_folder)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Cancel)
        dialog.setIcon(QMessageBox.Question)

        answer = dialog.exec()
        if answer != QMessageBox.Yes:
            return

        # find files
        for f in os.listdir(self.player_folder):
            if f.startswith(uuid):
                player_files.append(f)

        # move em
        for f in player_files:
            logging.info("Moving player file %s", f)
            try:
                # using shutil cause of a problem with os.rename not working
                # across filesystems. trust me to be the only person on earth
                # with that setup
                shutil.move(os.path.join(self.player_folder, f),
                            os.path.join(self.backup_folder, f))
            except OSError:
                logging.exception("Unable to move file %s", f)
                break

        self.get_players()
