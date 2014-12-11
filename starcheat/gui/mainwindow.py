"""
Main application window for starcheat GUI
"""

import sys
import logging
import json

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMenu, QAction
from PyQt5.QtGui import QPixmap, QCursor
from PIL.ImageQt import ImageQt

import saves, assets, qt_mainwindow
from config import Config
from gui.common import ItemWidget, empty_slot
from gui.utils import CharacterSelectDialog, OptionsDialog, AboutDialog, ModsDialog
from gui.utils import save_modified_dialog, new_setup_dialog
from gui.itemedit import ItemEdit, ImageBrowser
from gui.blueprints import BlueprintLib
from gui.itembrowser import ItemBrowser
from gui.appearance import Appearance
from gui.techs import Techs


class StarcheatMainWindow(QMainWindow):
    """Overrides closeEvent on the main window to allow "want to save changes?" dialog"""
    def __init__(self, parent):
        super(QMainWindow, self).__init__()
        self.parent = parent

    def closeEvent(self, event):
        if not self.isWindowModified():
            event.accept()
            return

        button = save_modified_dialog(self.parent.window)
        if button == QMessageBox.Save:
            self.parent.save()
            event.accept()
        elif button == QMessageBox.Cancel:
            event.ignore()
        elif button == QMessageBox.Discard:
            event.accept()


