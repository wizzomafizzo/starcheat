"""
Main application window for starcheat GUI
"""

import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

from config import Config
import logging, save_file, assets, qt_mainwindow

from gui_common import ItemWidget, empty_slot, preview_icon
from gui_utils import CharacterSelectDialog, OptionsDialog
from gui_itemedit import ItemEdit
from gui_blueprints import BlueprintLib

class MainWindow():
    def __init__(self):
        """Display the main starcheat window."""
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = qt_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self.window)

        logging.info("Main window init")

        # launch first setup
        self.setup_dialog = None
        # TODO: I don't like this at all, I want a proper validation when they
        # try click save but for now we need a way to stop people hitting enter
        # the second this pops up
        while Config().read("player_folder") == "" or Config().read("assets_folder") == "":
            logging.info("First setup dialog")
            self.new_setup_dialog()

        self.filename = None
        logging.debug("Loading assets")
        self.items = assets.Items()

        # atm we only support one of each dialog at a time, don't think this
        # will be a problem tho
        # TODO: some really weird behaviour here w/ blueprint
        #self.item_browser = None
        self.item_edit = None
        self.blueprint_lib = None
        self.options_dialog = None

        # connect action menu
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionReload.triggered.connect(self.reload)
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionQuit.triggered.connect(self.app.closeAllWindows)
        self.ui.actionOptions.triggered.connect(self.new_options_dialog)

        # launch open file dialog
        # we want this after the races are populated but before the slider setup
        self.player = None
        logging.debug("Open file dialog")
        self.open_file()
        # we *need* at least an initial save file
        if self.player == None:
            logging.warning("No player file selected")
            return

        # set up sliders to update values together
        stats = "health", "energy", "food", "warmth", "breath"
        for s in stats:
            logging.debug("Setting up %s stat", s)
            update = getattr(self, "update_" + s)
            getattr(self.ui, s).valueChanged.connect(update)
            getattr(self.ui, "max_" + s).valueChanged.connect(update)

        # set up bag tables
        bags = "wieldable", "head", "chest", "legs", "back", "main_bag", "action_bar", "tile_bag"
        for b in bags:
            logging.debug("Setting up %s bag", b)
            item_edit = getattr(self, "new_" + b + "_item_edit")
            getattr(self.ui, b).cellDoubleClicked.connect(item_edit)
            # TODO: still issues with drag drop between tables
            getattr(self.ui, b).setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.ui.blueprints_button.clicked.connect(self.new_blueprint_edit)
        self.ui.race.currentTextChanged.connect(self.update_player_preview)
        self.ui.male.clicked.connect(self.update_player_preview)
        self.ui.female.clicked.connect(self.update_player_preview)
        self.ui.name.setFocus()

        logging.debug("Showing main window")
        self.window.show()
        sys.exit(self.app.exec_())

    def update(self):
        """Update all GUI widgets with values from PlayerSave instance."""
        logging.info("Updating main window")
        # uuid / save version
        self.ui.uuid_label.setText(self.player.get_uuid())
        self.ui.ver_label.setText("v" + self.player.get_save_ver())
        # name
        self.ui.name.setText(self.player.get_name())
        # race
        # populate race combo box
        self.ui.race.clear()
        for race in assets.Species().get_species_list():
            self.ui.race.addItem(race)
        self.ui.race.setCurrentText(self.player.get_race())
        # BUG: okay so there is this bug where sometimes on windows pyqt will chuck
        # a fit and not set values on some stuff. this seems to work itself out
        # when you overwrite the values and reopen the file. i'm going to just
        # ignore it but would still like a better solution
        # pixels
        try:
            self.ui.pixels.setValue(self.player.get_pixels())
        except TypeError:
            logging.exception("Unable to set pixels")
        # description
        self.ui.description.setPlainText(self.player.get_description())
        # gender
        getattr(self.ui, self.player.get_gender()).toggle()

        # stats
        stats = "health", "energy", "food", "breath"
        for stat in stats:
            try:
                max_stat = getattr(self.player, "get_max_" + stat)()
                getattr(self.ui, "max_" + stat).setValue(max_stat)
                cur_stat = getattr(self.player, "get_" + stat)()
                getattr(self.ui, stat).setMaximum(cur_stat[1])
                getattr(self.ui, stat).setValue(cur_stat[0])
                getattr(self, "update_" + stat)()
            except TypeError:
                logging.exception("Unable to set %s", stat)
        # energy regen rate
        try:
            self.ui.energy_regen.setValue(self.player.get_energy_regen())
        except TypeError:
            logging.exception("Unable to set energy regen rate")
        # warmth
        try:
            max_warmth = self.player.get_max_warmth()
            self.ui.max_warmth.setValue(max_warmth)
            cur_warmth = self.player.get_warmth()
            self.ui.warmth.setMinimum(cur_warmth[0])
            self.ui.warmth.setMaximum(max_warmth)
            self.ui.warmth.setValue(cur_warmth[1])
            self.update_warmth()
        except TypeError:
            logging.exception("Unable to set warmth")

        # equipment
        equip_bags = "head", "chest", "legs", "back"
        for bag in equip_bags:
            logging.debug("Updating %s", bag)
            items = [ItemWidget(x) for x in getattr(self.player, "get_" + bag)()]
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
        logging.debug(self.player.data)
        # name
        self.player.set_name(self.ui.name.text())
        # race
        self.player.set_race(self.ui.race.currentText())
        # pixels
        self.player.set_pixels(self.ui.pixels.value())
        # description
        self.player.set_description(self.ui.description.toPlainText())

        # gender
        if self.ui.male.isChecked():
            self.player.set_gender("male")
        else:
            self.player.set_gender("female")

        # stats
        stats = "health", "energy", "food", "breath"
        for s in stats:
            current = getattr(self.ui, s).value()
            maximum = getattr(self.ui, "max_" + s).value()
            getattr(self.player, "set_" + s)(current, maximum)
            getattr(self.player, "set_max_" + s)(maximum)
        # energy regen rate
        self.player.set_energy_regen(self.ui.energy_regen.value())
        # warmth
        self.player.set_warmth(self.ui.warmth.value())
        self.player.set_max_warmth(self.ui.max_warmth.value())

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
        self.player.export_save(self.player.filename)
        self.ui.statusbar.showMessage("Saved " + self.player.filename, 3000)

    def new_item_edit(self, bag):
        """Display a new item edit dialog using the select cell in a given bag."""
        logging.debug("New item edit dialog")
        row = bag.currentRow()
        column = bag.currentColumn()
        item_edit = ItemEdit(self.window, bag.currentItem())

        def update_slot():
            logging.debug("Writing changes to slot")
            new_slot = item_edit.get_item()
            bag.setItem(row, column, new_slot)

        def trash_slot():
            logging.debug("Trashed item")
            bag.setItem(row, column, empty_slot())
            item_edit.dialog.close()

        item_edit.dialog.accepted.connect(update_slot)
        item_edit.ui.trash_button.clicked.connect(trash_slot)

    def new_blueprint_edit(self):
        logging.debug("New blueprint dialog")
        # TODO: why does this only work with and instance var but the other
        # ones don't...???
        self.blueprint_lib = BlueprintLib(self.window, self.player.get_blueprints())

        def update_blueprints():
            logging.debug("Writing blueprints")
            self.player.set_blueprints(self.blueprint_lib.get_known_list())
            self.blueprint_lib.dialog.close()

        # TODO: find out why this wasn't working since the grid update. what
        # makes a buttonBox "automatic" when it's created originally in designer?
        self.blueprint_lib.ui.buttonBox.accepted.connect(update_blueprints)
        self.blueprint_lib.ui.buttonBox.rejected.connect(self.blueprint_lib.dialog.close)
        self.blueprint_lib.dialog.show()

    def new_options_dialog(self):
        logging.debug("New options dialog")
        self.options_dialog = OptionsDialog(self.window)

        def write_options():
            logging.info("Writing options to disk")
            # TODO: reload icons on asset update?
            self.ui.statusbar.showMessage("Options have been updated", 3000)

        self.options_dialog.dialog.accepted.connect(write_options)
        self.options_dialog.dialog.exec()

    def new_setup_dialog(self):
        self.setup_dialog = OptionsDialog(self.window)
        self.setup_dialog.dialog.rejected.connect(sys.exit)
        self.setup_dialog.dialog.exec()
        self.setup_dialog.rebuild_db()

    def reload(self):
        """Reload the currently open save file and update GUI values."""
        logging.info("Reloading file %s", self.player.filename)
        self.player = save_file.PlayerSave(self.player.filename)
        self.update()
        self.ui.statusbar.showMessage("Reloaded " + self.player.filename, 3000)

    def open_file(self):
        """Display open file dialog and load selected save."""
        character_select = CharacterSelectDialog(self.window)
        character_select.show()

        try:
            self.player = character_select.selected
        except AttributeError:
            # didn't pick anything... i think?
            logging.exception("No player selected")
            return

        self.update()
        self.window.setWindowTitle("starcheat - " + os.path.basename(self.player.filename))
        self.ui.statusbar.showMessage("Opened " + self.player.filename, 3000)

    def get_bag(self, name):
        """Return the entire contents of a given non-equipment bag as raw values."""
        logging.debug("Getting %s contents", name)
        row = column = 0
        bag = getattr(self.player, "get_" + name)()

        for i in range(len(bag)):
            item = getattr(self.ui, name).item(row, column)
            if type(item) is QTableWidgetItem or item == None:
                item = empty_slot()

            count = item.item_count
            item_type = item.name
            variant = item.variant
            bag[i] = (item_type, int(count), variant)

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
            main = save_file.empty_slot()
        else:
            main = (main_cell.name, main_cell.item_count, main_cell.variant)

        if glamor_cell == None or type(glamor_cell) is QTableWidgetItem:
            glamor = save_file.empty_slot()
        else:
            glamor = (glamor_cell.name, glamor_cell.item_count, glamor_cell.variant)

        return main, glamor

    def update_bag(self, bag_name):
        """Set the entire contents of any given bag with ItemWidgets based off player data."""
        logging.debug("Updating %s contents", bag_name)
        row = column = 0
        bag = getattr(self.player, "get_" + bag_name)()

        for slot in range(len(bag)):
            widget = ItemWidget(bag[slot])
            getattr(self.ui, bag_name).setItem(row, column, widget)

            column += 1
            if (column % 10) == 0:
                row += 1
                column = 0

    def update_player_preview(self):
        if self.ui.male.isChecked():
            gender = "male"
        else:
            gender = "female"
        image = preview_icon(self.ui.race.currentText(), gender)
        self.ui.player_preview.setPixmap(image.scaled(64, 64))

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

    # these update all values in a stat group at once
    def update_energy(self):
        self.ui.energy.setMaximum(self.ui.max_energy.value())
        self.ui.energy_val.setText(str(self.ui.energy.value()) + " /")
    def update_health(self):
        self.ui.health.setMaximum(self.ui.max_health.value())
        self.ui.health_val.setText(str(self.ui.health.value()) + " /")
    def update_food(self):
        self.ui.food.setMaximum(self.ui.max_food.value())
        self.ui.food_val.setText(str(self.ui.food.value()) + " /")
    def update_warmth(self):
        self.ui.warmth.setMaximum(self.ui.max_warmth.value())
        self.ui.warmth_val.setText(str(self.ui.warmth.value()) + " /")
    def update_breath(self):
        self.ui.breath.setMaximum(self.ui.max_breath.value())
        self.ui.breath_val.setText(str(self.ui.breath.value()) + " /")
