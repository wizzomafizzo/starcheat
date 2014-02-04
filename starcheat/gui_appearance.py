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
            "hair_group": self.player.get_hair()[0],
            "hair_type": self.player.get_hair()[1],
            "facial_hair_group": self.player.get_facial_hair()[0],
            "facial_hair_type": self.player.get_facial_hair()[1],
            "facial_mask_group": self.player.get_facial_mask()[0],
            "facial_mask_type": self.player.get_facial_mask()[1]
        }
        appearance_values = ("hair_group", "hair_type",
                             "facial_hair_group", "facial_hair_type",
                             "facial_mask_group", "facial_mask_type")

        for value in appearance_values:
            asset_data = getattr(self.species, "get_%ss" % value)(race, gender)
            widget = getattr(self.ui, value)
            for option in asset_data:
                widget.addItem(option)
            widget.setCurrentText(current_appearance[value])
            if len(asset_data) < 2: widget.setEnabled(False)

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
