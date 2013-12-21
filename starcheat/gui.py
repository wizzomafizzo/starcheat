import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem

from qt_mainwindow import Ui_MainWindow
from qt_itemedit import Ui_Dialog

import save_file, assets

# TODO: add support for item icons
class ItemWidget(QTableWidgetItem):
    def __init__(self, item):
        self.item_count = item[1]
        self.type_name = item[0]
        self.variant = item[2]
        QTableWidgetItem.__init__(self, self.type_name)
        if self.type_name != "":
            self.setToolTip(self.type_name + " (" + str(self.item_count) + ")")

class MainWindow():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        # track current open/selected item
        self.item_bag = ""
        self.item_edit = ""
        self.item_dialog = ""

        # populate race combo box
        for race in save_file.race_types:
            self.ui.race.addItem(race[0].upper() + race[1:])

        # launch open file dialog
        # TODO: handle file errors
        self.open_file()

        # connect action menu
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionReload.triggered.connect(self.reload)
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionQuit.triggered.connect(self.app.closeAllWindows)

        # set up sliders to update values together
        # health
        self.ui.max_health.valueChanged.connect(self.update_health)
        self.ui.max_energy.valueChanged.connect(self.update_energy)
        # energy
        self.ui.health.valueChanged.connect(self.update_health)
        self.ui.energy.valueChanged.connect(self.update_energy)
        # TODO: food, warmth, breath

        # connect edit item dialog to each bag table
        self.ui.main_bag.cellDoubleClicked.connect(self.new_main_item_edit)
        self.ui.tile_bag.cellDoubleClicked.connect(self.new_tile_item_edit)
        self.ui.action_bar.cellDoubleClicked.connect(self.new_action_item_edit)
        self.ui.head.cellDoubleClicked.connect(self.new_head_item_edit)
        self.ui.chest.cellDoubleClicked.connect(self.new_chest_item_edit)
        self.ui.legs.cellDoubleClicked.connect(self.new_legs_item_edit)
        self.ui.back.cellDoubleClicked.connect(self.new_back_item_edit)
        self.ui.wielded.cellDoubleClicked.connect(self.new_wielded_item_edit)

        # TODO: fix up the .ui file and remove all this
        # TODO: reimplement drag drop methods
        bags = ("wielded", "head", "chest", "legs", "back", "main_bag", "action_bar", "tile_bag")
        for i in bags:
            getattr(self.ui, i).setAcceptDrops(False)
            getattr(self.ui, i).setDragDropOverwriteMode(True)
            getattr(self.ui, i).setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
            getattr(self.ui, i).setDefaultDropAction(QtCore.Qt.MoveAction)
            getattr(self.ui, i).setDragEnabled(True)

        self.window.show()
        sys.exit(self.app.exec_())

    def empty_slot(self):
        """Return an empty bag slot widget."""
        return ItemWidget(("", 0, (7, [])))

    # these are used for connecting the item edit dialog to bag tables
    def new_main_item_edit(self):
        self.item_bag = "main_bag"
        self.new_item_edit(self.ui.main_bag)

    def new_tile_item_edit(self):
        self.item_bag = "tile_bag"
        self.new_item_edit(self.ui.tile_bag)

    def new_action_item_edit(self):
        self.item_bag = "action_bar"
        self.new_item_edit(self.ui.action_bar)

    def new_head_item_edit(self):
        self.item_bag = "head"
        self.new_item_edit(self.ui.head)

    def new_chest_item_edit(self):
        self.item_bag = "chest"
        self.new_item_edit(self.ui.chest)

    def new_legs_item_edit(self):
        self.item_bag = "legs"
        self.new_item_edit(self.ui.legs)

    def new_back_item_edit(self):
        self.item_bag = "back"
        self.new_item_edit(self.ui.back)

    def new_wielded_item_edit(self):
        self.item_bag = "wielded"
        self.new_item_edit(self.ui.wielded)

    def new_item_edit(self, bag):
        """Display an item edit dialog for the selected cell in a given bag."""
        self.item_dialog = QDialog()
        self.item_edit = Ui_Dialog()
        self.item_edit.setupUi(self.item_dialog)

        item = bag.currentItem()
        # cells don't retain ItemSlot widget when they've been dragged away
        if type(item) is QTableWidgetItem or item == None:
            item = self.empty_slot()

        # set up signals
        self.item_dialog.accepted.connect(self.write_item_edit)
        self.item_edit.load_button.clicked.connect(self.open_asset)

        # set type text box
        self.item_edit.item_type.setText(item.type_name)
        # set item count spinbox
        self.item_edit.count.setValue(int(item.item_count))

        # set up variant table
        self.item_edit.variant.setRowCount(len(item.variant[1]))
        for i in range(len(item.variant[1])):
            key = QTableWidgetItem(item.variant[1][i][0])
            value = QTableWidgetItem(str(item.variant[1][i][1]))
            self.item_edit.variant.setItem(i, 0, key)
            self.item_edit.variant.setItem(i, 1, value)

        self.item_dialog.show()

    def write_item_edit(self):
        """Write item edit dialog values to selected item cell."""
        type_name = self.item_edit.item_type.text()
        count = self.item_edit.count.value()
        bag = getattr(self.ui, self.item_bag)

        cur_item = bag.currentItem()
        if type(cur_item) is QTableWidgetItem or cur_item == None:
            cur_item = self.empty_slot()

        # TODO: variants. might want to write a recursive variant dialog
        # for now could use literal eval?
        variant = cur_item.variant

        # write to cell
        new_item = ItemWidget((type_name, count, variant))
        row = bag.currentRow()
        column = bag.currentColumn()
        bag.setItem(row, column, new_item)

    def update_energy(self):
        self.ui.energy.setMaximum(self.ui.max_energy.value())
        self.ui.energy_val.setText(str(self.ui.energy.value()) + " /")

    def update_health(self):
        self.ui.health.setMaximum(self.ui.max_health.value())
        self.ui.health_val.setText(str(self.ui.health.value()) + " /")

    def save(self):
        """Update internal player dict with GUI values and export to file."""
        # TODO: everything here should be a setting in PlayerSave
        # name
        self.player.data["name"] = self.ui.name.text()
        # race
        self.player.data["race"] = self.ui.race.currentText().lower()
        # pixels
        self.player.data["inv"]["pixels"] = (self.ui.pixels.value(),)
        # description
        self.player.data["description"] = self.ui.description.toPlainText()
        # gender
        if self.ui.male.isChecked():
            self.player.data["gender"] = (0,)
        else:
            self.player.data["gender"] = (1,)
        # health
        self.player.data["health"] = (self.ui.health.value(), int(self.ui.max_health.value()))
        self.player.data["base_max_health"] = (int(self.ui.max_health.value()),)
        # energy
        self.player.data["energy"] = (self.ui.energy.value(), int(self.ui.max_energy.value()))
        self.player.data["energy_regen_rate"] = (self.ui.energy_regen.value(),)
        self.player.data["base_max_energy"] = (int(self.ui.max_energy.value()),)
        # hunger
        self.player.data["food"] = (self.ui.hunger.value(), self.player.data["food"][1])
        # warmth
        self.player.data["warmth"] = (self.player.data["warmth"][0], self.ui.warmth.value())
        # breath
        self.player.data["breath"] = (self.ui.breath.value(), self.ui.breath.maximum())

        # equipment
        # get items from given equipment slot
        def get_equip(name):
            equip = getattr(self.ui, name)
            main_cell = equip.item(0, 0)
            glamor_cell = equip.item(0, 1)
            if main_cell == None or type(main_cell) is QTableWidgetItem:
                main = ("", 0, (7, []))
            else:
                main = (main_cell.type_name, main_cell.item_count, main_cell.variant)
            if glamor_cell == None or type(glamor_cell) is QTableWidgetItem:
                glamor = ("", 0, (7, []))
            else:
                glamor = (glamor_cell.type_name, glamor_cell.item_count, glamor_cell.variant)
            return main, glamor

        # head
        head = get_equip("head")
        self.player.data["head"] = head[0]
        self.player.data["head_glamor"] = head[1]
        # chest
        chest = get_equip("chest")
        self.player.data["chest"] = chest[0]
        self.player.data["chest_glamor"] = chest[1]
        # legs
        legs = get_equip("legs")
        self.player.data["legs"] = legs[0]
        self.player.data["legs_glamor"] = legs[1]
        # back
        back = get_equip("back")
        self.player.data["back"] = back[0]
        self.player.data["back_glamor"] = back[1]
        # left hand
        wielded = get_equip("wielded")
        self.player.data["inv"]["wieldable"][0] = wielded[0]
        # right hand
        self.player.data["inv"]["wieldable"][1] = wielded[1]

        # main bag
        main_bag_row = 0
        main_bag_column = 0
        for i in range(len(self.player.data["inv"]["main_bag"])):
            item = self.ui.main_bag.item(main_bag_row, main_bag_column)
            if type(item) is QTableWidgetItem or item == None:
                item = self.empty_slot()
            count = item.item_count
            item_type = item.type_name
            variant = self.player.data["inv"]["main_bag"][i][2]
            self.player.data["inv"]["main_bag"][i] = (item_type, int(count), variant)
            main_bag_column += 1
            if (main_bag_column % 10) == 0:
                main_bag_row += 1
                main_bag_column = 0

        # tile bag
        tile_bag_row = 0
        tile_bag_column = 0
        for i in range(len(self.player.data["inv"]["tile_bag"])):
            item = self.ui.tile_bag.item(tile_bag_row, tile_bag_column)
            if type(item) is QTableWidgetItem or item == None:
                item = self.empty_slot()
            count = item.item_count
            item_type = item.type_name
            variant = self.player.data["inv"]["tile_bag"][i][2]
            self.player.data["inv"]["tile_bag"][i] = (item_type, int(count), variant)
            tile_bag_column += 1
            if (tile_bag_column % 10) == 0:
                tile_bag_row += 1
                tile_bag_column = 0

        # action bar
        action_bar_column = 0
        for i in range(len(self.player.data["inv"]["action_bar"])):
            item = self.ui.action_bar.item(0, action_bar_column)
            if type(item) is QTableWidgetItem or item == None:
                item = self.empty_slot()
            count = item.item_count
            item_type = item.type_name
            variant = self.player.data["inv"]["action_bar"][i][2]
            self.player.data["inv"]["action_bar"][i] = (item_type, int(count), variant)
            action_bar_column += 1

        # might need to update them here too...? apprently now
        # equipment
        # wieldable

        # save and show status
        self.player.dump()
        self.player.export_save(self.player.filename)
        self.ui.statusbar.showMessage("Saved " + self.player.filename, 3000)

    def update(self):
        """Update all GUI values using internal player dictionary."""
        # TODO: all these should be made into setters on PlayerSave
        # name
        self.ui.name.setText(self.player.data["name"])
        # race
        self.ui.race.setCurrentText(self.player.data["race"][0].upper() + self.player.data["race"][1:])
        # pixels
        self.ui.pixels.setValue(self.player.data["inv"]["pixels"][0])
        # description
        self.ui.description.setPlainText(self.player.data["description"])
        # gender
        if self.player.data["gender"][0] == 0:
            self.ui.male.toggle()
        else:
            self.ui.female.toggle()
        # health
        self.ui.health.setMaximum(self.player.data["health"][1])
        self.ui.health.setValue(self.player.data["health"][0])
        self.ui.max_health.setValue(self.player.data["base_max_health"][0])
        self.update_health()
        # energy
        self.ui.energy.setMaximum(self.player.data["energy"][1])
        self.ui.energy.setValue(self.player.data["energy"][0])
        self.ui.max_energy.setValue(self.player.data["base_max_energy"][0])
        self.ui.energy_regen.setValue(self.player.data["energy_regen_rate"][0])
        self.update_energy()
        # hunger
        self.ui.hunger.setMaximum(self.player.data["food"][1])
        self.ui.hunger.setValue(self.player.data["food"][0])
        # warmth
        self.ui.warmth.setMinimum(self.player.data["warmth"][0])
        # TODO: check this is right
        self.ui.warmth.setMaximum(100)
        self.ui.warmth.setValue(self.player.data["warmth"][1])
        # breath
        self.ui.breath.setMaximum(self.player.data["breath"][1])
        self.ui.breath.setValue(self.player.data["breath"][0])

        # equipment
        # head
        head = ItemWidget(self.player.data["head"])
        self.ui.head.setItem(0, 0, head)
        head_glamor = ItemWidget(self.player.data["head_glamor"])
        self.ui.head.setItem(0, 1, head_glamor)
        # chest
        chest = ItemWidget(self.player.data["chest"])
        self.ui.chest.setItem(0, 0, chest)
        chest_glamor = ItemWidget(self.player.data["chest_glamor"])
        self.ui.chest.setItem(0, 1, chest_glamor)
        # legs
        legs = ItemWidget(self.player.data["legs"])
        self.ui.legs.setItem(0, 0, legs)
        legs_glamor = ItemWidget(self.player.data["legs_glamor"])
        self.ui.legs.setItem(0, 1, legs_glamor)
        # back
        back = ItemWidget(self.player.data["back"])
        self.ui.back.setItem(0, 0, back)
        back_glamor = ItemWidget(self.player.data["back_glamor"])
        self.ui.back.setItem(0, 1, back_glamor)
        # left hand
        left_hand = ItemWidget(self.player.data["inv"]["wieldable"][0])
        self.ui.wielded.setItem(0, 0, left_hand)
        # right hand
        right_hand = ItemWidget(self.player.data["inv"]["wieldable"][1])
        self.ui.wielded.setItem(0, 1, right_hand)

        # main bag
        main_bag_row = 0
        main_bag_column = 0
        main_bag = self.player.data["inv"]["main_bag"]
        for i in range(len(main_bag)):
            item_type = ItemWidget(main_bag[i])
            self.ui.main_bag.setItem(main_bag_row, main_bag_column, item_type)
            main_bag_column += 1
            if (main_bag_column % 10) == 0:
                main_bag_row += 1
                main_bag_column = 0

        # tile bag
        tile_bag_row = 0
        tile_bag_column = 0
        tile_bag = self.player.data["inv"]["tile_bag"]
        for i in range(len(tile_bag)):
            item_type = ItemWidget(tile_bag[i])
            self.ui.tile_bag.setItem(tile_bag_row, tile_bag_column, item_type)
            tile_bag_column += 1
            if (tile_bag_column % 10) == 0:
                tile_bag_row += 1
                tile_bag_column = 0

        # action bar
        action_bar_column = 0
        action_bar = self.player.data["inv"]["action_bar"]
        for i in range(len(action_bar)):
            item_type = ItemWidget(action_bar[i])
            self.ui.action_bar.setItem(0, action_bar_column, item_type)
            action_bar_column += 1

    def reload(self):
        """Reload the currently open save file and update GUI values."""
        self.player = save_file.PlayerSave(self.player.filename)
        self.update()
        self.ui.statusbar.showMessage("Reloaded " + self.player.filename, 3000)

    def open_file(self):
        """Display open file dialog and load selected save."""
        filename = QFileDialog.getOpenFileName(self.window,
                                               'Open save file...',
                                               '/opt/starbound/linux64/player',
                                               '*.player')
        self.player = save_file.PlayerSave(filename[0])
        self.update()
        self.ui.statusbar.showMessage("Opened " + self.player.filename, 3000)

    # TODO: update when assets module is fleshed out
    def open_asset(self):
        """Pick item asset file and load into item edit dialog."""
        filename = QFileDialog.getOpenFileName(self.item_dialog,
                                               "Pick an asset...",
                                               "/opt/starbound/assets/items")
        item = assets.parse_json(filename[0])
        try:
            name = item["name"]
        except KeyError:
            try:
                name = item["itemName"]
            except KeyError:
                name = item["objectName"]

        self.item_edit.item_type.setText(name)
        self.item_edit.count.setValue(1)

if __name__ == '__main__':
    window = MainWindow()
