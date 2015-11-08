"""
Qt techs management dialog
"""

import logging

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PIL.ImageQt import ImageQt

import qt_techs
import saves


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


class Techs(object):
    def __init__(self, main_window):
        self.dialog = QDialog(main_window.window)
        self.ui = qt_techs.Ui_Dialog()
        self.ui.setupUi(self.dialog)
        self.main_window = main_window

        self.assets = main_window.assets
        self.player = main_window.player

        self.selected_tech = None

        self.ui.tech_list.currentItemChanged.connect(lambda: self.set_select(self.ui.tech_list))
        self.ui.tech_list.itemDoubleClicked.connect(self.add_tech)
        self.ui.known_list.currentItemChanged.connect(lambda: self.set_select(self.ui.known_list))
        self.ui.known_list.itemDoubleClicked.connect(self.remove_tech)

        self.techs = [None, None, None, None]
        self.equip = [None, None, None, None]

        self.populate_equipped()

        self.ui.toggle_button.clicked.connect(self.toggle_tech)
        self.ui.add_button.clicked.connect(self.add_tech)
        self.ui.remove_button.clicked.connect(self.remove_tech)
        self.ui.unlock_button.clicked.connect(self.learn_all_techs)

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

    def populate_equipped(self):
        current = 1
        for i in self.player.get_equipped_techs():
            if i is None:
                continue

            try:
                name = i["content"]["name"]
                tech = self.assets.techs().get_tech(name)
                icon = QPixmap.fromImage(ImageQt(tech[1]))
                getattr(self.ui, "icon"+str(current)).setPixmap(icon.scaled(32, 32))
                getattr(self.ui, "icon"+str(current)).setToolTip(tech[0]["shortdescription"])
                self.techs[current-1] = new_tech_slot(tech[0]["techModule"])
                self.equip[current-1] = tech[0]["itemName"]
            except TypeError:
                logging.exception("Couldn't load tech")

            current += 1

    def update_lists(self):
        visible_techs = [x["name"] for x in self.player.get_visible_techs()]
        self.ui.tech_list.clear()
        for tech in sorted(self.assets.techs().all()):
            if tech not in visible_techs:
                item = QListWidgetItem(tech)
                self.ui.tech_list.addItem(item)

        enabled = [x["name"] for x in self.player.get_enabled_techs()]
        self.ui.known_list.clear()
        for tech in sorted(visible_techs):
            item = QListWidgetItem(tech)
            if tech in enabled:
                item.setBackground(QBrush(QColor("lightBlue")))
            self.ui.known_list.addItem(item)

    def update_selection(self):
        tech = self.assets.techs().get_tech(self.selected_tech)

        # this is only used if player has corrupt/missing modded techs known
        if tech is None:
            self.ui.tech_info.setText("Unknown Tech")
            self.ui.current_icon.setPixmap(QPixmap())
            self.ui.add_button.setEnabled(False)
            self.ui.remove_button.setEnabled(True)
            return

        visible = [x["name"] for x in self.player.get_visible_techs()]

        tech_info = "<strong>%s (%s)</strong><br><br>" % (tech[0]["shortdescription"],
                                                          tech[0]["itemName"])
        tech_info += "<strong>Type:</strong> %s<br>" % tech[3]["type"]
        tech_info += "<strong>Rarity:</strong> %s<br>" % tech[0]["rarity"]
        tech_info += "<strong>Module:</strong> %s<br><br>" % tech[0]["techModule"]
        tech_info += tech[0]["description"]+"<br>"

        self.ui.tech_info.setText(tech_info)
        self.ui.current_icon.setPixmap(QPixmap.fromImage(ImageQt(tech[1])).scaled(32, 32))

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
        item = self.selected_tech
        if item in enabled:
            new_techs = [x for x in enabled if x != item]
            self.player.set_enabled_techs(make_tech_list(new_techs))
        else:
            enabled.append(item)
            self.player.set_enabled_techs(make_tech_list(enabled))
        self.update_lists()
        self.update_selection()

    def add_tech(self):
        item = self.selected_tech
        visible = [x["name"] for x in self.player.get_visible_techs()]
        visible.append(item)
        self.player.set_visible_techs(make_tech_list(visible))
        self.update_lists()
        self.update_selection()

    def remove_tech(self):
        if self.selected_tech is None:
            return
        item = self.selected_tech
        visible = [x["name"] for x in self.player.get_visible_techs()]
        enabled = [x["name"] for x in self.player.get_enabled_techs()]
        self.player.set_visible_techs(make_tech_list([x for x in visible if x != item]))
        self.player.set_enabled_techs(make_tech_list([x for x in enabled if x != item]))
        self.update_lists()
        self.update_selection()

    def learn_all_techs(self):
        all_techs = self.assets.techs().all()
        self.player.set_visible_techs(make_tech_list(all_techs))
        self.player.set_enabled_techs(make_tech_list(all_techs))
        self.update_lists()
        self.update_selection()

    def set_tech(self, index):
        if self.selected_tech is None:
            return

        tech_name = self.selected_tech
        tech = self.assets.techs().get_tech(tech_name)

        if tech is None:
            return

        icon = QPixmap.fromImage(ImageQt(tech[1]))
        getattr(self.ui, "icon"+str(index+1)).setPixmap(icon.scaled(32, 32))
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
