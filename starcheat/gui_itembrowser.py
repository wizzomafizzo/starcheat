"""
Qt item browser dialog
"""

from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QDialogButtonBox
from PyQt5.QtGui import QPixmap

import assets, qt_itembrowser
from gui_common import inv_icon

class ItemBrowser():
    def __init__(self, parent, just_browse=False):
        """Dialog for viewing/searching indexed items and returning selection."""
        self.dialog = QDialog(parent)
        self.ui = qt_itembrowser.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        if just_browse:
            self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.item_browse_select = None
        self.items = assets.Items()

        # populate category combobox
        for cat in self.items.get_categories():
            self.ui.category.addItem(cat[0])

        # populate initial items list
        self.ui.items.clear()
        for item in self.items.get_all_items():
            self.ui.items.addItem(item[0])

        self.ui.items.itemSelectionChanged.connect(self.update_item_view)
        self.ui.items.itemDoubleClicked.connect(self.dialog.accept)
        self.ui.filter.textChanged.connect(self.update_item_list)
        self.ui.category.currentTextChanged.connect(self.update_item_list)

        self.ui.items.setCurrentRow(0)
        self.ui.filter.setFocus()

    def update_item_view(self):
        """Update item details view with data from currently selected item."""
        try:
            selected = self.ui.items.selectedItems()[0].text()
        except IndexError:
            return

        item = self.items.get_item(selected)
        # don't like so many queries but should be ok for the browser
        icon_file = self.items.get_item_image(selected)
        # fallback on inventory icon
        if icon_file == None:
            icon = inv_icon(selected)
        else:
            icon = QPixmap(icon_file).scaledToHeight(64)

        # last ditch, just use x.png
        try:
            self.ui.item_icon.setPixmap(icon)
        except TypeError:
            self.ui.item_icon.setPixmap(QPixmap(self.items.missing_icon()))

        self.item_browse_select = selected

        # TODO: update qt objectnames, already not making sense
        try:
            self.ui.item_name.setText(item[0]["shortdescription"])
        except KeyError:
            self.ui.item_name.setText("Missing short description")

        try:
            self.ui.short_desc.setText(item[0]["description"])
        except KeyError:
            self.ui.short_desc.setText("Missing description")

        # populate default variant table
        row = 0
        self.ui.info.setRowCount(len(item[0]))
        for key in sorted(item[0].keys()):
            try:
                text = str(key) + ": " + str(item[0][key])
                table_item = QTableWidgetItem(text)
                table_item.setToolTip(text)
                self.ui.info.setItem(row, 0, table_item)
            except TypeError:
                pass
            row += 1

    def update_item_list(self):
        """Populate item list based on current filter details."""
        category = self.ui.category.currentText()
        name = self.ui.filter.text()
        result = self.items.filter_items(category, name)

        # TODO: i'd like this to set focus on the list when category is changed
        #       but not when the edit box is changed (split this function)
        self.ui.items.clear()
        for item in result:
            self.ui.items.addItem(item[0])
        self.ui.items.setCurrentRow(0)

    def get_selection(self):
        return self.item_browse_select
