"""
Qt appearance management dialog
"""

from PyQt5.QtWidgets import QDialog

import assets, qt_appearance

class Appearance():
    def __init__(self, parent):
        self.dialog = QDialog(parent)
        self.ui = qt_appearance.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.species = assets.Species()
