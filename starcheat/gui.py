"""
GUI module for starcheat
"""

import sys, re
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem

import save_file, assets
import qt_mainwindow, qt_itemedit, qt_itembrowser
from config import config

# TODO: add support for item icons
# TODO: reimplement drag events
class ItemWidget(QTableWidgetItem):
    def __init__(self, item, icon=None):
        self.item_count = item[1]
        self.type_name = item[0]
        self.variant = item[2]
        QTableWidgetItem.__init__(self, self.type_name)
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        if icon != None:
            try:
                self.setIcon(QtGui.QIcon(icon))
            except TypeError:
                pass
        if self.type_name != "":
            self.setToolTip(self.type_name + " (" + str(self.item_count) + ")")

class MainWindow():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = qt_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self.window)

        self.items = assets.Items()

        # populate race combo box
        for race in save_file.race_types:
            self.ui.race.addItem(race)

        # connect action menu
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionReload.triggered.connect(self.reload)
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionQuit.triggered.connect(self.app.closeAllWindows)

        # launch open file dialog
        # we want this after the races are populated but before the slider setup
        # TODO: handle file errors
        self.open_file()

        # set up sliders to update values together
        stats = "health", "energy", "food", "warmth", "breath"
        for s in stats:
            update = getattr(self, "update_" + s)
            getattr(self.ui, s).valueChanged.connect(update)
            getattr(self.ui, "max_" + s).valueChanged.connect(update)

        # set up bag tables
        bags = "wieldable", "head", "chest", "legs", "back", "main_bag", "action_bar", "tile_bag"
        for b in bags:
            item_edit = getattr(self, "new_" + b + "_item_edit")
            getattr(self.ui, b).cellDoubleClicked.connect(item_edit)
            # TODO: once drag is redone, fix up the .ui file and remove all this
            getattr(self.ui, b).setAcceptDrops(False)
            getattr(self.ui, b).setDragDropOverwriteMode(True)
            getattr(self.ui, b).setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
            getattr(self.ui, b).setDefaultDropAction(QtCore.Qt.MoveAction)
            getattr(self.ui, b).setDragEnabled(True)
            getattr(self.ui, b).setTabKeyNavigation(False)

        self.window.show()
        sys.exit(self.app.exec_())

    def empty_slot(self):
        """Return an empty bag slot widget."""
        return ItemWidget(save_file.empty_slot())

    def inv_icon(self, name):
        icon_file = self.items.get_item_icon(name)
        if icon_file == None:
            return None
        if icon_file[1] == "chest":
            offset = 16
        elif icon_file[1] == "pants":
            offset = 32
        else:
            offset = 0
        reader = QtGui.QImageReader(icon_file[0])
        reader.setClipRect(QtCore.QRect(offset, 0, 16, 16))
        return QtGui.QPixmap.fromImageReader(reader).scaled(32, 32)

    # TODO: move to separate class
    def new_item_browser(self):
        dialog = QDialog(self.item_dialog)
        item_browser = qt_itembrowser.Ui_Dialog()
        item_browser.setupUi(dialog)
        self.item_browse_select = ""

        for cat in self.items.get_categories():
            item_browser.category.addItem(cat[0])

        all_items = self.items.get_all_items()

        item_browser.items.clear()
        for i in all_items:
            item_browser.items.addItem(i[0])

        def update_item_view():
            try:
                selected = item_browser.items.selectedItems()[0].text()
            except IndexError:
                return
            item = self.items.get_item(selected)
            try:
                icon = QtGui.QPixmap(item[2] + "/" + item[0]["image"]).scaledToHeight(64)
            except KeyError:
                icon = self.inv_icon(selected)
            item_browser.item_icon.setPixmap(icon)
            self.item_browse_select = selected
            # TODO: update qt objectnames, already not making sense
            try:
                item_browser.item_name.setText(item[0]["shortdescription"])
            except KeyError:
                item_browser.item_name.setText("Missing short description")
            try:
                item_browser.short_desc.setText(item[0]["description"])
            except KeyError:
                item_browser.short_desc.setText("Missing description")
            row = 0
            item_browser.info.setRowCount(len(item[0]))
            for key in item[0]:
                item_browser.info.setItem(row, 0, QTableWidgetItem(key))
                try:
                    item_browser.info.setItem(row, 1, QTableWidgetItem(str(item[0][key])))
                except TypeError:
                    pass
                row += 1

        def update_item_list():
            category = item_browser.category.currentText()
            name = item_browser.filter.text()
            result = self.items.filter_items(category, name)
            item_browser.items.clear()
            for i in result:
                item_browser.items.addItem(i[0])
            item_browser.items.setCurrentRow(0)

        item_browser.items.itemSelectionChanged.connect(update_item_view)
        item_browser.filter.textChanged.connect(update_item_list)
        item_browser.category.currentTextChanged.connect(update_item_list)
        dialog.accepted.connect(self.write_item_browser)

        item_browser.items.setCurrentRow(0)

        dialog.show()

    def write_item_browser(self):
        self.item_edit.item_type.setText(self.item_browse_select)
        self.item_edit.count.setValue(1)

    # TODO: move to separate class
    def new_item_edit(self, bag):
        """Display an item edit dialog for the selected cell in a given bag."""
        self.item_dialog = QDialog(self.window)
        self.item_edit = qt_itemedit.Ui_Dialog()
        self.item_edit.setupUi(self.item_dialog)

        item = bag.currentItem()
        # cells don't retain ItemSlot widget when they've been dragged away
        if type(item) is QTableWidgetItem or item == None:
            item = self.empty_slot()

        # set up signals
        self.item_dialog.accepted.connect(self.write_item_edit)
        self.item_edit.load_button.clicked.connect(self.new_item_browser)
        self.item_edit.trash_button.clicked.connect(self.trash_item_edit)

        # set type text box
        self.item_edit.item_type.setText(item.type_name)
        # set item count spinbox
        self.item_edit.count.setValue(int(item.item_count))

        if item.type_name != "":
            self.item_edit.icon.setPixmap(self.inv_icon(item.type_name))

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

    def trash_item_edit(self):
        bag = getattr(self.ui, self.item_bag)
        row = bag.currentRow()
        column = bag.currentColumn()
        bag.setItem(row, column, self.empty_slot())
        self.item_dialog.close()

    # these are used for connecting the item edit dialog to bag tables
    def new_main_bag_item_edit(self):
        self.item_bag = "main_bag"
        self.new_item_edit(self.ui.main_bag)

    def new_tile_bag_item_edit(self):
        self.item_bag = "tile_bag"
        self.new_item_edit(self.ui.tile_bag)

    def new_action_bar_item_edit(self):
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

    def new_wieldable_item_edit(self):
        self.item_bag = "wieldable"
        self.new_item_edit(self.ui.wieldable)

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

    # get items from given equipment slot
    def get_equip(self, name):
        equip = getattr(self.ui, name)
        main_cell = equip.item(0, 0)
        glamor_cell = equip.item(0, 1)
        if main_cell == None or type(main_cell) is QTableWidgetItem:
            main = save_file.empty_slot()
        else:
            main = (main_cell.type_name, main_cell.item_count, main_cell.variant)
        if glamor_cell == None or type(glamor_cell) is QTableWidgetItem:
            glamor = save_file.empty_slot()
        else:
            glamor = (glamor_cell.type_name, glamor_cell.item_count, glamor_cell.variant)
        return main, glamor

    def get_bag(self, name):
        row = column = 0
        bag = getattr(self.player, "get_" + name)()
        for i in range(len(bag)):
            item = getattr(self.ui, name).item(row, column)
            if type(item) is QTableWidgetItem or item == None:
                item = self.empty_slot()
            count = item.item_count
            item_type = item.type_name
            # TODO: variant update support
            variant = bag[i][2]
            bag[i] = (item_type, int(count), variant)
            column += 1
            if (column % 10) == 0:
                row += 1
                column = 0
        return bag

    def save(self):
        """Update internal player dict with GUI values and export to file."""
        # TODO: everything here should be a setter in PlayerSave
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

        # might need to update equipment? not sure

        # save and show status
        self.player.dump()
        self.player.export_save(self.player.filename)
        self.ui.statusbar.showMessage("Saved " + self.player.filename, 3000)

    def update(self):
        """Update all GUI widgets with values from PlayerSave instance."""
        # uuid / save version
        self.ui.uuid_label.setText(self.player.get_uuid())
        self.ui.ver_label.setText("v" + self.player.get_save_ver())
        # name
        self.ui.name.setText(self.player.get_name())
        # race
        self.ui.race.setCurrentText(self.player.get_race())
        # pixels
        self.ui.pixels.setValue(self.player.get_pixels())
        # description
        self.ui.description.setPlainText(self.player.get_description())
        # gender
        getattr(self.ui, self.player.get_gender()).toggle()

        # stats
        stats = "health", "energy", "food", "breath"
        for stat in stats:
            cur_stat = getattr(self.player, "get_" + stat)()
            getattr(self.ui, stat).setMaximum(cur_stat[1])
            getattr(self.ui, stat).setValue(cur_stat[0])
            max_stat = getattr(self.player, "get_max_" + stat)()
            getattr(self.ui, "max_" + stat).setValue(max_stat)
            getattr(self, "update_" + stat)()
        # energy regen rate
        self.ui.energy_regen.setValue(self.player.get_energy_regen())
        # warmth
        cur_warmth = self.player.get_warmth()
        max_warmth = self.player.get_max_warmth()
        self.ui.warmth.setMinimum(cur_warmth[0])
        self.ui.warmth.setMaximum(max_warmth)
        self.ui.warmth.setValue(cur_warmth[1])
        self.ui.max_warmth.setValue(max_warmth)
        self.update_warmth()

        # equipment
        equip_bags = "head", "chest", "legs", "back"
        for bag in equip_bags:
            items = [ItemWidget(x, self.inv_icon(x[0])) for x in getattr(self.player, "get_" + bag)()]
            getattr(self.ui, bag).setItem(0, 0, items[0])
            getattr(self.ui, bag).setItem(0, 1, items[1])

        # wielded
        self.update_bag("wieldable")

        # bags
        self.update_bag("main_bag")
        self.update_bag("tile_bag")
        self.update_bag("action_bar")

    def update_bag(self, bag_name):
        row = column = 0
        bag = getattr(self.player, "get_" + bag_name)()
        for slot in range(len(bag)):
            widget = ItemWidget(bag[slot], self.inv_icon(bag[slot][0]))
            getattr(self.ui, bag_name).setItem(row, column, widget)
            column += 1
            if (column % 10) == 0:
                row += 1
                column = 0

    def reload(self):
        """Reload the currently open save file and update GUI values."""
        self.player = save_file.PlayerSave(self.player.filename)
        self.update()
        self.ui.statusbar.showMessage("Reloaded " + self.player.filename, 3000)

    def open_file(self):
        """Display open file dialog and load selected save."""
        filename = QFileDialog.getOpenFileName(self.window,
                                               'Open save file...',
                                               config["starbound_folder"] + '/player',
                                               '*.player')
        self.player = save_file.PlayerSave(filename[0])
        self.update()
        self.ui.statusbar.showMessage("Opened " + self.player.filename, 3000)

if __name__ == '__main__':
    window = MainWindow()
