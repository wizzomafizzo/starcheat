"""
Main application window for starcheat GUI
"""

import sys
import logging
import json

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtGui import QPixmap
from PIL.ImageQt import ImageQt
from threading import Thread

import saves
import assets
import qt_mainwindow
from config import Config
from gui.common import ItemWidget
from gui.common import empty_slot
from gui.openplayer import CharacterSelectDialog
from gui.utils import OptionsDialog
from gui.utils import AboutDialog
from gui.utils import ModsDialog
from gui.utils import save_modified_dialog
from gui.utils import new_setup_dialog
from gui.utils import check_index_valid
from gui.utils import update_check_worker
from gui.utils import update_check_dialog
from gui.itemedit import ItemEdit
from gui.itemedit import ImageBrowser
from gui.itemedit import import_json
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
        # check for new starcheat version online in seperate thread
        update_result = [None]
        update_thread = Thread(target=update_check_worker, args=(1, update_result), daemon=True)
        update_thread.start()

        """Display the main starcheat window."""
        self.app = QApplication(sys.argv)
        self.window = StarcheatMainWindow(self)
        self.ui = qt_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self.window)

        logging.info("Main window init")

        self.players = None
        self.filename = None

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

        # set up bag tables
        bags = ("wieldable", "head", "chest", "legs", "back", "main_bag",
                "action_bar", "tile_bag", "essentials", "mouse")
        for bag in bags:
            logging.debug("Setting up %s bag", bag)
            self.bag_setup(getattr(self.ui, bag), bag)

        # signals
        self.ui.blueprints_button.clicked.connect(self.new_blueprint_edit)
        self.ui.appearance_button.clicked.connect(self.new_appearance_dialog)
        self.ui.techs_button.clicked.connect(self.new_techs_dialog)

        self.ui.name.textChanged.connect(self.set_name)
        self.ui.male.clicked.connect(self.set_gender)
        self.ui.female.clicked.connect(self.set_gender)
        self.ui.description.textChanged.connect(self.set_description)
        self.ui.pixels.valueChanged.connect(self.set_pixels)

        self.ui.health.valueChanged.connect(lambda: self.set_stat_slider("health"))
        self.ui.energy.valueChanged.connect(lambda: self.set_stat_slider("energy"))
        self.ui.health_button.clicked.connect(lambda: self.max_stat("health"))
        self.ui.energy_button.clicked.connect(lambda: self.max_stat("energy"))

        self.ui.name_button.clicked.connect(self.random_name)
        self.ui.copy_uuid_button.clicked.connect(self.copy_uuid)

        self.window.setWindowModified(False)

        logging.debug("Showing main window")
        self.window.show()

        # launch first setup if we need to
        if not new_setup_dialog(self.window):
            logging.error("Config/index creation failed")
            return
        logging.info("Starbound folder: %s", Config().read("starbound_folder"))

        logging.info("Checking assets hash")
        if not check_index_valid(self.window):
            logging.error("Index creation failed")
            return

        logging.info("Loading assets database")
        self.assets = assets.Assets(Config().read("assets_db"),
                                    Config().read("starbound_folder"))
        self.items = self.assets.items()

        # populate species combobox
        for species in self.assets.species().get_species_list():
            self.ui.race.addItem(species)
        self.ui.race.currentTextChanged.connect(self.update_species)

        # populate game mode combobox
        for mode in sorted(self.assets.player().mode_types.values()):
            self.ui.game_mode.addItem(mode)
        self.ui.game_mode.currentTextChanged.connect(self.set_game_mode)

        # launch open file dialog
        self.player = None
        logging.debug("Open file dialog")
        open_player = self.open_file()
        # we *need* at least an initial save file
        if not open_player:
            logging.warning("No player file selected")
            return

        self.ui.name.setFocus()

        # block for update check result (should be ready now)
        update_thread.join()
        print(update_result)
        if update_result[0]:
            update_check_dialog(self.window, update_result[0])

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

        total = 0
        progress = QProgressDialog("Updating item slots...",
                                   None, 0, 10, self.window)

        progress.setWindowTitle("Updating...")
        progress.setWindowModality(QtCore.Qt.ApplicationModal)
        progress.forceShow()
        progress.setValue(total)

        # equipment
        equip_bags = "head", "chest", "legs", "back"
        for bag in equip_bags:
            logging.debug("Updating %s", bag)
            items = []
            for x in getattr(self.player, "get_" + bag)():
                if x is not None:
                    items.append(ItemWidget(x["__content"], self.assets))
                else:
                    items.append(ItemWidget(None, self.assets))

            getattr(self.ui, bag).setItem(0, 0, items[0])
            getattr(self.ui, bag).setItem(0, 1, items[1])
            total += 1
            progress.setValue(total)

        for bag in "wieldable", "main_bag", "tile_bag", "action_bar", "essentials", "mouse":
            self.update_bag(bag)
            total += 1
            progress.setValue(total)

        self.update_player_preview()

    def bag_setup(self, widget, name):
        widget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        # TODO: still issues with drag drop between tables
        widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        widget.cellChanged.connect(self.set_edited)

        item_edit = getattr(self, "new_" + name + "_item_edit")

        widget.cellDoubleClicked.connect(lambda: item_edit(False))

        sortable = ("main_bag", "tile_bag")
        clearable = ("wieldable", "action_bar", "essentials")

        edit_action = QAction("Edit...", widget)
        edit_action.triggered.connect(lambda: item_edit(False))
        widget.addAction(edit_action)
        import_json = QAction("Import...", widget)
        import_json.triggered.connect(lambda: item_edit(True))
        widget.addAction(import_json)
        trash_action = QAction("Trash", widget)
        trash_slot = lambda: self.trash_slot(self.window, widget, True)
        trash_action.triggered.connect(trash_slot)
        widget.addAction(trash_action)

        if name in sortable or name in clearable:
            sep_action = QAction(widget)
            sep_action.setSeparator(True)
            widget.addAction(sep_action)
            if name in clearable:
                clear_action = QAction("Clear Held Items", widget)
                clear_action.triggered.connect(self.clear_held_slots)
                widget.addAction(clear_action)
            if name in sortable:
                sort_name = QAction("Sort By Name", widget)
                sort_name.triggered.connect(lambda: self.sort_bag(name, "name"))
                widget.addAction(sort_name)
                sort_type = QAction("Sort By Type", widget)
                sort_type.triggered.connect(lambda: self.sort_bag(name, "category"))
                widget.addAction(sort_type)
                sort_count = QAction("Sort By Count", widget)
                sort_count.triggered.connect(lambda: self.sort_bag(name, "count"))
                widget.addAction(sort_count)

    def update_title(self):
        """Update window title with player name."""
        self.window.setWindowTitle("starcheat - " + self.player.get_name() + "[*]")

    def save(self):
        """Update internal player dict with GUI values and export to file."""
        logging.info("Saving player file %s", self.player.filename)
        self.set_bags()
        # save and show status
        logging.info("Writing file to disk")
        self.player.export_save(self.player.filename)
        self.update_title()
        self.ui.statusbar.showMessage("Saved " + self.player.filename, 3000)
        self.window.setWindowModified(False)
        self.players[self.player.get_uuid()] = self.player

    def new_item_edit(self, bag, do_import):
        """Display a new item edit dialog using the select cell in a given bag."""
        logging.debug("New item edit dialog")
        row = bag.currentRow()
        column = bag.currentColumn()
        current = bag.currentItem()
        item = saves.empty_slot()
        valid_slot = (type(current) is not QTableWidgetItem and
                      current is not None and
                      current.item is not None)

        if do_import:
            imported = import_json(self.window)
            if imported is False:
                self.ui.statusbar.showMessage("Error importing item, see starcheat log for details", 3000)
                return
            elif imported is None:
                return
            else:
                item = imported

        # cells don't retain ItemSlot widget when they've been dragged away
        if valid_slot:
            item.update(current.item)

        item_edit = ItemEdit(self.window, item,
                             self.player, self.assets,
                             self.remember_browser)

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
        got_item = item_edit.launch()
        if got_item:
            item_edit.dialog.exec()

    def trash_slot(self, dialog, bag, standalone=False):
        row = bag.currentRow()
        column = bag.currentColumn()
        ask_dialog = QMessageBox(dialog)
        ask_dialog.setWindowTitle("Trash Item")
        ask_dialog.setText("Are you sure?")
        ask_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ask_dialog.setDefaultButton(QMessageBox.No)
        ask_dialog.setIcon(QMessageBox.Question)
        if ask_dialog.exec() == QMessageBox.Yes:
            bag.setItem(row, column, empty_slot())
            if not standalone:
                dialog.close()
            self.set_edited()

    def set_edited(self):
        self.window.setWindowModified(True)

    def sort_bag(self, bag_name, sort_by):
        self.set_bags()
        bag = getattr(self.player, "get_" + bag_name)()
        sorted_bag = self.assets.player().sort_bag(bag, sort_by)
        getattr(self.player, "set_" + bag_name)(sorted_bag)
        self.ui.statusbar.showMessage("Sorting by " + sort_by + "...", 3000)
        self.update()
        self.ui.statusbar.clearMessage()

    def clear_held_slots(self):
        self.player.clear_held_slots()
        self.set_edited()
        self.ui.statusbar.showMessage("All held items have been cleared", 3000)

    def new_blueprint_edit(self):
        """Launch a new blueprint management dialog."""
        logging.debug("New blueprint dialog")
        blueprint_lib = BlueprintLib(self.window,
                                     self.player.get_blueprints(),
                                     self.player.get_new_blueprints())

        def update_blueprints():
            logging.debug("Writing blueprints")
            self.player.set_blueprints(blueprint_lib.get_known_list())
            self.player.set_new_blueprints(blueprint_lib.new_blueprints)
            blueprint_lib.dialog.close()
            self.set_edited()

        blueprint_lib.ui.buttonBox.rejected.connect(update_blueprints)
        blueprint_lib.dialog.exec()

    def copy_uuid(self):
        clipboard = self.app.clipboard()
        clipboard.setText(self.player.get_uuid())
        self.ui.statusbar.showMessage("UUID copied to clipboard", 3000)

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
            self.options_dialog.write()
            self.update()

        self.options_dialog.dialog.rejected.connect(write_options)
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
        self.update_title()
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

        character_select = CharacterSelectDialog(self, self.assets)
        character_select.show()

        self.players = character_select.players

        if character_select.selected is None:
            logging.warning("No player selected")
            return False
        else:
            self.player = character_select.selected

        self.update()
        self.update_title()
        self.ui.statusbar.showMessage("Opened " + self.player.filename, 3000)
        self.window.setWindowModified(False)
        return True

    def export_save(self):
        """Save a copy of the current player file to another location.
        Doesn't change the current filename."""
        filename = QFileDialog.getSaveFileName(self.window,
                                               "Export Save File As",
                                               filter="Player (*.player);;All Files (*)")
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
                                               "Export JSON File As",
                                               filter="JSON (*.json);;All Files (*)")
        if filename[0] != "":
            json_file = open(filename[0], "w")
            json_file.write(json_data)
            json_file.close()
            self.ui.statusbar.showMessage("Exported JSON file to " + filename[0], 3000)

    def import_json(self):
        """Import an exported JSON player entity and merge/update with open player."""
        filename = QFileDialog.getOpenFileName(self.window,
                                               "Import JSON Player File",
                                               filter="JSON (*.json);;All Files (*)")

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
            if item is not None and "__content" in item:
                widget = ItemWidget(item["__content"], self.assets)
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
            getattr(self.player, "set_%s_directives" % key)(defaults[key][0])
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

    def random_name(self):
        species_name = self.player.get_race()
        name = self.assets.species().generate_name(species_name)
        self.ui.name.setText(name)

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
            button = getattr(self.ui, name+"_button")
            getattr(self.ui, name).setValue(current)
            button.setEnabled(current != 100)
            self.set_edited()
        except TypeError:
            logging.exception("Unable to set stat %s", name)

    # these are used for connecting the item edit dialog to bag tables
    def new_main_bag_item_edit(self, do_import):
        self.new_item_edit(self.ui.main_bag, do_import)
    def new_tile_bag_item_edit(self, do_import):
        self.new_item_edit(self.ui.tile_bag, do_import)
    def new_action_bar_item_edit(self, do_import):
        self.new_item_edit(self.ui.action_bar, do_import)
    def new_head_item_edit(self, do_import):
        self.new_item_edit(self.ui.head, do_import)
    def new_chest_item_edit(self, do_import):
        self.new_item_edit(self.ui.chest, do_import)
    def new_legs_item_edit(self, do_import):
        self.new_item_edit(self.ui.legs, do_import)
    def new_back_item_edit(self, do_import):
        self.new_item_edit(self.ui.back, do_import)
    def new_wieldable_item_edit(self, do_import):
        self.new_item_edit(self.ui.wieldable, do_import)
    def new_essentials_item_edit(self, do_import):
        self.new_item_edit(self.ui.essentials, do_import)
    def new_mouse_item_edit(self, do_import):
        self.new_item_edit(self.ui.mouse, do_import)
