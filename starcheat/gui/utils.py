"""
Utility dialogs for starcheat itself
"""

import os, sys, platform, subprocess, shutil
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QListWidgetItem, QProgressDialog
from PyQt5 import QtGui, QtCore

import saves, assets, logging, config
import qt_options, qt_openplayer, qt_about, qt_mods
from config import Config
from gui.common import preview_icon

# TODO: there are way too many html templates and message text in here now
# it should all be moved to a templates file or something

# TODO: we can use this for rebuild db but have to skip the sys.exit and
# file remove calls
def build_assets_db(parent):
    assets_db_file = Config().read("assets_db")
    starbound_folder = Config().read("starbound_folder")
    assets_db = assets.Assets(assets_db_file, starbound_folder)

    missing_assets_text = """<html><body>
    <p>starcheat couldn't find any Starbound assets. You should double check:</p>
    <ol>
    <li>You selected the right Starbound folder.</li>
    <li>The assets you want to use have been unpacked. Instructions are
    <a href="https://github.com/wizzomafizzo/starcheat#unpacking-starbound-assets">here</a>
    and this includes vanilla Starbound assets.</li>
    </ol>
    <p>Once that's done, try restart starcheat to run the setup again.</p>
    </body></html>"""

    def bad_asset_dialog():
        dialog = QMessageBox()
        dialog.setText("Unable to index assets.")
        dialog.setInformativeText(missing_assets_text)
        dialog.setIcon(QMessageBox.Critical)
        dialog.exec()
        assets_db.db.close()
        os.remove(assets_db_file)

    assets_db.init_db()
    asset_files = assets_db.find_assets()
    total = 0
    progress = QProgressDialog("Indexing Starbound assets...",
                               "Cancel", 0, len(asset_files),
                               parent)
    progress.setWindowModality(QtCore.Qt.ApplicationModal)
    progress.forceShow()

    for i in assets_db.create_index():
        total += 1
        progress.setValue(total)
        if progress.wasCanceled():
            assets_db.db.close()
            os.remove(assets_db_file)
            return False

    progress.hide()
    if total == 0:
        bad_asset_dialog()
        return False
    else:
        return True

def save_modified_dialog():
    """Display a prompt asking user what to do about a modified file. Return button clicked."""
    dialog = QMessageBox()
    dialog.setText("This player has been modified.")
    dialog.setInformativeText("Do you want to save your changes?")
    dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
    dialog.setDefaultButton(QMessageBox.Save)
    dialog.setIcon(QMessageBox.Question)
    return dialog.exec()

def select_starbound_folder_dialog():
    folder = QFileDialog.getExistingDirectory(caption="Select Starbound Folder")
    while not os.path.isfile(os.path.join(folder, "starbound.config")):
        dialog = QMessageBox()
        dialog.setText("This is not your Starbound folder!")
        dialog.setInformativeText("Please try again and select your Starbound folder, which should contain the starbound.config file.")
        dialog.setIcon(QMessageBox.Warning)
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        answer = dialog.exec()
        if answer == QMessageBox.Cancel:
            dialog = QMessageBox()
            dialog.setIcon(QMessageBox.Critical)
            dialog.setText("starcheat needs Starbound installed to work.")
            dialog.exec()
            Config().remove_config()
            sys.exit()
        folder = QFileDialog.getExistingDirectory(caption="Select Starbound Folder")
    return os.path.normpath(folder)

def new_setup_dialog(parent):
    """Run through an initial setup dialog for starcheat if it's required."""

    logging.info("First setup dialog")

    if os.path.isfile(Config().ini_file):
        if not (Config().has_key("config_version") and int(Config().read("config_version")) == Config().CONFIG_VERSION):
            logging.info("rebuild config and assets_db (config_version mismatch)")
            dialog = QMessageBox()
            dialog.setText("Your starcheat settings are outdated.")
            dialog.setInformativeText("A new config file and assets index will be created...")
            dialog.setIcon(QMessageBox.Warning)
            dialog.exec()
        else:
            return True
        os.remove(Config().ini_file)

    # Starbound folder settings
    starbound_folder = Config().detect_starbound_folder()
    if starbound_folder == "":
        dialog = QMessageBox()
        dialog.setText("Unable to detect the main Starbound folder.")
        dialog.setInformativeText("Please select it in the next dialog.")
        dialog.setIcon(QMessageBox.Warning)
        dialog.exec()
        starbound_folder = select_starbound_folder_dialog()
    else:
        dialog = QMessageBox()
        dialog.setText("Detected the following folder as the location of Starbound. Is this correct?")
        dialog.setInformativeText(starbound_folder)
        dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        dialog.setIcon(QMessageBox.Question)
        answer = dialog.exec()
        if answer == QMessageBox.No:
            starbound_folder = select_starbound_folder_dialog()

    # looks okay enough, let's go
    Config().create_config(starbound_folder)
    assets_db_file = Config().read("assets_db")

    if not build_assets_db(parent):
        os.remove(Config().ini_file)
        return False
    else:
        return True

