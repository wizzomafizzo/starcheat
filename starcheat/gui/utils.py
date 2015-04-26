"""
Utility dialogs for starcheat itself
"""

import os
import sys
import hashlib
import webbrowser

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressDialog
from PyQt5 import QtCore

from urllib.request import urlopen
from urllib.error import URLError

import logging
import config
import qt_options
import qt_about
import qt_mods

from config import Config
from assets.core import Assets


def make_pak_hash():
    vanilla = os.path.join(Config().read("assets_folder"), "packed.pak")
    mods = Config().read("mods_folder")
    pak_list = [vanilla]
    timestamps = []

    for root, dirs, files in os.walk(mods):
        for f in files:
            if f.endswith(".modpak"):
                pak_list.append(os.path.join(root, f))

    for pak in pak_list:
        timestamps.append(str(os.stat(pak).st_mtime))

    final_hash = hashlib.md5()
    final_hash.update("_".join(timestamps).encode())

    return final_hash.hexdigest()


def build_assets_db(parent):
    assets_db_file = Config().read("assets_db")
    starbound_folder = Config().read("starbound_folder")
    assets_db = Assets(assets_db_file, starbound_folder)

    def bad_asset_dialog():
        dialog = QMessageBox(parent)
        dialog.setWindowTitle("No Assets Found")
        dialog.setText("Unable to index Starbound assets.")
        dialog.setInformativeText("Check that the Starbound folder was set correctly.")
        dialog.setIcon(QMessageBox.Critical)
        dialog.exec()
        assets_db.db.close()

    assets_db.init_db()
    asset_files = assets_db.find_assets()
    total = 0
    progress = QProgressDialog("Indexing Starbound assets...",
                               "Abort", 0, len(asset_files),
                               parent)
    progress.setWindowTitle("Indexing...")
    progress.setWindowModality(QtCore.Qt.ApplicationModal)
    progress.forceShow()
    progress.setValue(total)

    for i in assets_db.create_index():
        total += 1
        progress.setValue(total)
        if progress.wasCanceled():
            assets_db.db.close()
            return False

    progress.hide()
    if total == 0:
        bad_asset_dialog()
        return False
    else:
        Config().set("pak_hash", make_pak_hash())
        return True


def check_index_valid(parent):
    old_hash = Config().read("pak_hash")
    new_hash = make_pak_hash()
    if old_hash != new_hash:
        logging.info("Hashes don't match, updating index")
        dialog = QMessageBox(parent)
        dialog.setWindowTitle("Assets Out-of-date")
        dialog.setText("Starbound assets have been changed.")
        dialog.setInformativeText("Rebuild the starcheat assets index?")
        dialog.setIcon(QMessageBox.Question)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        answer = dialog.exec()
        if answer == QMessageBox.Yes:
            return build_assets_db(parent)
        else:
            return True
    else:
        return True


def save_modified_dialog(parent):
    """Display a prompt asking user what to do about a modified file. Return button clicked."""
    dialog = QMessageBox(parent)
    dialog.setWindowTitle("Save Changes?")
    dialog.setText("This player has been modified.")
    dialog.setInformativeText("Do you want to save your changes?")
    dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
    dialog.setDefaultButton(QMessageBox.Save)
    dialog.setIcon(QMessageBox.Question)
    return dialog.exec()


def select_starbound_folder_dialog(parent):
    folder = QFileDialog.getExistingDirectory(caption="Select Starbound Folder")
    while not os.path.isfile(os.path.join(folder, "assets", "packed.pak")):
        dialog = QMessageBox(parent)
        dialog.setWindowTitle("Wrong Starbound Folder")
        dialog.setText("This is not your Starbound folder!")
        dialog.setInformativeText("Please try again and select your Starbound folder, which should contain the assets folder.")
        dialog.setIcon(QMessageBox.Warning)
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        answer = dialog.exec()
        if answer == QMessageBox.Cancel:
            dialog = QMessageBox(parent)
            dialog.setWindowTitle("Starbound Not Installed")
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
        config_valid = (Config().has_key("config_version") and
                        int(Config().read("config_version")) == Config().CONFIG_VERSION)

        if not config_valid:
            logging.info("rebuild config and assets_db (config_version mismatch)")
            dialog = QMessageBox(parent)
            dialog.setWindowModality(QtCore.Qt.WindowModal)
            dialog.setWindowTitle("Config Out-of-date")
            dialog.setText("Your starcheat settings are outdated.")
            dialog.setInformativeText("A new config file and assets index will be created...")
            dialog.setIcon(QMessageBox.Warning)
            dialog.exec()
        else:
            vanilla_pak = os.path.join(Config().read("starbound_folder"), "assets", "packed.pak")
            if os.path.isfile(vanilla_pak):
                return True
            else:
                logging.error("No vanilla pak, Starbound folder may be wrong")

        os.remove(Config().ini_file)

    # Starbound folder settings
    starbound_folder = Config().detect_starbound_folder()
    if starbound_folder == "":
        dialog = QMessageBox(parent)
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        dialog.setWindowTitle("Starbound Not Found")
        dialog.setText("Unable to detect the main Starbound folder.")
        dialog.setInformativeText("Please select it in the next dialog.")
        dialog.setIcon(QMessageBox.Warning)
        dialog.exec()
        starbound_folder = select_starbound_folder_dialog(parent)
    else:
        dialog = QMessageBox(parent)
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        dialog.setWindowTitle("Starbound Folder Found")
        dialog.setText("Detected the following folder as the location of Starbound. Is this correct?")
        dialog.setInformativeText(starbound_folder)
        dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        dialog.setIcon(QMessageBox.Question)
        answer = dialog.exec()
        if answer == QMessageBox.No:
            starbound_folder = select_starbound_folder_dialog(parent)

    # looks okay enough, let's go
    Config().create_config(starbound_folder)

    if not build_assets_db(parent):
        os.remove(Config().ini_file)
        return False
    else:
        return True


