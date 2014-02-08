"""
Qt item edit dialog
"""

# TODO: the variant editing stuff would work much better as a tree view,
# especially considering the upcoming change

# TODO: a function to convert from an asset item to a valid inventory item
# once that's complete, work can be started on proper item generation. to begin,
# we just wanna pull in all the default values of an item

from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QDialogButtonBox
from PyQt5.QtGui import QPixmap

import json
import assets, qt_itemedit, qt_itemeditoptions, saves
from gui.common import inv_icon, ItemWidget, empty_slot
from gui.itembrowser import ItemBrowser
from config import Config

class ItemEditOptions():
    def __init__(self, parent, key, value):
        self.dialog = QDialog(parent)
        self.ui = qt_itemeditoptions.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.option = key, value

        self.ui.name_label.setText(key)

        pretty_data = json.dumps(value, sort_keys=True,
                                 indent=4, separators=(',', ': '))
        self.ui.options.setPlainText(pretty_data)

        self.ui.options.textChanged.connect(self.validate_options)
        self.validate_options()

    def validate_options(self):
        valid = "Item option is valid."
        invalid = "Item option invalid: %s"
        try:
            json.loads(self.ui.options.toPlainText())
            self.ui.valid_label.setStyleSheet("color: green")
            self.ui.valid_label.setText(valid)
            self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        except ValueError as err:
            self.ui.valid_label.setStyleSheet("color: red")
            self.ui.valid_label.setText(invalid % err)
            # this would be nicer if it just disabled the save button
            self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Cancel)

class ItemOptionWidget(QTableWidgetItem):
    def __init__(self, key, value):
        self.option = key, value
        item_text = key + ": " + str(value)
        QTableWidgetItem.__init__(self, item_text)
        self.setToolTip(str(value))

class ItemEdit():
    def __init__(self, parent, item=None):
        """Takes an item widget and displays an edit dialog for it."""
        self.dialog = QDialog(parent)
        self.ui = qt_itemedit.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.assets = assets.Assets(assets_db_file, starbound_folder)

        self.item_browser = None

        # cells don't retain ItemSlot widget when they've been dragged away
        if type(item) is QTableWidgetItem or item == None:
            self.item = empty_slot()
        else:
            self.item = item.item

        try:
            # set name text box
            self.ui.item_type.setText(self.item["name"])
            # set item count spinbox
            self.ui.count.setValue(int(self.item["count"]))
            # set up variant table
            self.populate_options()
            self.update_item_info(self.item["name"], self.item["data"])
        except TypeError:
            # empty slot
            self.new_item_browser()
            self.update_item()

        # set up signals
        self.ui.load_button.clicked.connect(self.new_item_browser)
        self.ui.item_type.textChanged.connect(self.update_item)
        self.ui.variant.itemDoubleClicked.connect(self.new_item_edit_options)
        self.ui.clear_options_button.clicked.connect(self.clear_item_options)

        self.ui.item_type.setFocus()

    def update_item_info(self, name, data):
        item_info = "<html><body>"

        try:
            item_info += "<strong>" + data["shortdescription"] + "</strong>"
        except KeyError:
            try:
                item_info += "<strong>" + self.assets.items().get_item(name)[0]["shortdescription"] + "</strong>"
            except:
                pass

        try:
            item_info += "<p>" + data["description"] + "</p>"
        except KeyError:
            pass

        item_info += "</body></html>"
        self.ui.desc.setText(item_info)

        try:
            self.ui.icon.setPixmap(inv_icon(name))
        except TypeError:
            # TODO: change this to the x.png?
            self.ui.icon.setPixmap(QPixmap())

    def update_item(self):
        """Update main item view with current item browser data."""
        name = self.ui.item_type.text()

        try:
            item = self.assets.items().get_item(name)
        except TypeError:
            self.item = empty_slot().item
            self.ui.desc.setText("<html><body><strong>Empty Slot</strong></body></html>")
            self.ui.icon.setPixmap(QPixmap())
            self.ui.variant.clear()
            self.ui.variant.setHorizontalHeaderLabels(["Options"])
            return

        self.item = saves.new_item(name, 1, item[0])
        self.ui.count.setValue(1)
        self.update_item_info(name, item[0])
        self.populate_options()

    def get_item(self):
        """Return an ItemWidget of the currently open item."""
        name = self.ui.item_type.text()
        count = self.ui.count.value()
        data = {}
        for i in range(self.ui.variant.rowCount()):
            option = self.ui.variant.item(i, 0).option
            data[option[0]] = option[1]
        item = saves.new_item(name, count, data)
        return ItemWidget(item)

    def clear_item_options(self):
        self.ui.variant.clear()
        self.ui.variant.setHorizontalHeaderLabels(["Options"])
        self.ui.variant.setRowCount(0)

    def new_item_edit_options(self):
        selected = self.ui.variant.currentItem()
        item_edit_options = ItemEditOptions(self.dialog, selected.option[0], selected.option[1])
        def save():
            new_option = json.loads(item_edit_options.ui.options.toPlainText())
            name = item_edit_options.option[0]
            self.item["data"][name] = new_option
            # TODO: update the item info. not working for some reason
            self.populate_options()
        item_edit_options.dialog.accepted.connect(save)
        item_edit_options.dialog.exec()

    def new_item_browser(self):
        self.item_browser = ItemBrowser(self.dialog)
        self.item_browser.dialog.accepted.connect(self.set_item_browser_selection)
        self.item_browser.dialog.exec()

    def populate_options(self):
        self.ui.variant.setRowCount(len(self.item["data"]))
        self.ui.variant.setHorizontalHeaderLabels(["Options"])
        row = 0
        for k in sorted(self.item["data"].keys()):
            variant = ItemOptionWidget(k, self.item["data"][k])
            self.ui.variant.setItem(row, 0, variant)
            row += 1

    def set_item_browser_selection(self):
        name = self.item_browser.get_selection()
        self.ui.item_type.setText(name)