def unpack_assets():
    unpack_test_file = os.path.join(starbound_folder, "assets", "species", "human.species")
    dialog = QMessageBox()
    dialog.setText("No unpacked assets found!")
    dialog.setInformativeText("""<html><body>
    <p>starcheat needs to unpack your Starbound assets to work. This only happens once.</p>
    <p>Do you want to unpack the assets now?
    <i>(this requires ~410MB of disk space and takes 1-5 mins)</i></p></body></html>""")
    dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    dialog.setIcon(QMessageBox.Question)
    answer = dialog.exec()
    if answer == QMessageBox.No:
        sys.exit()

    if platform.system() == "Windows":
        asset_unpacker = os.path.join(starbound_folder, "win32", "asset_unpacker.exe")
    elif platform.system() == "Darwin":
        asset_unpacker = os.path.join(starbound_folder, "Starbound.app", "Contents",
                                      "MacOS", "asset_unpacker")
    elif sys.maxsize > 2**32: # 64-bit Linux
        asset_unpacker = os.path.join(starbound_folder, "linux64", "asset_unpacker")
    else: # 32-bit Linux
        asset_unpacker = os.path.join(starbound_folder, "linux32", "asset_unpacker")

    unpack_cmd = '"{0}" "{1}" "{2}"'.format(asset_unpacker,
                                            os.path.join(starbound_folder, "assets", "packed.pak"),
                                            os.path.join(starbound_folder, "assets"))
    # just so the cmd window isn't totally empty
    print("Unpacking Starbound vanilla assets...")
    subprocess.call(unpack_cmd, shell=True)

    if not os.path.isfile(unpack_test_file):
        dialog = QMessageBox()
        dialog.setText("Unable to unpack the Starbound assets.")
        dialog.setInformativeText("""<html><body>Please follow
        <a href="https://github.com/wizzomafizzo/starcheat#unpacking-starbound-assets">this guide</a>
        to do it yourself.</body></html>""")
        dialog.setIcon(QMessageBox.Warning)
        dialog.exec()
        sys.exit()

class AboutDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_about.Ui_Dialog()
        self.ui.setupUi(self.dialog)
        set_ver = self.ui.header_info.text().replace("STARCHEAT_VERSION",
                                                     config.STARCHEAT_VERSION)
        self.ui.header_info.setText(set_ver)

class OptionsDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_options.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.db = assets.Assets(assets_db_file, starbound_folder)

        self.config = Config()

        # read the current config and prefill everything
        self.ui.starbound_folder.setText(self.config.read("starbound_folder"))
        self.ui.total_indexed.setText(str(self.db.total_indexed()) + " indexed")

        self.ui.starbound_folder_button.clicked.connect(self.open_starbound)
        self.ui.rebuild_button.clicked.connect(self.rebuild_db)

        self.ui.buttonBox.accepted.connect(self.write)

    def write(self):
        starbound_folder = self.ui.starbound_folder.text()
        self.config.set("starbound_folder", starbound_folder)
        # TODO: remove these settings completely at some point
        self.config.set("assets_folder", os.path.join(starbound_folder, "assets"))
        self.config.set("player_folder", os.path.join(starbound_folder, "player"))

    def open_starbound(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                                    "Select Starbound Folder",
                                                    self.config.read("starbound_folder"))
        if filename != "":
            self.ui.starbound_folder.setText(filename)

    def rebuild_db(self):
        self.write()

        def bad_asset_dialog():
            dialog = QMessageBox()
            dialog.setText("No Starbound assets could be found.")
            dialog.setInformativeText("The Starbound folder option might be set wrong.")
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec()

        try:
            rebuild = build_assets_db(self.dialog)
        except FileNotFoundError:
            bad_asset_dialog()

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.db = assets.Assets(assets_db_file, starbound_folder)
        total = str(self.db.total_indexed())

        if not rebuild or total == 0:
            bad_asset_dialog()
        else:
            dialog = QMessageBox()
            dialog.setText("Finished indexing Starbound assets.")
            dialog.setInformativeText("Found %s assets." % total)
            dialog.setIcon(QMessageBox.Information)
            dialog.exec()

        self.ui.total_indexed.setText(total + " indexed")

# TODO: support stuff like sorting by date (needs to be a table widget)
class CharacterSelectDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_openplayer.Ui_OpenPlayer()
        self.ui.setupUi(self.dialog)

        self.player_folder = Config().read("player_folder")
        self.backup_folder = Config().read("backup_folder")
        self.selected = None

        self.dialog.rejected.connect(self.dialog.close)
        self.dialog.accepted.connect(self.accept)
        # bizarre, if i set this to self.accept it just doesn't work...
        self.ui.player_list.itemDoubleClicked.connect(self.dialog.accept)
        self.ui.trash_button.clicked.connect(self.trash_player)

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
                        player = saves.PlayerSave(os.path.join(self.player_folder, f))
                        players_found[player.get_name()] = player
                    except saves.WrongSaveVer:
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

    def show(self):
        # quit if there are no players
        if len(self.players) == 0:
            dialog = QMessageBox()
            dialog.setText("No compatible save files found in:")
            dialog.setInformativeText(self.player_folder)
            dialog.setIcon(QMessageBox.Warning)
            dialog.exec()
        else:
            self.dialog.exec()

    def trash_player(self):
        """Move all player files to backup folder set in config file."""
        player = self.ui.player_list.currentItem().text()
        uuid = self.players[player].get_uuid()
        player_files = []

        # are you sure?
        dialog = QMessageBox()
        dialog.setText("Trash this player?")
        dialog.setInformativeText("Player files will be backed up to: %s" % self.backup_folder)
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
        self.populate()

class ModsDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_mods.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        starbound_folder = Config().read("starbound_folder")
        self.assets = assets.Assets(Config().read("assets_db"),
                                    starbound_folder)

        mods = self.assets.get_mods()
        self.ui.mods_total.setText(str(len(mods))+" total")
        for mod in mods:
            self.ui.mods_list.addItem(mod)
