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

        race = self.player.get_race()
        gender = self.player.get_gender()
        # TODO: should be functions to access these
        idle = self.player.entity["identity"]["personalityIdle"]
        hair_type = self.player.entity["identity"]["hairType"]
        facial_hair = self.player.entity["identity"]["facialHairGroup"]
        facial_mask = self.player.entity["identity"]["facialMaskType"]

        for option in self.species.get_hair(race, gender):
            self.ui.hair_type.addItem(option)
        self.ui.hair_type.setCurrentText(hair_type)

        for option in self.species.get_facial_hair(race, gender):
            self.ui.facial_hair_type.addItem(option)
        self.ui.facial_hair_type.setCurrentText(facial_hair)

        for option in self.species.get_facial_mask(race, gender):
            self.ui.facial_mask_type.addItem(option)
        self.ui.facial_mask_type.setCurrentText(facial_mask)

        for option in self.species.get_personality():
            self.ui.personality.addItem(option[0])
        self.ui.personality.setCurrentText(idle)
