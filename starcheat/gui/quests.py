"""
Qt quests management dialog
"""

import logging

from gui.itemedit import ItemEditOptions
from gui.common import text_to_html

import qt_quests

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QMessageBox


def make_quest_info(name, data):
    """Return an HTML summary of a quest from its data."""
    info = ""
    info += "<b>%s</b><br>" % name
    info += "%s<br><br>" % text_to_html(data["title"])
    info += "%s<br><br>" % text_to_html(data["fullText"])
    info += "<b>Pixels:</b> %s" % data["money"]
    return info


class Quests():
    def __init__(self, main_window):
        self.dialog = QDialog(main_window.window)
        self.ui = qt_quests.Ui_Dialog()
        self.ui.setupUi(self.dialog)
        self.main_window = main_window

        self.assets = main_window.assets
        self.player = main_window.player

        self.quests = self.read_quests()

        self.ui.quest_status.currentTextChanged.connect(self.filter_quests)
        self.ui.quest_list.currentItemChanged.connect(self.lookup_quest)
        self.ui.trash_button.clicked.connect(self.trash_quest)
        self.ui.edit_button.clicked.connect(self.edit_quest)

        self.filter_quests()
        self.update_statuses()

    def update_statuses(self):
        """Refresh quest status combo box."""
        self.ui.quest_status.clear()
        for status in sorted(self.quests.keys()):
            self.ui.quest_status.addItem(status.capitalize())

    def get_status(self):
        status = self.ui.quest_status.currentText()
        return status.lower()

    def edit_quest(self):
        """Launch JSON edit dialog for selected quest."""
        if self.ui.quest_list.currentItem() is None:
            return
        selected = self.selected_quest()
        edit = ItemEditOptions(self.dialog,
                               selected[0],
                               selected[1],
                               "Edit Quest Data")

        def save():
            name, value = edit.get_option()
            status = self.get_status()
            self.quests[status][name] = value

        edit.dialog.accepted.connect(save)
        edit.ui.name.setEnabled(False)
        edit.dialog.exec()

    def trash_quest(self):
        """Confirm with user and delete selected quest."""
        if self.ui.quest_list.currentItem() is None:
            return
        status = self.get_status()
        quest_name = self.ui.quest_list.currentItem().text()
        ask_dialog = QMessageBox(self.dialog)
        ask_dialog.setWindowTitle("Trash Quest")
        ask_dialog.setText("Are you sure?")
        ask_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ask_dialog.setDefaultButton(QMessageBox.No)
        ask_dialog.setIcon(QMessageBox.Question)
        if ask_dialog.exec() == QMessageBox.Yes:
            self.quests[status].pop(quest_name)
            self.update_statuses()
            self.filter_quests()
            self.lookup_quest()

    def selected_quest(self):
        """Return selected quest name and data."""
        status = self.get_status()
        quest_name = self.ui.quest_list.currentItem().text()
        return quest_name, self.quests[status][quest_name]

    def lookup_quest(self):
        """Update info box and button statuses using selected quest."""
        if self.ui.quest_list.currentItem() is None:
            self.ui.trash_button.setEnabled(False)
            self.ui.edit_button.setEnabled(False)
            self.ui.quest_info_label.setText("<b>Nothing selected.</b>")
            return
        selected = self.selected_quest()
        self.ui.trash_button.setEnabled(True)
        self.ui.edit_button.setEnabled(True)
        self.ui.quest_info_label.setText(make_quest_info(*selected))

    def filter_quests(self):
        """Filter quest list based on selected status."""
        status = self.get_status()
        self.ui.quest_list.clear()
        # no quests
        if not status in self.quests:
            return
        for quest_id in self.quests[status].keys():
            self.ui.quest_list.addItem(quest_id)
        self.ui.quest_list.setFocus()
        self.ui.quest_list.setCurrentRow(0)

    def read_quests(self):
        """Read quests from metadata and return dict sorted by status."""
        raw_quests = self.player.metadata.get_quests()
        quests = {}

        for k, v in raw_quests.items():
            status = v["status"]
            if not status in quests:
                quests[status] = {}
            quests[status][k] = v

        return quests

    def write_quests(self):
        """Convert and write sorted quest dict to metadata."""
        quests = {}

        for status_k, status_v in self.quests.items():
            for quest_k, quest_v in status_v.items():
                quests[quest_k] = quest_v

        self.player.metadata.set_quests(quests)
        self.main_window.window.setWindowModified(True)
