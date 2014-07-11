"""
Qt item edit dialog
"""

# TODO: the variant editing stuff would work much better as a tree view,
# especially considering the upcoming change

# TODO: a function to convert from an asset item to a valid inventory item
# once that's complete, work can be started on proper item generation. to begin,
# we just wanna pull in all the default values of an item

from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QDialogButtonBox
from PyQt5.QtWidgets import QInputDialog, QListWidgetItem, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PIL.ImageQt import ImageQt
import json, copy, logging

import assets, qt_itemedit, qt_itemeditoptions, saves
import qt_imagebrowser
from gui.common import inv_icon, empty_slot
from gui.itembrowser import ItemBrowser, generate_item_info
from config import Config

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

class ImageBrowser():
    def __init__(self, parent, assets):
        self.dialog = QDialog(parent)
        self.ui = qt_imagebrowser.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.assets = assets

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
    def __init__(self, parent, item, player, browser_category="<all>"):
        """Takes an item widget and displays an edit dialog for it."""
        self.dialog = QDialog(parent)
        self.ui = qt_itemedit.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.assets = assets.Assets(assets_db_file, starbound_folder)

        self.player = player

        self.item_browser = None
        self.remember_browser = browser_category
        self.item = copy.deepcopy(item)

        if self.item["name"] != "":
            # set name text box
            self.ui.item_type.setText(self.item["name"])
            # set item count spinbox
            self.ui.count.setValue(int(self.item["count"]))
            # set up variant table
            self.populate_options()
            self.update_item_info(self.item["name"], self.item["data"])
        else:
            # empty slot
            self.new_item_browser()
            self.update_item()

        # set up signals
        self.ui.load_button.clicked.connect(self.new_item_browser)
        self.ui.item_type.textChanged.connect(self.update_item)
        self.ui.variant.itemDoubleClicked.connect(lambda: self.new_item_edit_options(False))
        self.ui.max_button.clicked.connect(self.max_count)
        self.ui.add_option_button.clicked.connect(lambda: self.new_item_edit_options(True))
        self.ui.remove_option_button.clicked.connect(self.remove_option)
        self.ui.edit_option_button.clicked.connect(self.edit_option)
        self.ui.export_button.clicked.connect(self.export_item)
        self.ui.import_button.clicked.connect(self.import_item)

        self.ui.item_type.setFocus()

    def update_item_info(self, name, data):
        item_info = "<html><body>"
        item_info += generate_item_info(data)
        item_info += "</body></html>"
        self.ui.desc.setText(item_info)

        inv_icon_file = self.assets.items().get_item_icon(name)
        if inv_icon_file is not None:
            icon = QPixmap.fromImage(ImageQt(inv_icon_file))
        else:
            image_file = self.assets.items().get_item_image(name)
            if image_file is not None:
                icon = QPixmap.fromImage(ImageQt(image_file))
            else:
                icon = QPixmap.fromImage(QImage.fromData(self.assets.items().missing_icon()))
        # last ditch
        try:
            icon = self.scale_image_icon(icon,64,64)
            self.ui.icon.setPixmap(icon)
        except TypeError:
            logging.warning("Unable to load item image: "+name)
            self.ui.icon.setPixmap(QPixmap())

    def scale_image_icon(self, qpix, width, height):
        """Scales the image icon to best fit in the width and height bounds given. Preserves aspect ratio."""
        scaled_qpix = qpix
        src_width = qpix.width()
        src_height = qpix.height()

        if src_width == src_height and width == height: #square image and square bounds
            scaled_qpix = qpix.scaled(width,height)
        elif src_width > src_height: #wider than tall needs width scaling to fit
            scaled_qpix = qpix.scaledToWidth(width)
        elif src_height > src_width: #taller than wide needs height scaling to fit
            scaled_qpix = qpix.scaledToHeight(height)
        return scaled_qpix

    def update_item(self):
        """Update main item view with current item browser data."""
        name = self.ui.item_type.text()

        # TODO: i guess eventually we're gonna need like.. some sort of generic
        # generate item function
        try:
            item = self.assets.items().get_item(name)
            if item[1].endswith("generatedgun"):
                options = self.assets.items().generate_gun(item)
                name = options["itemName"]
            elif item[1].endswith("generatedsword"):
                options = self.assets.items().generate_sword(item)
                name = options["itemName"]
            elif item[1].endswith("generatedshield"):
                options = self.assets.items().generate_shield(item)
                name = options["itemName"]
            elif item[1].endswith("sapling"):
                options = self.assets.items().generate_sapling(item)
            elif name == "filledcapturepod":
                options = self.assets.items().generate_filledcapturepod(item,
                                                                        self.player.get_uuid())
            else:
                options = item[0]
        except TypeError:
            self.item = empty_slot().item
            self.ui.desc.setText("<html><body><strong>Empty Slot</strong></body></html>")
            self.ui.icon.setPixmap(QPixmap())
            self.clear_item_options()
            return

        self.ui.item_type.setText(name)

        self.item = saves.new_item(name, 1, options)
        self.ui.count.setValue(1)
        self.update_item_info(name, options)
        self.populate_options()

    def get_item(self):
        """Return an ItemWidget of the currently open item."""
        name = self.ui.item_type.text()
        count = self.ui.count.value()
        data = self.item["data"]
        return saves.new_item(name, count, data)

    def clear_item_options(self):
        self.ui.variant.clear()
        self.ui.variant.setHorizontalHeaderLabels(["Options"])
        self.ui.variant.setRowCount(0)
        # don't understand why i need to do this check either...
        if self.item is not None:
            self.item["data"] = {}

    def new_item_edit_options(self, new):
        """Edit the selected item option with custom dialog."""

        if new:
            selected = ItemOptionWidget("", None)
        else:
            selected = self.ui.variant.currentItem()

        # TODO: need a better way to lay this out. it's going to get big and messy fast

        # this is for the qinputdialog stuff. can't set signals on them
        generic = False
        if new:
            # needs to be here or new opts get detected as string (?)
            dialog = ItemEditOptions(self.dialog, selected.option[0], selected.option[1])
            def get_option():
                data = dialog.ui.options.toPlainText()
                return dialog.ui.name.text(), json.loads(data)
        #elif selected.option[0] in ["inventoryIcon", "image", "largeImage"]:
        #    dialog = ImageBrowser(self.dialog, self.assets)
        #    def get_option():
        #        return selected.option[0], dialog.get_key()
        elif type(self.item["data"][selected.option[0]]) is str:
            generic = True
            text, ok = QInputDialog.getText(self.dialog, "Edit Text", selected.option[0],
                                            text=self.item["data"][selected.option[0]])
            if ok:
                self.item["data"][selected.option[0]] = text
        elif type(self.item["data"][selected.option[0]]) is int:
            generic = True
            num, ok = QInputDialog.getInt(self.dialog, "Edit Integer", selected.option[0],
                                          self.item["data"][selected.option[0]])
            if ok:
                self.item["data"][selected.option[0]] = num
        elif type(self.item["data"][selected.option[0]]) is float:
            generic = True
            num, ok = QInputDialog.getDouble(self.dialog, "Edit Double", selected.option[0],
                                             self.item["data"][selected.option[0]], decimals=2)
            if ok:
                self.item["data"][selected.option[0]] = num
        elif type(self.item["data"][selected.option[0]]) is bool:
            generic = True
            self.item["data"][selected.option[0]] = not self.item["data"][selected.option[0]]
        else:
            dialog = ItemEditOptions(self.dialog, selected.option[0], selected.option[1])
            def get_option():
                data = dialog.ui.options.toPlainText()
                return dialog.ui.name.text(), json.loads(data)

        def save():
            new_option = get_option()
            self.item["data"][new_option[0]] = new_option[1]

        if not generic:
            dialog.dialog.accepted.connect(save)
            dialog.dialog.exec()

        self.populate_options()
        self.update_item_info(self.item["name"], self.item["data"])

    def remove_option(self):
        """Remove the currently selected item option."""
        try:
            option_name = self.ui.variant.currentItem().option[0]
        except AttributeError:
            return
        self.item["data"].pop(option_name)
        self.populate_options()

    def edit_option(self):
        """Edit currently selected item option."""
        try:
            option_name = self.ui.variant.currentItem().option[0]
        except AttributeError:
            return
        self.new_item_edit_options(False)

    def new_item_browser(self):
        self.item_browser = ItemBrowser(self.dialog, category=self.remember_browser)
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
        name = self.item_browser.get_selection()
        if name is None:
            return
        self.remember_browser = self.item_browser.remember_category
        self.ui.item_type.setText(name)

    def max_count(self):
        if "maxStack" in self.item["data"]:
            max = int(self.item["data"]["maxStack"])
        else:
            max = 1000
        self.ui.count.setValue(max)

    def export_item(self):
        json_data = json.dumps(self.item, sort_keys=True,
                               indent=4, separators=(',', ': '))
        filename = QFileDialog.getSaveFileName(self.dialog,
                                               "Export Item As")
        if filename[0] != "":
            json_file = open(filename[0], "w")
            json_file.write(json_data)
            json_file.close()

    def import_item(self):
        filename = QFileDialog.getOpenFileName(self.dialog,
                                               "Import Item File")
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
            if "data" not in item_data:
                item_data["data"] = {}
            return item_data

        item = parse()
        if not item:
            logging.warning("Invalid item file: %s", filename[0])
            return
        else:
            self.ui.item_type.setText(item["name"])
            self.item = item
            self.ui.count.setValue(self.item["count"])
            self.update_item_info(self.item["name"], self.item["data"])
            self.populate_options()