def update_check_worker(result):
    if Config().has_key("check_updates"):
        check_updates = Config().read("check_updates") == "yes"
    else:
        check_updates = True

    if not check_updates:
        logging.info("Skipping update check")
        return

    logging.info("Checking for updates")
    try:
        latest_tag = urlopen("https://github.com/wizzomafizzo/starcheat/releases/latest").geturl()
        if latest_tag.find("github.com/wizzomafizzo/starcheat/releases") >= 0:
            if not latest_tag.endswith("tag/" + config.STARCHEAT_VERSION_TAG):
                result[0] = latest_tag
                logging.info("update check: found new starcheat version")
                return
        else:
            logging.info("update check: skipping update check because of failed redirect")
    except URLError:
        logging.info("update check: skipping update check because of no internet connection")
    result[0] = False


def update_check_dialog(parent, latest_tag):
    dialog = QMessageBox(parent)
    dialog.setWindowModality(QtCore.Qt.WindowModal)
    dialog.setWindowTitle("Outdated starcheat Version")
    dialog.setText("A new version of starcheat is available! Do you want to update now?")
    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    dialog.setDefaultButton(QMessageBox.Yes)
    dialog.setIcon(QMessageBox.Question)
    if dialog.exec() == QMessageBox.Yes:
        webbrowser.open(latest_tag, 2)
        sys.exit(0)


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
        self.db = Assets(assets_db_file, starbound_folder)

        self.config = Config()
        self.current_folder = self.config.read("starbound_folder")

        # read the current config and prefill everything
        self.ui.starbound_folder.setText(self.config.read("starbound_folder"))
        self.ui.total_indexed.setText(str(self.db.total_indexed()) + " indexed")
        self.ui.update_checkbox.setChecked(self.config.read("check_updates") == "yes")

        self.ui.starbound_folder_button.clicked.connect(self.open_starbound)
        self.ui.rebuild_button.clicked.connect(self.rebuild_db)
        self.ui.update_checkbox.toggled.connect(self.write_update_check)

    def write(self):
        starbound_folder = self.ui.starbound_folder.text()
        if self.current_folder != starbound_folder:
            self.config.create_config(starbound_folder)

    def write_update_check(self):
        do_check = self.ui.update_checkbox.isChecked()
        # configparser has a getbool method but it's not much smarter than this
        # and will complicate the config class. move this to a separate method
        # if we need more bools
        if do_check:
            conf_val = "yes"
        else:
            conf_val = "no"
        self.config.set("check_updates", conf_val)

    def open_starbound(self):
        filename = QFileDialog.getExistingDirectory(self.dialog,
                                                    "Select Starbound Folder",
                                                    self.config.read("starbound_folder"))
        if filename != "":
            self.ui.starbound_folder.setText(filename)

    def rebuild_db(self):
        self.write()

        def bad_asset_dialog():
            dialog = QMessageBox(self.dialog)
            dialog.setWindowTitle("No Starbound Assets")
            dialog.setText("No Starbound assets could be found.")
            dialog.setInformativeText("The Starbound folder option might be set wrong.")
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec()

        try:
            rebuild = build_assets_db(self.dialog)
        except FileNotFoundError:
            rebuild = False

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.db = Assets(assets_db_file, starbound_folder)
        total = str(self.db.total_indexed())

        if not rebuild or total == 0:
            bad_asset_dialog()
        else:
            dialog = QMessageBox(self.dialog)
            dialog.setWindowTitle("Finished Indexing")
            dialog.setText("Finished indexing Starbound assets.")
            dialog.setInformativeText("Found %s assets." % total)
            dialog.setIcon(QMessageBox.Information)
            dialog.exec()

        self.ui.total_indexed.setText(total + " indexed")


class ModsDialog():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_mods.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        starbound_folder = Config().read("starbound_folder")
        self.assets = Assets(Config().read("assets_db"),
                             starbound_folder)

        mods = self.assets.get_mods()
        self.ui.mods_total.setText(str(len(mods))+" total")
        for mod in mods:
            self.ui.mods_list.addItem(mod)

        self.ui.export_button.clicked.connect(self.export_list)

    def export_list(self):
        data = ""
        for mod in self.assets.get_mods():
            data += mod + "\n"

        filename = QFileDialog.getSaveFileName(self.dialog,
                                               "Export Mod List As",
                                               filter="Text (*.txt);;All Files (*)")

        if filename[0] != "":
            json_file = open(filename[0], "w")
            json_file.write(data)
            json_file.close()
