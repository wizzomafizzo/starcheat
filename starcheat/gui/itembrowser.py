"""
Qt item browser dialog
"""

import logging

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage
from PIL.ImageQt import ImageQt

import qt_itembrowser

# TODO: use parent assets
from assets.core import Assets
from config import Config
from gui.common import text_to_html


def format_status_effects(data):
    info = "<b>Status Effects:</b><br>"
    for status in data:
        if type(status) is str:
            info += "%s<br>" % status
        elif "amount" in status.keys():
            info += "%s (%s)<br>" % (status["stat"], str(status["amount"]))
        elif "effect" in status.keys():
            info += "%s<br>" % status["effect"]
        else:
            info += "%s<br>" % status["stat"]
    return info


def format_effects(data):
    info = "<b>Effects:</b><br>"
    for status in data[0]:
        if type(status) is str:
            info += "%s<br>" % status
        elif type(status) is dict:
            if "effect" in status.keys():
                if "duration" in status.keys():
                    info += "%s (%s)<br>" % (status["effect"], str(status["duration"]))
                else:
                    info += "%s<br>" % status["effect"]
            # NOTE: old style effect, potentially remove later
            elif "kind" in status.keys():
                if "amount" in status.keys():
                    info += "%s (%s)<br>" % (status["kind"], str(status["amount"]))
                else:
                    info += "%s<br>" % status["kind"]

    return info


data_format = (
    # (key name, format/func)
    # key name is name of the key in item data it corresponds to
    # format/func is either a format string with 1 %s replacement that the
    # key gets passed to or a function that outputs a string using the option
    # as input
    # order matters
    ("shortdescription", "<b>%s</b> "),
    ("itemName", "(%s)<br>"),
    ("objectName", "(%s)<br>"),
    ("description", "%s<br><br>"),
    ("inspectionKind", "<b>Type:</b> %s<br>"),
    ("rarity", "<b>Rarity:</b> %s<br><br>"),
    ("statusEffects", format_status_effects),
    ("effects", format_effects),
    ("blockRadius", "<b>Mining Radius:</b> %s blocks")
)


def generate_item_info(item_data):
    """Takes inventory item data and makes a detailed description (HTML)."""
    info = ""

    if item_data is None:
        return ""

    for fmt in data_format:
        if fmt[0] in item_data:
            try:
                if type(fmt[1]) is str:
                    info += fmt[1] % text_to_html(str(item_data[fmt[0]]))
                else:
                    info += fmt[1](item_data[fmt[0]])
            except:
                logging.exception("Error parsing %s key", fmt[0])

    return info


class BrowserItem(QListWidgetItem):
    def __init__(self, name, desc):
        if desc == "":
            display = name
        else:
            # display = "%s (%s)" % (desc, name)
            display = desc
        QListWidgetItem.__init__(self, display)
        self.name = name


class ItemBrowser(object):
    def __init__(self, parent, just_browse=False, category="<all>"):
        """Dialog for viewing/searching indexed items and returning selection."""
        self.dialog = QDialog(parent)
        self.ui = qt_itembrowser.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.assets = Assets(assets_db_file, starbound_folder)

        self.remember_category = category

        if just_browse:
            self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.item_browse_select = None
        self.items = self.assets.items()

        # populate category combobox
        for cat in self.items.get_categories():
            self.ui.category.addItem(cat[0])
        self.ui.category.setCurrentText(self.remember_category)

        # populate initial items list
        self.ui.items.clear()
        self.update_item_list()
        self.update_item_view()

        self.ui.items.itemSelectionChanged.connect(self.update_item_view)
        if not just_browse:
            self.ui.items.itemDoubleClicked.connect(self.dialog.accept)
        self.ui.filter.textChanged.connect(self.update_item_list)
        self.ui.category.currentTextChanged.connect(self.update_item_list)

        self.ui.items.setCurrentRow(0)
        self.ui.filter.setFocus()

    def update_item_view(self):
        """Update item details view with data from currently selected item."""
        try:
            selected = self.ui.items.selectedItems()[0].name
        except IndexError:
            return

        try:
            item = self.items.get_item(selected)
        except TypeError:
            logging.warning("Unable to load asset "+selected)
            return

        inv_icon_file = self.items.get_item_icon(selected)
        if inv_icon_file is not None:
            icon = QPixmap.fromImage(ImageQt(inv_icon_file))
        else:
            image_file = self.items.get_item_image(selected)
            if image_file is not None:
                icon = QPixmap.fromImage(ImageQt(image_file))
            else:
                icon = QPixmap.fromImage(QImage.fromData(self.assets.items().missing_icon()))

        # last ditch
        try:
            icon = self.scale_image_icon(icon, 64, 64)
            self.ui.item_icon.setPixmap(icon)
        except TypeError:
            logging.warning("Unable to load item image: "+selected)
            self.ui.item_icon.setPixmap(QPixmap())

        self.ui.short_desc.setText(generate_item_info(item[0]))

        # populate default variant table

        try:
            row = 0
            self.ui.info.setRowCount(len(item[0]))
            for key in sorted(item[0].keys()):
                text = str(key) + ": " + str(item[0][key])
                table_item = QTableWidgetItem(text)
                table_item.setToolTip(text)
                self.ui.info.setItem(row, 0, table_item)
                row += 1
        except TypeError:
            self.ui.info.setRowCount(0)
            logging.error("No item data")

        self.item_browse_select = selected

    def scale_image_icon(self, qpix, width, height):
        """Scales the image icon to best fit in the width and height bounds given. Preserves aspect ratio."""
        scaled_qpix = qpix
        src_width = qpix.width()
        src_height = qpix.height()

        if src_width == src_height and width == height:  # square image and square bounds
            scaled_qpix = qpix.scaled(width, height)
        elif src_width > src_height:  # wider than tall needs width scaling to fit
            scaled_qpix = qpix.scaledToWidth(width)
        elif src_height > src_width:  # taller than wide needs height scaling to fit
            scaled_qpix = qpix.scaledToHeight(height)
        return scaled_qpix

    def update_item_list(self):
        """Populate item list based on current filter details."""
        category = self.ui.category.currentText()
        self.remember_category = category
        name = self.ui.filter.text()
        result = self.items.filter_items(category, name)

        self.ui.items.clear()
        for item in result:
            self.ui.items.addItem(BrowserItem(item[4], item[5]))
        self.ui.items.setCurrentRow(0)

    def get_selection(self):
        return self.item_browse_select
