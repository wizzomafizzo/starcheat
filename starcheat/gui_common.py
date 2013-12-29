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

def empty_slot():
    """Return an empty bag slot widget."""
    return ItemWidget(save_file.empty_slot())

def pretty_variant(variant):
    variant_type = variant[0]
    variant_value = variant[1]
    if variant_type == 2:
        return str(variant_value[0])
    elif variant_type == 3:
        if variant_value[0] == 1:
            return "True"
        else:
            return "False"
    elif variant_type == 4:
        return str(variant_value)
    elif variant_type == 5:
        return '"' + str(variant_value) + '"'
    elif variant_type == 6:
        items = []
        for i in variant_value:
            items.append(pretty_variant(i))
        return ", ".join(items)
    elif variant_type == 7:
        items = []
        for i in variant_value:
            items.append(i[0] + ": " + pretty_variant(i[1]))
        return "{ " + ", ".join(items) + " }"
    else:
        return "__UNKNOWN_TYPE__"

# TODO: a decision needs to be made here whether to continue with the custom
#       widget item or an entirely new custom table view. if the features below
#       are easy enough to add then we'll just stick with the current method
# TODO: swap items instead of overwriting
#       apparently this is done by reimplementing the drag functions
# TODO: some sort of icon painter so we can show a frame, rarity and count overlay
class ItemWidget(QTableWidgetItem):
    """Custom table wiget item with icon support and extra item variables."""
    def __init__(self, item):
        self.name = item[0]
        self.item_count = item[1]
        self.variant = item[2]
        QTableWidgetItem.__init__(self, self.name)
        self.setTextAlignment(QtCore.Qt.AlignCenter)

        # TODO: remove this
        print(self.variant)

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
