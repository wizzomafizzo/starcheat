"""
Main application window for starcheat GUI
"""

import sys, logging, json
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import saves, assets, qt_mainwindow
from config import Config
from gui.common import ItemWidget, empty_slot, preview_icon
from gui.utils import CharacterSelectDialog, OptionsDialog, AboutDialog
from gui.utils import save_modified_dialog, new_setup_dialog
from gui.itemedit import ItemEdit
from gui.blueprints import BlueprintLib
from gui.itembrowser import ItemBrowser
from gui.appearance import Appearance

class StarcheatMainWindow(QMainWindow):
    """Overrides closeEvent on the main window to allow "want to save changes?" dialog"""
    def __init__(self, parent):
        super(QMainWindow, self).__init__()
        self.parent = parent

    def closeEvent(self, event):
        if not self.isWindowModified():
            event.accept()
            return

        button = save_modified_dialog()
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
        # BUG: these export the current values in self.player but a lot of that
        # won't be populated until the file is actually saved
        self.ui.actionExport.triggered.connect(self.export_save)
        self.ui.actionExportJSON.triggered.connect(self.export_json)

        # launch open file dialog
        self.player = None
        # we *need* at least an initial save file
        logging.debug("Open file dialog")
        open_player = self.open_file(skip_update=True)
        if not open_player:
            logging.warning("No player file selected")
            return

        # populate species combobox
        for species in self.assets.species().get_species_list():
            self.ui.race.addItem(species)

        # populate game mode combobox
        for mode in self.assets.player().mode_types.values():
            self.ui.game_mode.addItem(mode)

        # set up sliders to update values together
        stats = "health", "energy"
        for s in stats:
            logging.debug("Setting up %s stat", s)
            update = getattr(self, "update_" + s)
            getattr(self.ui, s).valueChanged.connect(update)
            getattr(self.ui, "max_" + s).valueChanged.connect(update)

        self.ui.max_food.valueChanged.connect(self.set_edited)
        self.ui.max_breath.valueChanged.connect(self.set_edited)
        self.ui.max_warmth.valueChanged.connect(self.set_edited)

        # set up bag tables
        bags = "wieldable", "head", "chest", "legs", "back", "main_bag", "action_bar", "tile_bag"
        for b in bags:
            logging.debug("Setting up %s bag", b)
            item_edit = getattr(self, "new_" + b + "_item_edit")
            getattr(self.ui, b).cellDoubleClicked.connect(item_edit)
            # TODO: still issues with drag drop between tables
            getattr(self.ui, b).setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.ui.blueprints_button.clicked.connect(self.new_blueprint_edit)
        self.ui.appearance_button.clicked.connect(self.new_appearance_dialog)
        self.ui.name.textChanged.connect(self.set_edited)
        self.ui.race.currentTextChanged.connect(self.update_species)
        self.ui.male.clicked.connect(self.update_player_preview)
        self.ui.female.clicked.connect(self.update_player_preview)
        self.ui.description.textChanged.connect(self.set_edited)
        self.ui.pixels.valueChanged.connect(self.set_pixels)
        self.ui.game_mode.currentTextChanged.connect(self.set_edited)

        self.ui.play_time_button1.clicked.connect(lambda: self.inc_play_time(10*60))
        self.ui.play_time_button2.clicked.connect(lambda: self.inc_play_time(60*60))

        self.update()
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
        # BUG: okay so there is this bug where sometimes on windows pyqt will chuck
        # a fit and not set values on some stuff. this seems to work itself out
        # when you overwrite the values and reopen the file. i'm going to just
        # ignore it but would still like a better solution
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
        # play time
        # TODO: there must be a datetime function for doing this stuff
        play_time = str(int(self.player.get_play_time()/60)) + " mins"
        self.ui.play_time.setText(play_time)

        # stats
        stats = "health", "energy"
        for stat in stats:
            try:
                max_stat = getattr(self.player, "get_max_" + stat)()
                getattr(self.ui, "max_" + stat).setValue(max_stat)
                cur_stat = getattr(self.player, "get_" + stat)()
                getattr(self.ui, stat).setMaximum(max_stat)
                getattr(self.ui, stat).setValue(cur_stat[0])
                getattr(self, "update_" + stat)()
            except TypeError:
                logging.exception("Unable to set %s", stat)
        # energy regen rate
        try:
            self.ui.energy_regen.setValue(self.player.get_energy_regen())
        except TypeError:
            logging.exception("Unable to set energy regen rate")
        # breath
        try:
            max_food = self.player.get_max_food()
            self.ui.max_food.setValue(max_food)
            self.ui.food_val.setText(str(int(self.player.get_food()[0])) + " /")
        except TypeError:
            logging.exception("Unable to set food")
        # warmth
        try:
            max_warmth = self.player.get_max_warmth()
            self.ui.max_warmth.setValue(max_warmth)
            self.ui.warmth_val.setText(str(int(self.player.get_warmth()[1])) + " /")
        except TypeError:
            logging.exception("Unable to set warmth")
        # breath
        try:
            max_breath = self.player.get_max_breath()
            self.ui.max_breath.setValue(max_breath)
            self.ui.breath_val.setText(str(int(self.player.get_breath()[0])) + " /")
        except TypeError:
            logging.exception("Unable to set warmth")

        # equipment
        equip_bags = "head", "chest", "legs", "back"
        for bag in equip_bags:
            logging.debug("Updating %s", bag)
            items = [ItemWidget(x, self.assets) for x in getattr(self.player, "get_" + bag)()]
            getattr(self.ui, bag).setItem(0, 0, items[0])
            getattr(self.ui, bag).setItem(0, 1, items[1])

        # wielded
        self.update_bag("wieldable")

        # bags
        self.update_bag("main_bag")
        self.update_bag("tile_bag")
        self.update_bag("action_bar")

        self.update_player_preview()

    def save(self):
        """Update internal player dict with GUI values and export to file."""
        logging.info("Saving player file %s", self.player.filename)
        # name
        self.player.set_name(self.ui.name.text())
        # species
        self.player.set_race(self.ui.race.currentText())
        # description
        self.player.set_description(self.ui.description.toPlainText())
        # gender
        self.player.set_gender(self.get_gender())
        # game mode
        self.player.set_game_mode(self.assets.player().get_mode_type(self.ui.game_mode.currentText()))
        # stats
        stats = "health", "energy"
        for s in stats:
            current = getattr(self.ui, s).value()
            maximum = getattr(self.ui, "max_" + s).value()
            getattr(self.player, "set_" + s)(current, maximum)
            getattr(self.player, "set_max_" + s)(maximum)
        # food
        self.player.set_max_food(self.ui.max_food.value())
        # energy regen rate
        self.player.set_energy_regen(self.ui.energy_regen.value())
        # warmth
        self.player.set_max_warmth(self.ui.max_warmth.value())
        # breath
        self.player.set_max_breath(self.ui.max_breath.value())
        # equipment
        equip_bags = "head", "chest", "legs", "back"
        for b in equip_bags:
            bag = self.get_equip(b)
            getattr(self.player, "set_" + b)(bag[0], bag[1])
        # bags
        bags = "wieldable", "main_bag", "tile_bag", "action_bar"
        for b in bags:
            getattr(self.player, "set_" + b)(self.get_bag(b))
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
        item = saves.new_item("", 0, {})
        # cells don't retain ItemSlot widget when they've been dragged away
        if type(current) is QTableWidgetItem or current.item is None:
            pass
        else:
            item.update(current.item)

        item_edit = ItemEdit(self.window, item,
                             self.player, self.remember_browser)

        def update_slot():
            logging.debug("Writing changes to slot")
            new_slot = ItemWidget(item_edit.get_item(), self.assets)
            if new_slot.item["name"] != "":
                bag.setItem(row, column, new_slot)
                self.remember_browser = item_edit.remember_browser
                self.set_edited()

        def trash_slot():
            logging.debug("Trashed item")
            bag.setItem(row, column, empty_slot())
            item_edit.dialog.close()
            self.set_edited()

        item_edit.dialog.accepted.connect(update_slot)
        item_edit.ui.trash_button.clicked.connect(trash_slot)
        item_edit.dialog.exec()

    def set_edited(self):
        self.window.setWindowModified(True)

    def new_blueprint_edit(self):
        """Launch a new blueprint management dialog."""
        logging.debug("New blueprint dialog")
        blueprint_lib = BlueprintLib(self.window, self.player.get_blueprints())

        def update_blueprints():
            logging.debug("Writing blueprints")
            self.player.set_blueprints(blueprint_lib.get_known_list())
            blueprint_lib.dialog.close()
            self.set_edited()

        blueprint_lib.ui.buttonBox.accepted.connect(update_blueprints)
        blueprint_lib.ui.buttonBox.rejected.connect(blueprint_lib.dialog.close)
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
        appearance_dialog.dialog.accepted.connect(appearance_dialog.write_appearance_values)
        appearance_dialog.dialog.exec()

    def reload(self):
        """Reload the currently open save file and update GUI values."""
        logging.info("Reloading file %s", self.player.filename)
        self.player = saves.PlayerSave(self.player.filename)
        self.update()
        self.ui.statusbar.showMessage("Reloaded " + self.player.filename, 3000)
        self.window.setWindowModified(False)

    def open_file(self, skip_update=False):
        """Display open file dialog and load selected save."""
        if self.window.isWindowModified():
            button = save_modified_dialog()
            if button == QMessageBox.Cancel:
                return False
            elif button == QMessageBox.Save:
                self.save()

        character_select = CharacterSelectDialog(self.window)
        character_select.show()

        if character_select.selected == None:
            logging.warning("No player selected")
            return False
        else:
            self.player = character_select.selected

        if not skip_update:
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
            self.player.export_save(filename[0])
            self.ui.statusbar.showMessage("Exported save file to " + filename[0], 3000)

    def export_json(self):
        """Export player entity as json."""
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
            if type(item) is QTableWidgetItem or item == None:
                item = None
            else:
                item = item.item

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
        if main_cell == None or type(main_cell) is QTableWidgetItem:
            main = None
        else:
            main = main_cell.item

        if glamor_cell == None or type(glamor_cell) is QTableWidgetItem:
            glamor = None
        else:
            glamor = glamor_cell.item

        return main, glamor

    def update_bag(self, bag_name):
        """Set the entire contents of any given bag with ItemWidgets based off player data."""
        logging.debug("Updating %s contents", bag_name)
        row = column = 0
        bag = getattr(self.player, "get_" + bag_name)()

        for slot in range(len(bag)):
            widget = ItemWidget(bag[slot], self.assets)
            getattr(self.ui, bag_name).setItem(row, column, widget)

            column += 1
            if (column % 10) == 0:
                row += 1
                column = 0

    def update_player_preview(self):
        species = self.ui.race.currentText()
        gender = self.get_gender()
        image = preview_icon(species, gender)
        self.ui.player_preview.setPixmap(image.scaled(64, 64))
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

    # these are used for connecting the item edit dialog to bag tables
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

    def inc_play_time(self, amount):
        play_time = self.player.get_play_time() + float(amount)
        self.player.set_play_time(play_time)
        formatted = str(int(play_time/60)) + " mins"
        self.ui.play_time.setText(formatted)
        self.set_edited()

    def set_pixels(self):
        self.player.set_pixels(self.ui.pixels.value())

    # these update all values in a stat group at once
    def update_energy(self):
        self.ui.energy.setMaximum(self.ui.max_energy.value())
        self.ui.energy_val.setText(str(self.ui.energy.value()) + " /")
        self.set_edited()
    def update_health(self):
        self.ui.health.setMaximum(self.ui.max_health.value())
        self.ui.health_val.setText(str(self.ui.health.value()) + " /")
        self.set_edited()