class MainWindow():
    def __init__(self):
        """Display the main starcheat window."""
        self.app = QApplication(sys.argv)
        self.window = StarcheatMainWindow(self)
        self.ui = qt_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self.window)

        logging.info("Main window init")

        # launch first setup if we need to
        if not new_setup_dialog(self.window):
            logging.warning("Config/index creation failed")
            return
        logging.info("Starbound folder: %s", Config().read("starbound_folder"))

        self.filename = None

        logging.debug("Loading assets database")
        self.assets = assets.Assets(Config().read("assets_db"),
                                    Config().read("starbound_folder"))

        self.items = self.assets.items()

        self.item_browser = None
        # remember the last selected item browser category
        self.remember_browser = "<all>"
        self.options_dialog = None

        # connect action menu
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionReload.triggered.connect(self.reload)
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionQuit.triggered.connect(self.app.closeAllWindows)
        self.ui.actionOptions.triggered.connect(self.new_options_dialog)
        self.ui.actionItemBrowser.triggered.connect(self.new_item_browser)
        self.ui.actionAbout.triggered.connect(self.new_about_dialog)
        self.ui.actionExport.triggered.connect(self.export_save)
        self.ui.actionExportJSON.triggered.connect(self.export_json)
        self.ui.actionImportJSON.triggered.connect(self.import_json)
        self.ui.actionMods.triggered.connect(self.new_mods_dialog)
        self.ui.actionImageBrowser.triggered.connect(self.new_image_browser_dialog)

        # populate species combobox
        for species in self.assets.species().get_species_list():
            self.ui.race.addItem(species)

        # populate game mode combobox
        for mode in self.assets.player().mode_types.values():
            self.ui.game_mode.addItem(mode)

        def bag_context(widget, name):
            widget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

            item_edit = getattr(self, "new_" + b + "_item_edit")
            sortable = ("main_bag", "action_bar", "tile_bag")
            clearable = ("wieldable", "action_bar", "essentials")

            edit_action = QAction("Edit...", widget)
            edit_action.triggered.connect(item_edit)
            widget.addAction(edit_action)
            trash_action = QAction("Trash", widget)
            trash_slot = lambda: self.trash_slot(self.window, widget, True)
            trash_action.triggered.connect(trash_slot)
            widget.addAction(trash_action)
            sep_action = QAction(widget)

            if name in sortable or name in clearable:
                sep_action.setSeparator(True)
                widget.addAction(sep_action)
                if name in clearable:
                    clear_action = QAction("Clear Held Items", widget)
                    clear_action.triggered.connect(self.clear_held_slots)
                    widget.addAction(clear_action)
                if name in sortable:
                    sort_action = QAction("Sort Items...", widget)
                    sort_action.setEnabled(False)
                    widget.addAction(sort_action)

        # set up bag tables
        self.last_bag = None
        bags = ("wieldable", "head", "chest", "legs", "back", "main_bag",
                "action_bar", "tile_bag", "essentials", "mouse")
        for b in bags:
            logging.debug("Setting up %s bag", b)
            item_edit = getattr(self, "new_" + b + "_item_edit")
            getattr(self.ui, b).cellDoubleClicked.connect(item_edit)
            getattr(self.ui, b).cellChanged.connect(self.set_edited)

            bag_context(getattr(self.ui, b), b)

            # TODO: still issues with drag drop between tables
            getattr(self.ui, b).setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.ui.blueprints_button.clicked.connect(self.new_blueprint_edit)
        self.ui.appearance_button.clicked.connect(self.new_appearance_dialog)
        self.ui.techs_button.clicked.connect(self.new_techs_dialog)

        self.ui.name.textChanged.connect(self.set_name)
        self.ui.race.currentTextChanged.connect(self.update_species)
        self.ui.male.clicked.connect(self.set_gender)
        self.ui.female.clicked.connect(self.set_gender)
        self.ui.description.textChanged.connect(self.set_description)
        self.ui.pixels.valueChanged.connect(self.set_pixels)
        self.ui.game_mode.currentTextChanged.connect(self.set_game_mode)

        # set up stat signals
        self.ui.health.valueChanged.connect(lambda: self.set_stat_slider("health"))
        self.ui.energy.valueChanged.connect(lambda: self.set_stat_slider("energy"))
        self.ui.health_button.clicked.connect(lambda: self.max_stat("health"))
        self.ui.energy_button.clicked.connect(lambda: self.max_stat("energy"))

        # launch open file dialog
        self.player = None
        logging.debug("Open file dialog")
        open_player = self.open_file()
        # we *need* at least an initial save file
        if not open_player:
            logging.warning("No player file selected")
            return

        self.ui.name.setFocus()
        self.window.setWindowModified(False)

        logging.debug("Showing main window")
        self.window.show()
        sys.exit(self.app.exec_())

    def update(self):
        """Update all GUI widgets with values from PlayerSave instance."""
        logging.info("Updating main window")
        # uuid / save version
        self.ui.uuid_label.setText(self.player.get_uuid())
        self.ui.ver_label.setText(self.player.get_header())
        # name
        self.ui.name.setText(self.player.get_name())
        # race
        self.ui.race.setCurrentText(self.player.get_race(pretty=True))
        # pixels
        try:
            self.ui.pixels.setValue(self.player.get_pixels())
        except TypeError:
            logging.exception("Unable to set pixels widget")
        # description
        self.ui.description.setPlainText(self.player.get_description())
        # gender
        getattr(self.ui, self.player.get_gender()).toggle()
        # game mode
        game_mode = self.player.get_game_mode()
        try:
            self.ui.game_mode.setCurrentText(self.assets.player().mode_types[game_mode])
        except KeyError:
            logging.exception("No game mode set on player")

        # stats
        self.update_stat("health")
        self.update_stat("energy")

        # equipment
        equip_bags = "head", "chest", "legs", "back"
        for bag in equip_bags:
            logging.debug("Updating %s", bag)
            # TODO: hide meta attributes in saves.py?
            items = []
            for x in getattr(self.player, "get_" + bag)():
                if x is not None:
                    items.append(ItemWidget(x["__content"], self.assets))
                else:
                    items.append(ItemWidget(None, self.assets))

            getattr(self.ui, bag).setItem(0, 0, items[0])
            getattr(self.ui, bag).setItem(0, 1, items[1])

        # wielded
        self.update_bag("wieldable")

        # bags
        self.update_bag("main_bag")
        self.update_bag("tile_bag")
        self.update_bag("action_bar")
        self.update_bag("essentials")
        self.update_bag("mouse")

        self.update_player_preview()

    def save(self):
        """Update internal player dict with GUI values and export to file."""
        logging.info("Saving player file %s", self.player.filename)
        self.set_bags()
        # save and show status
        logging.info("Writing file to disk")
        logging.debug(self.player.data)
        self.player.export_save(self.player.filename)
        self.ui.statusbar.showMessage("Saved " + self.player.filename, 3000)
        self.window.setWindowModified(False)

    def new_item_edit(self, bag):
        """Display a new item edit dialog using the select cell in a given bag."""
        logging.debug("New item edit dialog")
        row = bag.currentRow()
        column = bag.currentColumn()
        current = bag.currentItem()
        # TODO: move to separate function?
        item = {
            "name": "",
            "count": 1,
            "parameters": {}
        }
        # cells don't retain ItemSlot widget when they've been dragged away
        if type(current) is QTableWidgetItem or current.item is None:
            pass
        else:
            item.update(current.item)

        item_edit = ItemEdit(self.window, item,
                             self.player, self.remember_browser)

        def update_slot():
            logging.debug("Writing changes to slot")
            try:
                new_slot = ItemWidget(item_edit.get_item(), self.assets)
                if new_slot.item["name"] != "":
                    bag.setItem(row, column, new_slot)
                    self.remember_browser = item_edit.remember_browser
                    self.set_edited()
            except TypeError:
                dialog = QMessageBox(item_edit.dialog)
                dialog.setWindowTitle("Invalid Item ID")
                dialog.setText("That item ID does not exist in the Starbound assets.")
                dialog.setStandardButtons(QMessageBox.Close)
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec()

        trash_slot = lambda: self.trash_slot(item_edit.dialog, bag)

        item_edit.dialog.accepted.connect(update_slot)
        item_edit.ui.trash_button.clicked.connect(trash_slot)
        item_edit.dialog.exec()

    def trash_slot(self, dialog, bag, standalone=False):
        row = bag.currentRow()
        column = bag.currentColumn()
        dialog = QMessageBox(dialog)
        dialog.setWindowTitle("Trash Item")
        dialog.setText("Are you sure?")
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)
        dialog.setIcon(QMessageBox.Question)
        if dialog.exec() == QMessageBox.Yes:
            bag.setItem(row, column, empty_slot())
            if not standalone:
                dialog.close()
            self.set_edited()

    def set_edited(self):
        self.window.setWindowModified(True)

    def clear_held_slots(self):
        self.player.clear_held_slots()
        self.ui.statusbar.showMessage("All held items have been cleared", 3000)

    def new_blueprint_edit(self):
        """Launch a new blueprint management dialog."""
        logging.debug("New blueprint dialog")
        blueprint_lib = BlueprintLib(self.window, self.player.get_blueprints())

        def update_blueprints():
            logging.debug("Writing blueprints")
            self.player.set_blueprints(blueprint_lib.get_known_list())
            blueprint_lib.dialog.close()
            self.set_edited()

        blueprint_lib.ui.buttonBox.rejected.connect(update_blueprints)
        blueprint_lib.dialog.exec()

    def new_item_browser(self):
        """Launch a standalone item browser dialog that does write any changes."""
        self.item_browser = ItemBrowser(self.window, True)
        self.item_browser.dialog.show()

    def new_options_dialog(self):
        """Launch a new options config dialog."""
        logging.debug("New options dialog")
        self.options_dialog = OptionsDialog(self.window)

        def write_options():
            logging.info("Writing options to disk")
            # TODO: reload icons on asset update?
            self.ui.statusbar.showMessage("Options have been updated", 3000)

        self.options_dialog.dialog.accepted.connect(write_options)
        self.options_dialog.dialog.exec()

    def new_about_dialog(self):
        """Launch a new about dialog."""
        about_dialog = AboutDialog(self.window)
        about_dialog.dialog.exec()

    def new_appearance_dialog(self):
        appearance_dialog = Appearance(self)
        appearance_dialog.dialog.exec()
        appearance_dialog.write_appearance_values()
        self.update_player_preview()

    def new_techs_dialog(self):
        techs_dialog = Techs(self)
        techs_dialog.dialog.rejected.connect(techs_dialog.write_techs)
        techs_dialog.dialog.exec()

    def new_mods_dialog(self):
        mods_dialog = ModsDialog(self.window)
        mods_dialog.dialog.exec()

    def new_image_browser_dialog(self):
        self.image_browser = ImageBrowser(self.window, self.assets)
        self.image_browser.dialog.show()

    def reload(self):
        """Reload the currently open save file and update GUI values."""
        logging.info("Reloading file %s", self.player.filename)
        self.player = saves.PlayerSave(self.player.filename)
        self.update()
        self.ui.statusbar.showMessage("Reloaded " + self.player.filename, 3000)
        self.window.setWindowModified(False)

    def open_file(self):
        """Display open file dialog and load selected save."""
        if self.window.isWindowModified():
            button = save_modified_dialog(self.window)
            if button == QMessageBox.Cancel:
                return False
            elif button == QMessageBox.Save:
                self.save()

        character_select = CharacterSelectDialog(self.window)
        character_select.show()

        if character_select.selected is None:
            logging.warning("No player selected")
            return False
        else:
            self.player = character_select.selected

        self.update()

        self.window.setWindowTitle("starcheat - " + self.player.get_name() + "[*]")
        self.ui.statusbar.showMessage("Opened " + self.player.filename, 3000)
        self.window.setWindowModified(False)
        return True

    def export_save(self):
        """Save a copy of the current player file to another location.
        Doesn't change the current filename."""
        filename = QFileDialog.getSaveFileName(self.window,
                                               "Export Save File As")
        if filename[0] != "":
            self.set_bags()
            self.player.export_save(filename[0])
            self.ui.statusbar.showMessage("Exported save file to " + filename[0], 3000)

    def export_json(self):
        """Export player entity as json."""
        self.set_bags()
        entity = self.player.entity
        json_data = json.dumps(entity, sort_keys=True,
                               indent=4, separators=(',', ': '))
        filename = QFileDialog.getSaveFileName(self.window,
                                               "Export JSON File As")
        if filename[0] != "":
            json_file = open(filename[0], "w")
            json_file.write(json_data)
            json_file.close()
            self.ui.statusbar.showMessage("Exported JSON file to " + filename[0], 3000)

    def import_json(self):
        """Import an exported JSON player entity and merge/update with open player."""
        filename = QFileDialog.getOpenFileName(self.window,
                                               "Import JSON Player File")

        if filename[0] == "":
            logging.debug("No player file selected to import")
            return

        try:
            player_data = json.load(open(filename[0], "r"))
            self.player.entity.update(player_data)
            self.update()
            self.ui.statusbar.showMessage("Imported player file " + filename[0], 3000)
        except:
            logging.exception("Error parsing player: %s", filename[0])
            self.ui.statusbar.showMessage("Error importing player, see starcheat log for details", 3000)

    def get_gender(self):
        if self.ui.male.isChecked():
            return "male"
        else:
            return "female"

    def get_bag(self, name):
        """Return the entire contents of a given non-equipment bag as raw values."""
        logging.debug("Getting %s contents", name)
        row = column = 0
        bag = getattr(self.player, "get_" + name)()

        for i in range(len(bag)):
            item = getattr(self.ui, name).item(row, column)
            empty_item = (item is None or
                          type(item) is QTableWidgetItem or
                          item.item is None)
            if empty_item:
                item = None
            else:
                widget = item.item
                item = saves.new_item(widget["name"],
                                      widget["count"],
                                      widget["parameters"])

            bag[i] = item

            # so far all non-equip bags are 10 cols long
            column += 1
            if (column % 10) == 0:
                row += 1
                column = 0

        return bag

    def get_equip(self, name):
        """Return the raw values of both slots in a given equipment bag."""
        logging.debug("Getting %s contents", name)
        equip = getattr(self.ui, name)
        main_cell = equip.item(0, 0)
        glamor_cell = equip.item(0, 1)

        # when you drag itemwidgets around the cell will become empty so just
        # pretend it had an empty slot value
        empty_main = (main_cell is None or
                      type(main_cell) is QTableWidgetItem or
                      main_cell.item is None)
        if empty_main:
            main = None
        else:
            widget = main_cell.item
            main = saves.new_item(widget["name"],
                                  widget["count"],
                                  widget["parameters"])

        empty_glamor = (glamor_cell is None or
                        type(glamor_cell) is QTableWidgetItem or
                        glamor_cell.item is None)
        if empty_glamor:
            glamor = None
        else:
            widget = glamor_cell.item
            glamor = saves.new_item(widget["name"],
                                    widget["count"],
                                    widget["parameters"])

        return main, glamor

    def update_bag(self, bag_name):
        """Set the entire contents of any given bag with ItemWidgets based off player data."""
        logging.debug("Updating %s contents", bag_name)
        row = column = 0
        bag = getattr(self.player, "get_" + bag_name)()

        for slot in range(len(bag)):
            item = bag[slot]
            if item is not None:
                widget = ItemWidget(bag[slot]["__content"], self.assets)
            else:
                widget = ItemWidget(None, self.assets)

            getattr(self.ui, bag_name).setItem(row, column, widget)

            column += 1
            if (column % 10) == 0:
                row += 1
                column = 0

    def update_player_preview(self):
        try:
            image = self.assets.species().render_player(self.player)
            pixmap = QPixmap.fromImage(ImageQt(image))
        except (OSError, TypeError, AttributeError):
            # TODO: more specific error handling. may as well except all errors
            # at this point jeez
            logging.exception("Couldn't load species images")
            pixmap = QPixmap()

        self.ui.player_preview.setPixmap(pixmap)
        self.window.setWindowModified(True)

    def update_species(self):
        species = self.ui.race.currentText()
        if self.player.get_race(pretty=True) == species:
            # don't overwrite appearance values if it didn't really change
            return
        self.player.set_race(species)
        defaults = self.assets.species().get_default_colors(species)
        for key in defaults:
            getattr(self.player, "set_%s_directives" % key)(defaults[key])
        self.update_player_preview()
        self.window.setWindowModified(True)

    def set_pixels(self):
        self.player.set_pixels(self.ui.pixels.value())
        self.set_edited()

    def set_name(self):
        self.player.set_name(self.ui.name.text())
        self.set_edited()

    def set_description(self):
        self.player.set_description(self.ui.description.toPlainText())
        self.set_edited()

    def set_gender(self):
        self.player.set_gender(self.get_gender())
        self.update_player_preview()
        self.set_edited()

    def set_game_mode(self):
        self.player.set_game_mode(self.assets.player().get_mode_type(self.ui.game_mode.currentText()))
        self.set_edited()

    def set_bags(self):
        # this function mostly just exist to work around the bug of
        # dragndrop not updating player entity. this requires the table view
        # equipment
        equip_bags = "head", "chest", "legs", "back"
        for b in equip_bags:
            bag = self.get_equip(b)
            getattr(self.player, "set_" + b)(bag[0], bag[1])
        # bags
        bags = "wieldable", "main_bag", "tile_bag", "action_bar", "essentials", "mouse"
        for b in bags:
            getattr(self.player, "set_" + b)(self.get_bag(b))

    def max_stat(self, name):
        """Set a stat's current value to its max value."""
        getattr(self.player, "set_"+name)(100)
        self.update_stat(name)

    def set_stat(self, name):
        max = getattr(self.ui, "max_"+name).value()
        getattr(self.player, "set_max_"+name)(float(max))
        self.update_stat(name)

    def set_stat_slider(self, name):
        current = getattr(self.ui, name).value()
        getattr(self.player, "set_"+name)(current)
        self.update_stat(name)

    def update_stat(self, name):
        try:
            current = int(getattr(self.player, "get_"+name)())
            getattr(self.ui, name).setValue(current)
            self.set_edited()
        except TypeError:
            logging.exception("Unable to set stat %s", name)

    # these are used for connecting the item edit dialog to bag tables
    # TODO: change to lamdas
    def new_main_bag_item_edit(self):
        self.new_item_edit(self.ui.main_bag)
    def new_tile_bag_item_edit(self):
        self.new_item_edit(self.ui.tile_bag)
    def new_action_bar_item_edit(self):
        self.new_item_edit(self.ui.action_bar)
    def new_head_item_edit(self):
        self.new_item_edit(self.ui.head)
    def new_chest_item_edit(self):
        self.new_item_edit(self.ui.chest)
    def new_legs_item_edit(self):
        self.new_item_edit(self.ui.legs)
    def new_back_item_edit(self):
        self.new_item_edit(self.ui.back)
    def new_wieldable_item_edit(self):
        self.new_item_edit(self.ui.wieldable)
    def new_essentials_item_edit(self):
        self.new_item_edit(self.ui.essentials)
    def new_mouse_item_edit(self):
        self.new_item_edit(self.ui.mouse)
