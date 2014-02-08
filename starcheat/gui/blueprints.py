"""
Qt blueprint/recipe management dialog
"""

from PyQt5.QtWidgets import QDialog, QListWidgetItem

import assets, qt_blueprints
from config import Config

# TODO: rework whole dialog with pretty icons and stuff like that

def new_blueprint(name, data):
    bp = {
        "name": name,
        "count": 1,
        "data": data
    }
    return bp

class BlueprintItem(QListWidgetItem):
    def __init__(self, blueprint):
        QListWidgetItem.__init__(self, blueprint["name"])
        self.blueprint = blueprint

class BlueprintLib():
    def __init__(self, parent, known_blueprints):
        """Blueprint library management dialog."""
        # BUG: some of the tier weapons are not importing correctly and showing
        # as duplicates in the available list
        # UPDATE: okay i think that's just caused by stripping the data?
        self.dialog = QDialog(parent)
        self.ui = qt_blueprints.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        assets_db_file = Config().read("assets_db")
        starbound_folder = Config().read("starbound_folder")
        self.assets = assets.Assets(assets_db_file, starbound_folder)

        self.blueprints = self.assets.blueprints()
        self.known_blueprints = known_blueprints

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

        self.ui.add_button.clicked.connect(self.add_blueprint)
        self.ui.remove_button.clicked.connect(self.remove_blueprint)

        self.ui.filter.textChanged.connect(self.update_available_list)
        self.ui.category.currentTextChanged.connect(self.update_available_list)

        self.ui.filter.setFocus()

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
            # TODO: we don't support data from asset blueprints yet'
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
