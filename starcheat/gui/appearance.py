"""
Qt appearance management dialog
"""

from PyQt5.QtWidgets import QDialog, QColorDialog

import assets, qt_appearance

class Appearance():
    def __init__(self, main_window):
        self.dialog = QDialog(main_window.window)
        self.ui = qt_appearance.Ui_Dialog()
        self.ui.setupUi(self.dialog)
        self.main_window = main_window

        self.species = assets.Species()
        self.player = main_window.player

        race = main_window.ui.race.currentText()
        self.player.set_race(race)
        self.player.set_gender(main_window.get_gender())

        # Current player stats
        race = self.player.get_race()
        gender = self.player.get_gender()
        personality = self.player.get_personality()

        current_appearance = {
            "hair": self.player.get_hair(),
            "facial_hair": self.player.get_facial_hair(),
            "facial_mask": self.player.get_facial_mask()
        }
        appearance_values = ("hair_group", "hair_type",
                             "facial_hair_group", "facial_hair_type",
                             "facial_mask_group", "facial_mask_type")
        appearance_values = ("hair", "facial_hair", "facial_mask")

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

    def write_appearance_values(self):
        hair = self.ui.hair_group.currentText(), self.ui.hair_type.currentText()
        facial_hair = self.ui.facial_hair_group.currentText(), self.ui.facial_hair_type.currentText()
        facial_mask = self.ui.facial_mask_group.currentText(), self.ui.facial_mask_type.currentText()
        personality = self.ui.personality.currentText()
        self.player.set_hair(*hair)
        self.player.set_facial_hair(*facial_hair)
        self.player.set_facial_mask(*facial_mask)
        self.player.set_personality(personality)
        self.main_window.window.setWindowModified(True)
