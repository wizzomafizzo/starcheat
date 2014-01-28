"""
Utility dialogs for starcheat itself
"""

import os, sys, platform
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QListWidgetItem
from PyQt5 import QtGui

from config import Config
from gui_common import preview_icon
import save_file, assets, logging
import qt_options, qt_openplayer, qt_about

# TODO: there are way too many html templates and message text in here now
# it should all be moved to a templates file or something

# TODO: we can use this for rebuild db but have to skip the sys.exit and
# file remove calls
def build_assets_db():
    assets_db_file = Config().read("assets_db")
    assets_db = assets.AssetsDb()

    logging.info("Indexing assets")
    dialog = QMessageBox()
    dialog.setText("starcheat will now build a database of Starbound assets.")
    dialog.setInformativeText("This can take a little while, please be patient.")
    dialog.setIcon(QMessageBox.Information)
    dialog.exec()

    missing_assets_text = """<html><body>
    <p>starcheat couldn't find any Starbound %s. You should double check:</p>
    <ol>
    <li>You selected the right Starbound folder.</li>
    <li>The assets you want to use have been unpacked. Instructions are
    <a href="https://github.com/wizzomafizzo/starcheat#unpacking-starbound-assets">here</a>
    and this includes vanilla Starbound assets.</li>
    </ol>
    <p>Once that's done, try restart starcheat to run the setup again.</p>
    </body></html>"""

    def bad_asset_dialog(asset_type=None):
        dialog = QMessageBox()
        dialog.setText("Unable to index assets.")
        if asset_type != None:
            dialog.setInformativeText(missing_assets_text % asset_type.lower())
        else:
            dialog.setInformativeText(missing_assets_text % "assets")
        dialog.setIcon(QMessageBox.Critical)
        dialog.exec()
        Config().remove_config()
        assets_db.db.close()
        os.remove(assets_db_file)
        sys.exit()

    assets_db.init_db()
    asset_types = ("Items", "Blueprints", "Species")
    for t in asset_types:
        try:
            asset_class = getattr(assets, t)()
            getattr(asset_class, "add_all_" + t.lower())()
        except FileNotFoundError:
            # catch anything that couldn't be skipped during index
            logging.exception("Asset folder not complete: %s", t)
            bad_asset_dialog(t)

        if getattr(asset_class, "get_" + t.lower() + "_total")() == 0:
            logging.error("Could not find any assets for: %s", t)
            bad_asset_dialog(t)

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
        dialog.setInformativeText("Please try it again and select your Starbound folder, which should contain the starbound.config.")
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
    return folder

def new_setup_dialog():
    """Run through an initial setup dialog for starcheat if it's required."""
    if os.path.isfile(Config().ini_file):
        if Config().has_key("config_version") and int(Config().read("config_version")) == Config().CONFIG_VERSION:
            return
        logging.info("rebuild config and assets_db (config_version mismatch)")
        dialog = QMessageBox()
        dialog.setText("Detected outdated starcheat config")
        dialog.setInformativeText("recreating config now...")
        dialog.setIcon(QMessageBox.Warning)
        dialog.exec()
        os.remove(Config().read("assets_db"))
        os.remove(Config().ini_file)

    logging.info("First setup dialog")

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

    # initial assets sanity check
    # better to check for an actual file. this should be a pretty safe bet
    unpack_test_file = os.path.join(starbound_folder, "assets", "species", "human.species")
    if not os.path.isfile(unpack_test_file):
        dialog = QMessageBox()
        dialog.setText("No unpacked assets found!")
        dialog.setInformativeText("""<html><body>
        <p>You need to unpack the Starcheat assets to use starcheat</p>
        <p>Do you want to extract the assets now?
        <i>(this requires ~410MB of disk space and takes up to 30 seconds)</i></p></body></html>""")
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

        os.system(unpack_cmd)

    # looks okay enough, let's go
    Config().create_config(starbound_folder)
    assets_db_file = Config().read("assets_db")
    # just to make sure
    if os.path.isfile(assets_db_file):
        os.remove(assets_db_file)
    build_assets_db()

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
        self.ui.total_indexed.setText(str(assets.AssetsDb().get_total_indexed()) + " indexed")

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

        try:
            assets.AssetsDb().rebuild_db()
        except FileNotFoundError:
            dialog = QMessageBox()
            dialog.setText("No assets found.")
            dialog.setInformativeText("Check the Starbound folder is set correctly.")
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec()
            return

        total = str(assets.AssetsDb().get_total_indexed())

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
        self.selected = None

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
