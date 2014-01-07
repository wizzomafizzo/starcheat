"""
Qt item edit dialog
"""

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QInputDialog
from PyQt5.QtGui import QPixmap

import assets, qt_itemedit, logging
from gui_common import inv_icon, pretty_variant, ItemWidget, empty_slot
from gui_itembrowser import ItemBrowser

class ItemVariant(QTableWidgetItem):
    def __init__(self, variant):
        self.variant_name = variant[0]
        self.variant_type = variant[1][0]
        self.variant_value = variant[1][1]

        item_text = self.variant_name + ": " + pretty_variant(variant[1])
        QTableWidgetItem.__init__(self, item_text)
        self.setToolTip(item_text)
        logging.debug(variant)

    def get_variant(self):
        """Return the full variant in the proper format."""
        return (self.variant_name, (self.variant_type, self.variant_value))

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
        self.ui.variant.cellDoubleClicked.connect(self.edit_variant)

        # set name text box
        self.ui.item_type.setText(self.item.name)
        # set item count spinbox
        self.ui.count.setValue(int(self.item.item_count))

        # set up variant table
        self.ui.variant.setRowCount(len(self.item.variant[1]))
        for i in range(len(self.item.variant[1])):
            variant = ItemVariant(self.item.variant[1][i])
            self.ui.variant.setItem(i, 0, variant)

        self.ui.item_type.setFocus()

        self.dialog.show()

        # if the inventory slot is empty show the browser as well
        if self.item.name == "":
            self.new_item_browser()

    def update_item(self):
        """Update main item view with current item browser data."""
        name = self.ui.item_type.text()

        def clear_variants():
            # TODO: we don't support importing variants from assets yet
            self.ui.variant.clear()
            # not sure why i need to do this too
            self.ui.variant.setRowCount(0)

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
        variant = []
        logging.debug(variant_rows)
        for i in range(variant_rows):
            cell = self.ui.variant.item(i, 0)
            variant.append(cell.get_variant())

        return ItemWidget((type_name, count, (7, variant)))

    def new_item_browser(self):
        self.item_browser = ItemBrowser(self.dialog)
        self.item_browser.dialog.accepted.connect(self.set_item_browser_selection)
        self.item_browser.dialog.show()

    def set_item_browser_selection(self):
        self.ui.item_type.setText(self.item_browser.get_selection())
        # TODO: stuff like setting value max to maxstack
        self.ui.count.setValue(1)

    def edit_variant(self):
        selected = self.ui.variant.currentItem()
        current_row = self.ui.variant.currentRow()
        new_variant = None

        if selected.variant_type == 2:
            # double
            dialog = QInputDialog.getDouble(self.dialog,
                                            "Edit Value",
                                            selected.variant_name,
                                            selected.variant_value[0],
                                            decimals=2)
            if dialog[1]:
                # didn't realise i was writing lisp
                new_variant = ItemVariant((selected.variant_name, (selected.variant_type, (dialog[0],))))
        elif selected.variant_type == 3:
            # bool
            if selected.variant_value[0] == 1:
                text = "True"
            else:
                text = "False"

            dialog = QInputDialog.getText(self.dialog,
                                          "Edit Value (True/False)",
                                          selected.variant_name,
                                          QtWidgets.QLineEdit.Normal,
                                          text)
            if dialog[1]:
                if dialog[0] == "True":
                    val = (1,)
                else:
                    val = (0,)

                new_variant = ItemVariant((selected.variant_name, (selected.variant_type, val)))
        elif selected.variant_type == 4:
            # int (vlq)
            dialog = QInputDialog.getInt(self.dialog,
                                         "Edit Value",
                                         selected.variant_name,
                                         selected.variant_value)
            if dialog[1]:
                new_variant = ItemVariant((selected.variant_name, (selected.variant_type, dialog[0])))
        elif selected.variant_type == 5:
            # string
            dialog = QInputDialog.getText(self.dialog,
                                          "Edit Value",
                                          selected.variant_name,
                                          QtWidgets.QLineEdit.Normal,
                                          selected.variant_value)
            if dialog[1]:
                new_variant = ItemVariant((selected.variant_name, (selected.variant_type, dialog[0])))
        elif selected.variant_type == 6:
            # TODO: both of these will require a fair bit of work
            #       i'd like a recurive variant table
            # variant list
            pass
        elif selected.variant_type == 7:
            # variant dicts
            pass

        if new_variant != None:
            self.ui.variant.setItem(current_row, 0, new_variant)
