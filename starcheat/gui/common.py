"""
Functions shared between GUI dialogs
"""

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPixmap, QImage
from sqlite3 import OperationalError

from PIL.ImageQt import ImageQt

import assets
from config import Config

def inv_icon(item_name):
    """Return a QPixmap object of the inventory icon of a given item (if possible)."""
    assets_db_file = Config().read("assets_db")
    starbound_folder = Config().read("starbound_folder")
    db = assets.Assets(assets_db_file, starbound_folder)
    icon_file = db.items().get_item_icon(item_name)

    if icon_file == None:
        try:
            image_file = db.items().get_item_image(item_name)
            return QPixmap.fromImage(ImageQt(image_file)).scaledToHeight(64)
        except (TypeError, AttributeError):
            return QPixmap.fromImage(QImage.fromData(db.items().missing_icon())).scaled(32, 32)

    try:
        return QPixmap.fromImage(ImageQt(icon_file)).scaled(32, 32)
    except AttributeError:
        return QPixmap.fromImage(QImage.fromData(db.items().missing_icon())).scaled(32, 32)

def preview_icon(race, gender):
    """Return an icon image for player race/gender previews."""
    assets_db_file = Config().read("assets_db")
    starbound_folder = Config().read("starbound_folder")
    db = assets.Assets(assets_db_file, starbound_folder)
    icon_file = db.species().get_preview_image(race, gender)
    return QPixmap.fromImage(QImage.fromData(icon_file))

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
    def __init__(self, item, assets=None):
        if item is None or assets is None or "name" not in item:
            # empty slot
            self.item = None
            QTableWidgetItem.__init__(self)
            return

        self.item = item
        QTableWidgetItem.__init__(self, self.item["name"])
        self.setTextAlignment(QtCore.Qt.AlignCenter)

        name = self.item["name"]
        if "shortdescription" in self.item["data"]:
            name = self.item["data"]["shortdescription"]
        else:
            try:
                asset_name = assets.items().get_item(name)[3]
                if asset_name != "":
                    name = asset_name
            except TypeError:
                pass

        self.setToolTip(name + " (" + str(self.item["count"]) + ")")

        icon = inv_icon(self.item["name"])
        try:
            self.setIcon(QtGui.QIcon(icon))
        except TypeError:
            pass

        if type(icon) is QPixmap:
            self.setText("")
