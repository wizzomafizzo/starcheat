"""
Qt blueprint/recipe management dialog
"""

from PyQt5.QtWidgets import QDialog

import assets, qt_blueprints

# TODO: rework whole dialog with pretty icons and stuff like that

class BlueprintLib():
    def __init__(self, parent, known_blueprints):
        """Blueprint library management dialog."""
        # BUG: somewhere in here is a bug that stops you from adding blueprints,
        # on windows, on only some save files
        # BUG: some of the tier weapons are not importing correctly and showing
        # as duplicates in the available list
        # TODO: is there something new in the crafting system? the dude in the
        # review is correct, there is no iron back lantern in the browser or in
        # the assets folder. is it generated on the fly like tech chips?
        self.dialog = QDialog(parent)
        self.ui = qt_blueprints.Ui_Dialog()
        self.ui.setupUi(self.dialog)

        self.blueprints = assets.Blueprints()
        self.known_blueprints = known_blueprints

        # populate known list
        self.ui.known_blueprints.clear()
        for blueprint in self.known_blueprints:
            self.ui.known_blueprints.addItem(blueprint)

        # populate initial available list
        self.ui.available_blueprints.clear()
        for blueprint in self.blueprints.get_all_blueprints():
            self.ui.available_blueprints.addItem(blueprint[0])

        # populate category combobox
        for cat in self.blueprints.get_categories():
            self.ui.category.addItem(cat[0])

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
            self.ui.available_blueprints.addItem(blueprint[0])
        self.ui.available_blueprints.setCurrentRow(0)

    def add_blueprint(self):
        """Add currently select blueprint in available list to known list."""
        try:
            selected = self.ui.available_blueprints.selectedItems()
        except AttributeError:
            # nothing selected
            return

        for blueprint in selected:
            # don't add more than one of each blueprint
            if blueprint.text() in self.known_blueprints:
                continue
            self.known_blueprints.append(blueprint.text())

        # regenerate the list
        self.known_blueprints.sort()
        self.ui.known_blueprints.clear()
        for i in range(len(self.known_blueprints)):
            self.ui.known_blueprints.addItem(self.known_blueprints[i])
        self.ui.known_blueprints.setCurrentRow(0)

    def remove_blueprint(self):
        """Remove currently selected blueprint in known list."""
        try:
            selected = self.ui.known_blueprints.selectedItems()
        except AttributeError:
            return

        for blueprint in selected:
            self.known_blueprints.remove(blueprint.text())

        self.known_blueprints.sort()
        self.ui.known_blueprints.clear()
        for blueprint in self.known_blueprints:
            self.ui.known_blueprints.addItem(blueprint)

    def get_known_list(self):
        return self.known_blueprints
