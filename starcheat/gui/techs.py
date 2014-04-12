"""
Qt techs management dialog
"""

import os, logging

from PyQt5.QtWidgets import QDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QImage, QIcon, QBrush, QColor
from PIL.ImageQt import ImageQt

import assets, qt_techs
from config import Config

def new_tech_slot(tech_asset):
    module = {
        "active": False,
        "modulePath": tech_asset,
        "scriptData": {}
    }

    return module

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

        self.ui.tech_list.currentItemChanged.connect(self.update_selection)

        self.techs = [None, None, None, None]
        self.equip = [None, None, None, None]

        # populate equipped techs
        current = 1
        for i in self.player.get_tech_modules():
            try:
                tech_name = os.path.basename(i["modulePath"].replace(".tech",""))
                tech = self.assets.techs().get_tech(tech_name)
                icon = QPixmap.fromImage(ImageQt(tech[1]))
                getattr(self.ui, "icon"+str(current)).setPixmap(icon.scaled(32,32))
                getattr(self.ui, "icon"+str(current)).setToolTip(tech[0]["shortdescription"])
                self.techs[current-1] = i
                self.equip[current-1] = tech[0]["itemName"]
            except TypeError:
                logging.exception("Couldn't load tech: %s", i["modulePath"])
                pass

            current += 1

        self.ui.icon1_clear.clicked.connect(lambda: self.clear_tech(0))
        self.ui.icon2_clear.clicked.connect(lambda: self.clear_tech(1))
        self.ui.icon3_clear.clicked.connect(lambda: self.clear_tech(2))
        self.ui.icon4_clear.clicked.connect(lambda: self.clear_tech(3))

        self.ui.icon1_button.clicked.connect(lambda: self.set_tech(0))
        self.ui.icon2_button.clicked.connect(lambda: self.set_tech(1))
        self.ui.icon3_button.clicked.connect(lambda: self.set_tech(2))
        self.ui.icon4_button.clicked.connect(lambda: self.set_tech(3))

        #known_recipes = [x["name"] for x in self.player.get_blueprints()]
        self.ui.tech_list.clear()
        for tech in self.assets.techs().all():
            item = QListWidgetItem(tech)
            #if tech in known_recipes:
            #    item.setBackground(QBrush(QColor("lightBlue")))
            self.ui.tech_list.addItem(item)

    def update_selection(self):
        tech_name = self.ui.tech_list.currentItem().text()
        tech = self.assets.techs().get_tech(tech_name)

        tech_info = "<strong>"+tech[0]["shortdescription"]+"</strong><br>"
        tech_info += "("+tech[0]["itemName"]+")"
        tech_info += "<p>"+tech[0]["description"]+"</p>"

        self.ui.tech_info.setText(tech_info)
        self.ui.current_icon.setPixmap(QPixmap.fromImage(ImageQt(tech[1])).scaled(32,32))

    def set_tech(self, index):
        tech_name = self.ui.tech_list.currentItem().text()
        tech = self.assets.techs().get_tech(tech_name)
        icon = QPixmap.fromImage(ImageQt(tech[1]))
        getattr(self.ui, "icon"+str(index+1)).setPixmap(icon.scaled(32,32))
        getattr(self.ui, "icon"+str(index+1)).setToolTip(tech[0]["shortdescription"])
        self.techs[index] = new_tech_slot(tech[2])
        self.equip[index] = tech[0]["itemName"]

    def clear_tech(self, index):
        self.techs[index] = None
        self.equip[index] = None
        getattr(self.ui, "icon"+str(index+1)).setPixmap(QPixmap())
        getattr(self.ui, "icon"+str(index+1)).setToolTip(None)
        print(self.equip)

    def write_techs(self):
        techs = []
        equip = [None, None, None, None]

        # tech list can't have empty spaces in it
        for i in self.techs:
            if i != None:
                techs.append(i)

        index = 0
        for i in self.equip:
            if i != None:
                equip[index] = i
                index += 1

        self.player.set_tech_modules(techs, equip)
        self.main_window.window.setWindowModified(True)
