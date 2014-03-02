"""
Qt techs management dialog
"""

from PyQt5.QtWidgets import QDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QImage, QIcon, QBrush, QColor
from PIL.ImageQt import ImageQt

import assets, qt_techs
from config import Config

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

        known_recipes = [x["name"] for x in self.player.get_blueprints()]
        self.ui.tech_list.clear()
        for tech in self.assets.techs().all():
            item = QListWidgetItem(tech)
            if tech in known_recipes:
                item.setBackground(QBrush(QColor("lightBlue")))
            self.ui.tech_list.addItem(item)

    def update_selection(self):
        tech_name = self.ui.tech_list.currentItem().text()
        tech = self.assets.techs().get_tech(tech_name)

        tech_info = "<strong>"+tech[0]["shortdescription"]+"</strong><br>"
        tech_info += "("+tech[0]["itemName"]+")"
        tech_info += "<p>"+tech[0]["description"]+"</p>"

        self.ui.tech_info.setText(tech_info)
        self.ui.current_icon.setPixmap(QPixmap.fromImage(ImageQt(tech[1])).scaled(32,32))
