"""
Qt item edit dialog
"""

# TODO: the variant editing stuff would work much better as a tree view,
# especially considering the upcoming change

# TODO: a function to convert from an asset item to a valid inventory item
# once that's complete, work can be started on proper item generation. to begin,
# we just wanna pull in all the default values of an item

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QInputDialog
from PyQt5.QtGui import QPixmap

import assets, qt_itemedit, qt_variantedit, logging
from gui_common import inv_icon, ItemWidget, empty_slot
from gui_itembrowser import ItemBrowser

class ItemVariant(QTableWidgetItem):
    def __init__(self, key, value):
        self.variant = key, value

        item_text = key + ": " + str(value)
        QTableWidgetItem.__init__(self, item_text)
        self.setToolTip(item_text)

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
            self.item = item

        # set up signals
        self.ui.load_button.clicked.connect(self.new_item_browser)
        self.ui.item_type.textChanged.connect(self.update_item)

        try:
            # set name text box
            self.ui.item_type.setText(self.item.name)
            # set item count spinbox
            self.ui.count.setValue(int(self.item.item_count))

            # set up variant table
            self.ui.variant.setRowCount(len(self.item.variant))
            self.ui.variant.setHorizontalHeaderLabels(["Options"])
            row = 0
            print(self.item.variant)
            for k in self.item.variant.keys():
                variant = ItemVariant(k, self.item.variant[k])
                self.ui.variant.setItem(row, 0, variant)
                row += 1
        except AttributeError:
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
            self.ui.short_desc.setText("")
            self.ui.desc.setText("")
            self.ui.icon.setPixmap(QPixmap())
            clear_variants()
            return

        try:
            self.ui.short_desc.setText(item[0]["shortdescription"])
        except KeyError:
            self.ui.short_desc.setText("Missing short description")

        try:
            self.ui.desc.setText(item[0]["description"])
        except KeyError:
            self.ui.desc.setText("Missing description")

        try:
            self.ui.icon.setPixmap(inv_icon(name))
        except TypeError:
            # TODO: change this to the x.png?
            self.ui.icon.setPixmap(QPixmap())

        clear_variants()

    def get_item(self):
        """Return an ItemWidget of the currently open item."""
        type_name = self.ui.item_type.text()
        count = self.ui.count.value()

        variant_rows = self.ui.variant.rowCount()
        variant = {}
        logging.debug(variant_rows)
        for i in range(variant_rows):
            cell = self.ui.variant.item(i, 0).variant
            variant[cell[0]] = cell[1]

        # TODO: move to save_file.py
        item = {
            "name": type_name,
            "count": count,
            "data": variant
        }

        return ItemWidget(item)

    def new_item_browser(self):
        self.item_browser = ItemBrowser(self.dialog)
        self.item_browser.dialog.accepted.connect(self.set_item_browser_selection)
        self.item_browser.dialog.exec()

    def set_item_browser_selection(self):
        self.ui.item_type.setText(self.item_browser.get_selection())
        # TODO: stuff like setting value max to maxstack
        self.ui.count.setValue(1)
