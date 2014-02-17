"""
Qt appearance management dialog
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QColorDialog, QTableWidgetItem
from PyQt5.QtGui import QColor, QBrush, QPixmap, QImage, QIcon
from PIL.ImageQt import ImageQt

import assets, qt_appearance, qt_coloredit
from gui.common import preview_icon
from config import Config

class Appearance():
    def __init__(self, main_window):
        self.dialog = QDialog(main_window.window)
        self.ui = qt_appearance.Ui_Dialog()
        self.ui.setupUi(self.dialog)
        self.main_window = main_window

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.assets = assets.Assets(assets_db_file, starbound_folder)
        self.species = self.assets.species()
        self.player = main_window.player

        race = main_window.ui.race.currentText()
        self.player.set_race(race)
        self.player.set_gender(main_window.get_gender())

        # Current player stats
        race = self.player.get_race()
        gender = self.player.get_gender()
        personality = self.player.get_personality()

        self.colors = {
            "body": self.player.get_body_directives(),
            "emote": self.player.get_emote_directives(),
            "hair": self.player.get_hair_directives(),
            "facial_hair": self.player.get_facial_hair_directives(),
            "facial_mask": self.player.get_facial_mask_directives()
        }
        color_values = ("body", "hair", "facial_hair", "facial_mask")

        current_appearance = {
            "hair": self.player.get_hair(),
            "facial_hair": self.player.get_facial_hair(),
            "facial_mask": self.player.get_facial_mask()
        }
        appearance_values = ("hair", "facial_hair", "facial_mask")

        # appearance groups/types
        for value in appearance_values:
            group_data = getattr(self.species, "get_%s_groups" % value)(race, gender)
            type_data = getattr(self.species, "get_%s_types" % value)(race, gender,
                                                                      current_appearance[value][0])
            group_widget = getattr(self.ui, value+"_group")
            for option in group_data:
                group_widget.addItem(option)
            group_widget.setCurrentText(current_appearance[value][0])
            if len(group_data) < 2: group_widget.setEnabled(False)

            type_widget = getattr(self.ui, value+"_type")
            for option in type_data:
                type_widget.addItem(option)
            type_widget.setCurrentText(current_appearance[value][1])
            if len(type_data) < 2: type_widget.setEnabled(False)

        # personality
        for option in self.species.get_personality():
            self.ui.personality.addItem(option[0])
        self.ui.personality.setCurrentText(personality)

        # set up color picker buttons
        for value in color_values:
            getattr(self.ui, value+"_color").clicked.connect(getattr(self, "new_%s_color_edit" % value))
            if len(self.colors[value]) == 0:
                getattr(self.ui, value+"_color").setEnabled(False)

        # player image
        image = preview_icon(race, gender)
        self.ui.player_preview.setPixmap(image.scaled(64, 64))

    def write_appearance_values(self):
        hair = self.ui.hair_group.currentText(), self.ui.hair_type.currentText()
        facial_hair = self.ui.facial_hair_group.currentText(), self.ui.facial_hair_type.currentText()
        facial_mask = self.ui.facial_mask_group.currentText(), self.ui.facial_mask_type.currentText()
        personality = self.ui.personality.currentText()
        self.player.set_hair(*hair)
        self.player.set_facial_hair(*facial_hair)
        self.player.set_facial_mask(*facial_mask)
        self.player.set_personality(personality)
        self.player.set_body_directives(self.colors["body"])
        self.player.set_hair_directives(self.colors["hair"])
        self.player.set_facial_hair_directives(self.colors["facial_hair"])
        self.player.set_facial_mask_directives(self.colors["facial_mask"])
        self.main_window.window.setWindowModified(True)

    def new_color_edit(self, type):
        color_edit = ColorEdit(self.dialog, self.colors[type])
        color_edit.dialog.exec()
        new_colors = color_edit.get_colors()
        return new_colors

    def hair_icon(self, species, hair_type, hair_group):
        image_data = self.assets.species().get_hair_image(species, hair_type, hair_group)
        return QPixmap.fromImage(ImageQt(image_data))

    # for color button signals
    def new_body_color_edit(self):
        self.colors["body"] = self.new_color_edit("body")
    def new_hair_color_edit(self):
        self.colors["hair"] = self.new_color_edit("hair")
    def new_facial_hair_color_edit(self):
        self.colors["facial_hair"] = self.new_color_edit("facial_hair")
    def new_facial_mask_color_edit(self):
        self.colors["facial_mask"] = self.new_color_edit("facial_mask")

class ColorItem(QTableWidgetItem):
    def __init__(self, color):
        QTableWidgetItem.__init__(self, color)
        color = color.upper()
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        self.setBackground(QBrush(QColor("#"+color)))

class ColorEdit():
    def __init__(self, parent, directives):
        self.dialog = QDialog(parent)
        self.ui = qt_coloredit.Ui_Dialog()
        self.ui.setupUi(self.dialog)
        self.parent = parent

        self.ui.colors.cellDoubleClicked.connect(self.edit_color)

        self.directives = directives
        self.splits = []
        total_rows = 0
        for i in directives:
            for j in i:
                total_rows += 1
        self.ui.colors.setRowCount(total_rows)
        row = 0
        for directive in directives:
            for group in directive:
                orig = ColorItem(group[0])
                replace = ColorItem(group[1])
                self.ui.colors.setItem(row, 0, orig)
                self.ui.colors.setItem(row, 1, replace)
                row += 1
            self.splits.append(row)

    def get_colors(self):
        new_colors = []
        tmp_group = []
        for i in range(self.ui.colors.rowCount()):
            orig = self.ui.colors.item(i, 0).text()
            replace = self.ui.colors.item(i, 1).text()
            tmp_group.append([orig, replace])
            if (i+1) in self.splits:
                new_colors.append(tmp_group)
                tmp_group = []
        return new_colors

    def edit_color(self):
        row = self.ui.colors.currentRow()
        column = self.ui.colors.currentColumn()
        old_color = self.ui.colors.currentItem().text()
        qcolor = QColorDialog().getColor(QColor("#"+old_color), self.dialog)
        if qcolor.isValid():
            new_color = qcolor.name()[1:].lower()
            self.ui.colors.setItem(row, column, ColorItem(new_color))
