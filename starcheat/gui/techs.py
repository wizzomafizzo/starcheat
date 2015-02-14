"""
Qt techs management dialog
"""

import os, logging

from PyQt5.QtWidgets import QDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QBrush, QColor
from PIL.ImageQt import ImageQt

import assets, qt_techs
import saves
from config import Config

from gui.itemedit import ItemEditOptions

# TODO: right now this dialog converts from techs to items by adding and
# removing the Tech suffix. if this is not a strict requirement for tech
# assets, this will all fail, but it makes lookups significantly faster.
# ideally this information should be indexed
# TODO: use proper tech names in lists, needs above mentioned index

def new_tech_slot(tech_asset):
    module = {
        "module": tech_asset,
        "scriptData": {}
    }
    return module

def make_tech_list(tech_names):
    techs = []
    for i in tech_names:
        techs.append(saves.new_item_data(i))
    return techs

class Techs():
    def __init__(self, main_window):
        self.dialog = QDialog(main_window.window)
        self.ui = qt_techs.Ui_Dialog()
        self.ui.setupUi(self.dialog)
        self.main_window = main_window

        starbound_folder = Config().read("starbound_folder")
        self.assets = assets.Assets(Config().read("assets_db"),
                                    starbound_folder)
        self.player = main_window.player

        self.selected_tech = None

        self.ui.tech_list.currentItemChanged.connect(lambda: self.set_select(self.ui.tech_list))
        self.ui.tech_list.itemDoubleClicked.connect(self.add_tech)
        self.ui.known_list.currentItemChanged.connect(lambda: self.set_select(self.ui.known_list))
        self.ui.known_list.itemDoubleClicked.connect(self.remove_tech)

        self.techs = [None, None, None, None]
        self.equip = [None, None, None, None]

        # populate equipped techs
        current = 1
        for i in self.player.get_equipped_techs():
            try:
                name = i["__content"]["name"].replace("Tech", "")
                tech = self.assets.techs().get_tech(name)
                icon = QPixmap.fromImage(ImageQt(tech[1]))
                getattr(self.ui, "icon"+str(current)).setPixmap(icon.scaled(32,32))
                getattr(self.ui, "icon"+str(current)).setToolTip(tech[0]["shortdescription"])
                self.techs[current-1] = new_tech_slot(name)
                self.equip[current-1] = tech[0]["itemName"]
            except TypeError:
                logging.exception("Couldn't load tech")
                pass

            current += 1

        self.ui.toggle_button.clicked.connect(self.toggle_tech)
        self.ui.add_button.clicked.connect(self.add_tech)
        self.ui.remove_button.clicked.connect(self.remove_tech)
        self.ui.unlock_button.clicked.connect(self.learn_all_techs)
        self.ui.movement_button.clicked.connect(self.edit_movement)

        self.ui.icon1_clear.clicked.connect(lambda: self.clear_tech(0))
        self.ui.icon2_clear.clicked.connect(lambda: self.clear_tech(1))
        self.ui.icon3_clear.clicked.connect(lambda: self.clear_tech(2))
        self.ui.icon4_clear.clicked.connect(lambda: self.clear_tech(3))

        self.ui.icon1_button.clicked.connect(lambda: self.set_tech(0))
        self.ui.icon2_button.clicked.connect(lambda: self.set_tech(1))
        self.ui.icon3_button.clicked.connect(lambda: self.set_tech(2))
        self.ui.icon4_button.clicked.connect(lambda: self.set_tech(3))

        self.update_lists()
        self.ui.tech_list.setFocus()
        if self.ui.tech_list.count() > 0:
            self.ui.tech_list.setCurrentRow(0)
        else:
            self.ui.known_list.setCurrentRow(0)

    def edit_movement(self):
        edit = ItemEditOptions(self.dialog,
                               "movementController",
                               self.player.get_movement(),
                               "Edit Default Movement")

        def save():
            name, value = edit.get_option()
            self.player.set_movement(value)

        edit.dialog.accepted.connect(save)
        edit.ui.name.setEnabled(False)
        edit.dialog.exec()

    def update_lists(self):
        visible_items = [x["name"] for x in self.player.get_visible_techs()]
        visible_techs = [x.replace("Tech", "") for x in visible_items]
        self.ui.tech_list.clear()
        for tech in sorted(self.assets.techs().all()):
            if tech not in visible_techs:
                item = QListWidgetItem(tech)
                self.ui.tech_list.addItem(item)

        enabled = [x["name"] for x in self.player.get_enabled_techs()]
        self.ui.known_list.clear()
        for tech in sorted(visible_items):
            item = QListWidgetItem(tech.replace("Tech", ""))
            if tech in enabled:
                item.setBackground(QBrush(QColor("lightBlue")))
            self.ui.known_list.addItem(item)

    def update_selection(self):
        enabled = [x["name"] for x in self.player.get_enabled_techs()]
        visible = [x["name"].replace("Tech", "") for x in self.player.get_visible_techs()]
        tech = self.assets.techs().get_tech(self.selected_tech)

        tech_info = "<strong>%s (%s)</strong><br><br>" % (tech[0]["shortdescription"],
                                                          tech[0]["itemName"])
        tech_info += "<strong>Type:</strong> %s<br>" % tech[3]["type"]
        tech_info += "<strong>Rarity:</strong> %s<br>" % tech[0]["rarity"]
        tech_info += "<strong>Module:</strong> %s<br><br>" % tech[0]["techModule"]
        tech_info += tech[0]["description"]+"<br>"

        self.ui.tech_info.setText(tech_info)
        self.ui.current_icon.setPixmap(QPixmap.fromImage(ImageQt(tech[1])).scaled(32,32))

        slots = ["head", "body", "legs", "suit"]
        index = 1
        for slot in slots:
            set_button = getattr(self.ui, "icon" + str(index) + "_button")
            clear_button = getattr(self.ui, "icon" + str(index) + "_clear")
            can_set = tech[3]["type"] == slot
            is_set = self.equip[index-1] is not None
            set_button.setEnabled(can_set)
            clear_button.setEnabled(is_set)
            index += 1

        can_add = self.selected_tech not in visible
        self.ui.add_button.setEnabled(can_add)
        self.ui.remove_button.setEnabled(not can_add)
        self.ui.toggle_button.setEnabled(not can_add)

    def set_select(self, source):
        selected = source.currentItem()
        if selected is not None:
            self.selected_tech = selected.text()
        else:
            return
        self.update_selection()

    def toggle_tech(self):
        enabled = [x["name"] for x in self.player.get_enabled_techs()]
        item = self.selected_tech + "Tech"
        if item in enabled:
            new_techs = [x for x in enabled if x != item]
            self.player.set_enabled_techs(make_tech_list(new_techs))
        else:
            enabled.append(item)
            self.player.set_enabled_techs(make_tech_list(enabled))
        self.update_lists()
        self.update_selection()

    def add_tech(self):
        item = self.selected_tech + "Tech"
        visible = [x["name"] for x in self.player.get_visible_techs()]
        visible.append(item)
        self.player.set_visible_techs(make_tech_list(visible))
        self.update_lists()
        self.update_selection()

    def remove_tech(self):
        if self.selected_tech is None:
            return
        item = self.selected_tech + "Tech"
        visible = [x["name"] for x in self.player.get_visible_techs()]
        enabled = [x["name"] for x in self.player.get_enabled_techs()]
        self.player.set_visible_techs(make_tech_list([x for x in visible if x != item]))
        self.player.set_enabled_techs(make_tech_list([x for x in enabled if x != item]))
        self.update_lists()
        self.update_selection()

    def learn_all_techs(self):
        all_techs = self.assets.techs().all()
        items = [x + "Tech" for x in all_techs]
        self.player.set_visible_techs(make_tech_list(items))
        self.player.set_enabled_techs(make_tech_list(items))
        self.update_lists()
        self.update_selection()

    def set_tech(self, index):
        if self.selected_tech is None:
            return
        tech_name = self.selected_tech
        tech = self.assets.techs().get_tech(tech_name)
        icon = QPixmap.fromImage(ImageQt(tech[1]))
        getattr(self.ui, "icon"+str(index+1)).setPixmap(icon.scaled(32,32))
        getattr(self.ui, "icon"+str(index+1)).setToolTip(tech[0]["shortdescription"])
        self.techs[index] = new_tech_slot(tech[0]["techModule"])
        self.equip[index] = tech[0]["itemName"]
        self.update_selection()

    def clear_tech(self, index):
        self.techs[index] = None
        self.equip[index] = None
        getattr(self.ui, "icon"+str(index+1)).setPixmap(QPixmap())
        getattr(self.ui, "icon"+str(index+1)).setToolTip(None)
        self.update_selection()

    def write_techs(self):
        techs = []
        equip = [None, None, None, None]
        enabled = []

        # tech list can't have empty spaces in it
        for i in self.techs:
            if i is not None:
                techs.append(i)

        index = 0
        for i in self.equip:
            equip[index] = i
            index += 1

        self.player.set_tech_modules(techs, equip)
        self.main_window.window.setWindowModified(True)
