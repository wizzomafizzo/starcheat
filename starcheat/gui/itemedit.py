"""
Qt item edit dialog
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QDialogButtonBox, QMessageBox
from PyQt5.QtWidgets import QInputDialog, QListWidgetItem, QFileDialog, QAction
from PyQt5.QtGui import QPixmap, QImage
from PIL.ImageQt import ImageQt

import json, copy, logging
import re

import assets, qt_itemedit, qt_itemeditoptions, saves
import qt_imagebrowser
from gui.common import inv_icon, empty_slot
from gui.itembrowser import ItemBrowser, generate_item_info
from config import Config


def import_json(parent):
    filename = QFileDialog.getOpenFileName(parent,
                                           "Import Item File",
                                           filter="JSON (*.json);;All Files (*)")

    if filename[0] == "":
        return None

    def parse():
        try:
            item_data = json.load(open(filename[0], "r"))
        except:
            logging.exception("Error parsing item: %s", filename[0])
            return False
        if "name" not in item_data:
            return False
        if "count" not in item_data:
            item_data["count"] = 1
        if "parameters" not in item_data:
            item_data["parameters"] = {}
        return item_data

    item = parse()
    if not item:
        logging.warning("Invalid item file: %s", filename[0])
        return False
    else:
        return saves.new_item_data(item["name"],
                                   item["count"],
                                   item["parameters"])


class ItemEditOptions():
    def __init__(self, parent, key, value):
        self.dialog = QDialog(parent)
        self.ui = qt_itemeditoptions.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.option = key, value

        self.ui.name.setText(key)

        pretty_data = json.dumps(value, sort_keys=True,
                                 indent=4, separators=(',', ': '))
        self.ui.options.setPlainText(pretty_data)

        self.ui.options.textChanged.connect(self.validate_options)
        self.ui.name.textChanged.connect(self.validate_options)
        self.validate_options()

        self.ui.name.setFocus()

    def validate_options(self):
        valid = "Item option is valid."
        invalid = "Item option invalid: %s"

        if self.ui.name.text() == "":
            self.ui.valid_label.setStyleSheet("color: red")
            self.ui.valid_label.setText(invalid % "Option name is empty")
            self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Cancel)
            return

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

    def get_option(self):
        return self.ui.name.text(), json.loads(self.ui.options.toPlainText())

class ImageBrowser():
    def __init__(self, parent, assets, just_browse=True):
        self.dialog = QDialog(parent)
        self.ui = qt_imagebrowser.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.assets = assets

        if just_browse:
            self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        else:
            self.ui.results.itemDoubleClicked.connect(self.dialog.accept)

        self.ui.search_button.clicked.connect(self.search)
        self.ui.results.currentItemChanged.connect(self.set_preview)

    def search(self):
        query = self.ui.search.text()
        results = self.assets.images().filter_images(query)
        self.ui.results.clear()
        for image in results:
            self.ui.results.addItem(QListWidgetItem(image[0]))

    def set_preview(self):
        if self.ui.results.currentItem() is None:
            self.ui.image.setPixmap(QPixmap())
            return

        key = self.ui.results.currentItem().text()
        image = QPixmap.fromImage(ImageQt(self.assets.images().get_image(key)))
        # TODO: scale image up
        self.ui.image.setPixmap(image)
        self.ui.asset_path.setText(key)

    def get_key(self):
        if self.ui.results.currentItem() is None:
            return ""
        else:
            return self.ui.results.currentItem().text()

class ItemOptionWidget(QTableWidgetItem):
    def __init__(self, key, value):
        self.option = key, value
        item_text = key + ": " + str(value)
        QTableWidgetItem.__init__(self, item_text)
        self.setToolTip(str(value))

class ItemEdit():
    def __init__(self, parent, item, player, assets, browser_category="<all>"):
        """Takes an item widget and displays an edit dialog for it."""
        self.dialog = QDialog(parent)
        self.ui = qt_itemedit.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.assets = assets
        self.player = player

        self.remember_browser = browser_category
        self.item = item

        # set up signals
        self.ui.load_button.clicked.connect(self.new_item_browser)
        self.ui.variant.itemDoubleClicked.connect(lambda: self.new_item_edit_options(False))
        self.ui.max_button.clicked.connect(self.max_count)
        self.ui.add_option_button.clicked.connect(lambda: self.new_item_edit_options(True))
        self.ui.remove_option_button.clicked.connect(self.remove_option)
        self.ui.edit_option_button.clicked.connect(self.edit_option)
        self.ui.export_button.clicked.connect(self.export_item)
        self.ui.import_button.clicked.connect(self.import_item)
        self.ui.count.valueChanged.connect(self.toggle_max)

        self.make_context_menu()
        self.ui.item_type.setFocus()

    def launch(self):
        if self.item["name"] == "":
            # empty slot
            self.new_item_browser()
            if self.ui.item_type.text() == "":
                return False
        else:
            self.ui.item_type.setText(self.item["name"])
            self.ui.count.setValue(int(self.item["count"]))
            self.update()
        return True

    def update(self):
        self.populate_options()
        self.update_item_info(self.item["name"], self.item["parameters"])

    def make_context_menu(self):
        self.ui.variant.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        edit_action = QAction("Edit...", self.ui.variant)
        edit_action.triggered.connect(lambda: self.new_item_edit_options(False))
        self.ui.variant.addAction(edit_action)

        edit_raw_action = QAction("Edit Raw JSON...", self.ui.variant)
        edit_raw_action.triggered.connect(lambda: self.new_item_edit_options(False, True))
        self.ui.variant.addAction(edit_raw_action)

        remove_action = QAction("Remove", self.ui.variant)
        remove_action.triggered.connect(self.remove_option)
        self.ui.variant.addAction(remove_action)

    def update_item_info(self, name, data):
        item_info = "<html><body>"
        item_info += generate_item_info(data)
        item_info += "</body></html>"
        self.ui.desc.setText(item_info)

        inv_icon = self.assets.items().get_item_icon(name)
        image = self.assets.items().get_item_image(name)

        if inv_icon is not None:
            inv_icon = self.assets.images().color_image(inv_icon, data)
            icon = QPixmap.fromImage(ImageQt(inv_icon))
        elif image is not None:
            image = self.assets.images().color_image(image, data)
            icon = QPixmap.fromImage(ImageQt(image))
        else:
            logging.warning("Unable to load image for %s", name)
            icon = QPixmap.fromImage(QImage.fromData(self.assets.items().missing_icon()))

        icon = self.scale_image_icon(icon, 64, 64)
        self.ui.icon.setPixmap(icon)

    def scale_image_icon(self, qpix, width, height):
        """Scales the image icon to best fit in the width and height bounds
        given. Preserves aspect ratio."""
        scaled_qpix = qpix
        src_width = qpix.width()
        src_height = qpix.height()

        if src_width == src_height and width == height:
            # square image and square bounds
            scaled_qpix = qpix.scaled(width,height)
        elif src_width > src_height:
            # wider than tall needs width scaling to fit
            scaled_qpix = qpix.scaledToWidth(width)
        elif src_height > src_width:
            # taller than wide needs height scaling to fit
            scaled_qpix = qpix.scaledToHeight(height)

        return scaled_qpix

    def update_item(self):
        """Update main item view with current item browser data."""
        name = self.ui.item_type.text()
        item = self.assets.items().get_item(name)
        uuid = self.player.get_uuid()

        generated_item = {
            "generatedgun": lambda: self.assets.items().generate_gun(item),
            "generatedsword": lambda: self.assets.items().generate_sword(item),
            "generatedshield": lambda: self.assets.items().generate_shield(item),
            "sapling": lambda: self.assets.items().generate_sapling(item),
            "filledcapturepod": lambda: self.assets.items().generate_filledcapturepod(item,
                                                                                      uuid)
        }

        if item is not None:
            category = re.search("\..+$", item[1])
            is_generated = (category is not None and
                            category.group()[1:] in generated_item.keys())
            if is_generated:
                name = category.group()[1:]
                self.ui.item_type.setText(name)
                generated = generated_item[name]()
                self.item = saves.new_item_data(name, 1, generated)
            else:
                self.item = saves.new_item_data(name, 1, item[0])

            self.ui.count.setValue(1)
            self.update()
            return True
        else:
            self.item = saves.new_item_data("", 1)
            self.ui.desc.setText("<html><body><strong>Empty Slot</strong></body></html>")
            self.update()
            return False

    def get_item(self):
        """Return an ItemWidget of the currently open item."""
        name = self.ui.item_type.text()
        count = self.ui.count.value()
        data = self.item["parameters"]
        return saves.new_item_data(name, count, data)

    def clear_item_options(self):
        self.ui.variant.clear()
        self.ui.variant.setHorizontalHeaderLabels(["Options"])
        self.ui.variant.setRowCount(0)
        if self.item is not None:
            self.item["parameters"] = {}

    def new_item_edit_options(self, new=False, raw=False):
        """Edit the selected item option with custom dialog."""

        if new:
            selected = ItemOptionWidget("", None)
        else:
            selected = self.ui.variant.currentItem()

        generic = False
        dialog = None
        name, value = selected.option

        # TODO: drawable images
        # TODO: status effects
        # TODO: color editing

        if new or raw:
            dialog = ItemEditOptions(self.dialog, name, value)
            def save():
                name, value = dialog.get_option()
                self.item["parameters"][name] = value
            dialog.dialog.accepted.connect(save)
            dialog.dialog.exec()
        elif name in ["inventoryIcon", "image", "largeImage"] and type(value) is str:
            dialog = ImageBrowser(self.dialog, self.assets, False)
            def save():
                value = dialog.get_key()
                self.item["parameters"][name] = value
            dialog.dialog.accepted.connect(save)
            dialog.dialog.exec()
        elif type(value) is str:
            text, ok = QInputDialog.getText(self.dialog, "Edit Text", name, text=value)
            if ok:
                value = text
                self.item["parameters"][name] = value
        elif type(value) is int:
            num, ok = QInputDialog.getInt(self.dialog, "Edit Integer", name, value)
            if ok:
                value = num
                self.item["parameters"][name] = value
        elif type(value) is float:
            num, ok = QInputDialog.getDouble(self.dialog, "Edit Double", name, value, decimals=2)
            if ok:
                value = num
                self.item["parameters"][name] = value
        elif type(value) is bool:
            value = not value
            self.item["parameters"][name] = value
        else:
            dialog = ItemEditOptions(self.dialog, name, value)
            def save():
                name, value = dialog.get_option()
                self.item["parameters"][name] = value
            dialog.dialog.accepted.connect(save)
            dialog.dialog.exec()

        self.update()

    def remove_option(self):
        """Remove the currently selected item option."""
        current = self.ui.variant.currentItem()
        if current is None:
            return
        self.item["parameters"].pop(current.option[0])
        self.populate_options()

    def edit_option(self):
        """Edit currently selected item option."""
        current = self.ui.variant.currentItem()
        if current is not None:
            self.new_item_edit_options()

    def new_item_browser(self):
        self.item_browser = ItemBrowser(self.dialog, category=self.remember_browser)
        self.item_browser.dialog.accepted.connect(self.set_item_browser_selection)
        self.item_browser.dialog.exec()

    def set_item_browser_selection(self):
        name = self.item_browser.get_selection()
        if name is None:
            return
        self.remember_browser = self.item_browser.remember_category
        self.ui.item_type.setText(name)
        self.update_item()

    def populate_options(self):
        self.ui.variant.setRowCount(len(self.item["parameters"]))
        self.ui.variant.setHorizontalHeaderLabels(["Options"])
        row = 0
        for k in sorted(self.item["parameters"].keys()):
            variant = ItemOptionWidget(k, self.item["parameters"][k])
            self.ui.variant.setItem(row, 0, variant)
            row += 1

    def max_count(self):
        if "maxStack" in self.item["parameters"]:
            max = int(self.item["parameters"]["maxStack"])
        else:
            max = 1000
        self.ui.count.setValue(max)

    def toggle_max(self):
        value = self.ui.count.value()
        self.ui.max_button.setEnabled(value != 1000)

    def export_item(self):
        json_data = json.dumps(self.item, sort_keys=True,
                               indent=4, separators=(',', ': '))
        filename = QFileDialog.getSaveFileName(self.dialog,
                                               "Export Item As",
                                               filter="JSON (*.json);;All Files (*)")
        if filename[0] != "":
            json_file = open(filename[0], "w")
            json_file.write(json_data)
            json_file.close()

    def import_item(self):
        item = import_json(self.dialog)
        if item == False:
            dialog = QMessageBox(self.dialog)
            dialog.setWindowTitle("Import Error")
            dialog.setText("Could not import requested item file.")
            dialog.setInformativeText("See starcheat log for more details.")
            dialog.setStandardButtons(QMessageBox.Close)
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec()
        elif item is None:
            pass
        else:
            self.ui.item_type.setText(item["name"])
            self.ui.count.setValue(item["count"])
            self.item = item
            self.update()
