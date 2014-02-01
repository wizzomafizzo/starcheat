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
import assets, qt_itemedit, qt_itemeditoptions, save_file
from gui_common import inv_icon, ItemWidget, empty_slot
from gui_itembrowser import ItemBrowser

class ItemEditOptions():
    def __init__(self, parent, options):
        self.dialog = QDialog(parent)
        self.ui = qt_itemeditoptions.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.item_options = options

        pretty_data = json.dumps(options, sort_keys=True,
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

        self.item_browser = None

        # cells don't retain ItemSlot widget when they've been dragged away
        if type(item) is QTableWidgetItem or item == None:
            self.item = empty_slot()
        else:
            self.item = item.item

        # set up signals
        self.ui.load_button.clicked.connect(self.new_item_browser)
        self.ui.item_type.textChanged.connect(self.update_item)
        self.ui.variant.itemDoubleClicked.connect(self.new_item_edit_options)

        try:
            # set name text box
            self.ui.item_type.setText(self.item["name"])
            # set item count spinbox
            self.ui.count.setValue(int(self.item["count"]))
            # set up variant table
            self.populate_options()
        except TypeError:
            # empty slot
            self.new_item_browser()

        self.ui.item_type.setFocus()
        self.dialog.show()

    def update_item(self):
        """Update main item view with current item browser data."""
        name = self.ui.item_type.text()

        def clear_variants():
            # TODO: we don't support importing variants from assets yet
            self.ui.variant.clear()
            # not sure why i need to do this too
            self.ui.variant.setRowCount(0)
            self.ui.variant.setHorizontalHeaderLabels(["Options"])

        try:
            item = assets.Items().get_item(name)
        except TypeError:
            self.ui.desc.setText("<html><body><strong>Empty Slot</strong></body></html>")
            self.ui.icon.setPixmap(QPixmap())
            clear_variants()
            return

        item_info = "<html><body>"

        try:
            item_info += "<strong>" + item[0]["shortdescription"] + "</strong>"
        except KeyError:
            pass

        try:
            item_info += "<p>" + item[0]["description"] + "</p>"
        except KeyError:
            pass

        item_info += "</body></html>"
        self.ui.desc.setText(item_info)

        try:
            self.ui.icon.setPixmap(inv_icon(name))
        except TypeError:
            # TODO: change this to the x.png?
            self.ui.icon.setPixmap(QPixmap())

        clear_variants()

    def get_item(self):
        """Return an ItemWidget of the currently open item."""
        name = self.ui.item_type.text()
        count = self.ui.count.value()

        variant_rows = self.ui.variant.rowCount()
        variant = {}
        for i in range(variant_rows):
            cell = self.ui.variant.item(i, 0).variant
            variant[cell[0]] = cell[1]

        item = save_file.new_item(name, count, variant)
        return ItemWidget(item)

    def new_item_edit_options(self):
        selected = self.ui
        item_edit_options = ItemEditOptions(self.dialog, self.item["data"])
        def save():
            new_options = json.loads(item_edit_options.ui.options.toPlainText())
            self.item["data"] = new_options
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
        self.ui.item_type.setText(self.item_browser.get_selection())
        # TODO: stuff like setting value max to maxstack
        self.ui.count.setValue(1)
