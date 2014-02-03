"""
Qt appearance management dialog
"""

from PyQt5.QtWidgets import QDialog, QColorDialog

import assets, qt_appearance

class Appearance():
    def __init__(self, parent, player):
        self.dialog = QDialog(parent)
        self.ui = qt_appearance.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.species = assets.Species()
        self.player = player

        # Current player stats
        race = self.player.get_race()
        gender = self.player.get_gender()
        personality = self.player.get_personality()
        hair = self.player.get_hair()
        facial_hair = self.player.get_facial_hair()
        facial_mask = self.player.get_facial_mask()

        hair_groups = self.species.get_hair_groups(race, gender)
        for option in hair_groups:
            self.ui.hair_group.addItem(option)
        self.ui.hair_type.setCurrentText(hair[0])
        print(len(hair_groups))
        if len(hair_groups) < 2: self.ui.hair_group.setEnabled(False)

        hair_types = self.species.get_hair_types(race, gender)
        for option in hair_types:
            self.ui.hair_type.addItem(option)
        self.ui.hair_type.setCurrentText(hair[1])
        if len(hair_types) < 2: self.ui.hair_type.setEnabled(False)

        facial_hair_groups = self.species.get_facial_hair_groups(race, gender)
        for option in facial_hair_groups:
            self.ui.facial_hair_group.addItem(option)
        self.ui.facial_hair_type.setCurrentText(facial_hair[0])
        if len(facial_hair_groups) < 2: self.ui.facial_hair_group.setEnabled(False)

        facial_hair_types = self.species.get_facial_hair_types(race, gender)
        for option in facial_hair_types:
            self.ui.facial_hair_type.addItem(option)
        self.ui.facial_hair_type.setCurrentText(facial_hair[1])
        if len(facial_hair_types) < 2: self.ui.facial_hair_type.setEnabled(False)

        facial_mask_groups = self.species.get_facial_mask_groups(race, gender)
        for option in facial_mask_groups:
            self.ui.facial_mask_group.addItem(option)
        self.ui.facial_mask_type.setCurrentText(facial_mask[0])
        if len(facial_mask_groups) < 2: self.ui.facial_mask_group.setEnabled(False)

        facial_mask_types = self.species.get_facial_mask_types(race, gender)
        for option in facial_mask_types:
            self.ui.facial_mask_type.addItem(option)
        self.ui.facial_mask_type.setCurrentText(facial_mask[1])
        if len(facial_mask_types) < 2: self.ui.facial_mask_type.setEnabled(False)

        for option in self.species.get_personality():
            self.ui.personality.addItem(option[0])
        self.ui.personality.setCurrentText(personality)
