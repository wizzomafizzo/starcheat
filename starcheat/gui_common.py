"""
Functions shared between GUI dialogs
"""

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPixmap, QImageReader

import save_file, assets

def inv_icon(item_name):
    """Return a QPixmap object of the inventory icon of a given item (if possible)."""
    icon_file = assets.Items().get_item_icon(item_name)

    if icon_file == None:
        return QPixmap()

    reader = QImageReader(icon_file[0])
    reader.setClipRect(QtCore.QRect(icon_file[1], 0, 16, 16))
    return QPixmap.fromImageReader(reader).scaled(32, 32)

def preview_icon(race, gender):
    """Return an icon image for player race/gender previews."""
    icon_file = assets.Species().get_preview_image(race, gender)

    reader = QImageReader(icon_file)
    reader.setClipRect(QtCore.QRect(0, 0, 32, 32))
    return QPixmap.fromImageReader(reader)

def empty_slot():
    """Return an empty bag slot widget."""
    return ItemWidget(None)

# TODO: a decision needs to be made here whether to continue with the custom
#       widget item or an entirely new custom table view. if the features below
#       are easy enough to add then we'll just stick with the current method
# TODO: swap items instead of overwriting
#       apparently this is done by reimplementing the drag functions
# TODO: some sort of icon painter so we can show a frame, rarity and count overlay
class ItemWidget(QTableWidgetItem):
    """Custom table wiget item with icon support and extra item variables."""
    def __init__(self, item):
        if item is None:
            # empty slot
            QTableWidgetItem.__init__(self)
            return

        self.name = item["name"]
        self.item_count = item["count"]
        self.variant = item["data"]
        QTableWidgetItem.__init__(self, self.name)
        self.setTextAlignment(QtCore.Qt.AlignCenter)

        if self.name != "":
            self.setToolTip(self.name + " (" + str(self.item_count) + ")")
        else:
            return

        icon = inv_icon(self.name)
        try:
            self.setIcon(QtGui.QIcon(icon))
        except TypeError:
            pass

        if type(icon) is QPixmap:
            #self.setText(str(self.item_count))
            self.setText("")
