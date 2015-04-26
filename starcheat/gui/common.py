"""
Functions shared between GUI dialogs
"""

import re

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage

from PIL.ImageQt import ImageQt

import qt_listedit

from assets.common import string_color
from assets.common import colors


def find_color(text):
    match = re.search("\^(\w+);", text)
    if match is not None:
        return match.groups()[0]


def replace_color(name, text):
    span_template = '<span style="color: %s">'
    return text.replace("^%s;" % name,
                        span_template % name)


def text_to_html(text):
    """Convert Starbound text to colored HTML."""
    colored = text
    match = find_color(colored)
    if match is None:
        return text
    while match is not None:
        colored = replace_color(match, colored)
        match = find_color(colored)
    return colored + ("</span>" * colored.count("<span"))


def setup_color_menu(parent, widget):
    def color_dialog():
        color = QInputDialog.getItem(parent, "Select Color",
                                     "Colors", colors)
        widget.insert(string_color(color[0]))
    widget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    action = QAction("Insert Color...", widget)
    action.triggered.connect(color_dialog)
    widget.addAction(action)


def inv_icon(item_name, item_data, assets):
    """Return a QPixmap object of the inventory icon of a given item (if possible)."""
    missing = QPixmap.fromImage(QImage.fromData(assets.items().missing_icon())).scaled(32, 32)
    icon_file = assets.items().get_item_icon(item_name)

    if icon_file is None:
        try:
            image_file = assets.items().get_item_image(item_name)
            image_file = assets.images().color_image(image_file, item_data)
            return QPixmap.fromImage(ImageQt(image_file)).scaledToHeight(64)
        except (TypeError, AttributeError):
            return missing

    icon_file = assets.images().color_image(icon_file, item_data)
    try:
        return QPixmap.fromImage(ImageQt(icon_file)).scaled(32, 32)
    except AttributeError:
        return missing


def empty_slot():
    """Return an empty bag slot widget."""
    return ItemWidget(None)


# TODO: a decision needs to be made here whether to continue with the custom
#       widget item or an entirely new custom table view. if the features below
#       are easy enough to add then we'll just stick with the current method
# TODO: swap items instead of overwriting
#       apparently this is done by reimplementing the drag functions
class ItemWidget(QTableWidgetItem):
    """Custom table wiget item with icon support and extra item variables."""
    def __init__(self, item, assets=None):
        if item is None or assets is None or "name" not in item:
            # empty slot
            self.item = None
            QTableWidgetItem.__init__(self)
            return

        self.assets = assets
        self.item = item

        QTableWidgetItem.__init__(self, self.item["name"])
        self.setTextAlignment(QtCore.Qt.AlignCenter)

        name = self.item["name"]
        try:
            asset_name = assets.items().get_item(name)[3]
            if asset_name != "":
                name = asset_name
        except TypeError:
            pass

        self.setToolTip(name + " (" + str(self.item["count"]) + ")")

        icon = inv_icon(self.item["name"], self.item["parameters"], assets)
        try:
            self.setIcon(QtGui.QIcon(icon))
        except TypeError:
            pass

        if type(icon) is QPixmap:
            self.setText("")


class ListEdit():
    def __init__(self, parent, list_data):
        self.dialog = QDialog(parent)
        self.ui = qt_listedit.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.ui.add_button.clicked.connect(self.add_item)
        self.ui.remove_button.clicked.connect(self.remove_item)

        self.data = list_data

        self.update()

    def new_item(self, text):
        widget = QListWidgetItem(str(text))
        widget.setFlags(QtCore.Qt.ItemIsEditable |
                        QtCore.Qt.ItemIsEnabled |
                        QtCore.Qt.ItemIsSelectable)
        return widget

    def update(self):
        self.ui.list.clear()
        for i in self.data:
            widget = self.new_item(i)
            self.ui.list.addItem(widget)

    def get_list(self):
        list_data = []

        for i in range(self.ui.list.count()):
            list_data.append(self.ui.list.item(i).text())

        self.data = list_data
        return self.data

    def add_item(self):
        self.ui.list.addItem(self.new_item("teleport"))

    def remove_item(self):
        selected = self.ui.list.currentRow()
        if selected is not None:
            self.ui.list.takeItem(selected)
