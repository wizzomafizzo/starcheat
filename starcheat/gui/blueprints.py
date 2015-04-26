"""
Qt blueprint/recipe management dialog
"""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QListWidgetItem

import assets
import qt_blueprints
import saves
from config import Config


def new_blueprint(name, data):
    return saves.new_item_data(name, 1, data)


class BlueprintItem(QListWidgetItem):
    def __init__(self, blueprint):
        QListWidgetItem.__init__(self, blueprint["name"])
        self.blueprint = blueprint


class BlueprintLib():
    def __init__(self, parent, known_blueprints, new_blueprints):
        """Blueprint library management dialog."""
        self.dialog = QDialog(parent)
        self.ui = qt_blueprints.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.assets = assets.Assets(assets_db_file, starbound_folder)

        self.blueprints = self.assets.blueprints()
        self.known_blueprints = known_blueprints
        self.new_blueprints = new_blueprints

        # populate known list
        self.ui.known_blueprints.clear()
        for blueprint in self.known_blueprints:
            self.ui.known_blueprints.addItem(BlueprintItem(blueprint))
        self.ui.known_blueprints.sortItems(0)

        # populate initial available list
        self.ui.available_blueprints.clear()
        for blueprint in self.blueprints.get_all_blueprints():
            self.ui.available_blueprints.addItem(blueprint[4])

        # populate category combobox
        for cat in self.blueprints.get_categories():
            self.ui.category.addItem(cat)

        if len(self.new_blueprints) == 0:
            self.ui.clear_new_button.setEnabled(False)

        self.ui.add_button.clicked.connect(self.add_blueprint)
        self.ui.remove_button.clicked.connect(self.remove_blueprint)

        self.ui.filter.textChanged.connect(self.update_available_list)
        self.ui.category.currentTextChanged.connect(self.update_available_list)

        self.ui.available_blueprints.itemSelectionChanged.connect(self.update_blueprint_info)

        self.ui.clear_new_button.clicked.connect(self.clear_new_blueprints)

        self.ui.available_blueprints.setCurrentRow(0)
        self.ui.filter.setFocus()
        self.update_blueprint_info()

    def update_blueprint_info(self):
        selected = self.ui.available_blueprints.selectedItems()
        if len(selected) == 0:
            # nothing selected
            info = "<html><body><strong>Nothing Selected</strong></body></html>"
            self.ui.blueprint_info.setText(info)
            return

        name = selected[0].text()
        blueprint = self.assets.blueprints().get_blueprint(name)[0]
        if blueprint is not None:
            info = "<html><body>"
            info += "<strong>Craftable in:</strong><br>"
            info += ", ".join(blueprint["groups"])
            info += "<br>"
            info += "<strong>In:</strong><br>"
            for i in blueprint["input"]:
                info += "%s (%i)<br>" % (i["item"], i["count"])
            info += "<strong>Out:</strong><br>"
            info += "%s (%i)" % (blueprint["output"]["item"],
                                 blueprint["output"]["count"])
            info += "</body></html>"
        else:
            info = "<html><body><strong>Unknown Blueprint</strong></body></html>"
        self.ui.blueprint_info.setText(info)

    def update_available_list(self):
        """Populate available blueprints list based on current filter details."""
        category = self.ui.category.currentText()
        name = self.ui.filter.text()
        result = self.blueprints.filter_blueprints(category, name)
        self.ui.available_blueprints.clear()
        for blueprint in result:
            self.ui.available_blueprints.addItem(blueprint[4])
        self.ui.available_blueprints.setCurrentRow(0)

    def add_blueprint(self):
        """Add currently select blueprint in available list to known list."""
        try:
            selected = self.ui.available_blueprints.selectedItems()
        except AttributeError:
            # nothing selected
            return

        known = [x["name"] for x in self.known_blueprints]
        for blueprint in selected:
            # don't add more than one of each blueprint
            if blueprint.text() in known:
                continue
            self.known_blueprints.append(new_blueprint(blueprint.text(), {}))

        # regenerate the list
        self.ui.known_blueprints.clear()
        for blueprint in self.known_blueprints:
            self.ui.known_blueprints.addItem(BlueprintItem(blueprint))
        self.ui.known_blueprints.sortItems(0)
        self.ui.known_blueprints.setCurrentRow(0)

    def remove_blueprint(self):
        """Remove currently selected blueprint in known list."""
        try:
            selected = self.ui.known_blueprints.selectedItems()
        except AttributeError:
            return

        for item in selected:
            self.known_blueprints.remove(item.blueprint)

        self.ui.known_blueprints.clear()
        for blueprint in self.known_blueprints:
            self.ui.known_blueprints.addItem(BlueprintItem(blueprint))

    def get_known_list(self):
        return self.known_blueprints

    def clear_new_blueprints(self):
        self.new_blueprints = []
        self.ui.clear_new_button.setEnabled(False)
