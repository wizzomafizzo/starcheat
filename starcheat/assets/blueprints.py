import os


class Blueprints():
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

    def is_blueprint(self, key):
        if key.endswith(".recipe"):
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        offset = asset[2]
        length = asset[3]
        name = os.path.basename(asset[0]).split(".")[0]
        asset_type = "blueprint"
        asset_data = self.assets.read(key, path)

        if asset_data is None:
            return

        try:
            category = asset_data["groups"][1]
        except (KeyError, IndexError):
            category = "other"

        return (key, path, offset, length, asset_type, category, name, "")

    def get_all_blueprints(self):
        """Return a list of every indexed blueprints."""
        c = self.assets.db.cursor()
        c.execute("select * from assets where type = 'blueprint' order by name collate nocase")
        return c.fetchall()

    def get_categories(self):
        """Return a list of all unique blueprint categories."""
        c = self.assets.db.cursor()
        c.execute("select distinct category from assets where type = 'blueprint' order by category")
        return [x[0] for x in c.fetchall()]

    def filter_blueprints(self, category, name):
        """Filter blueprints based on category and name."""
        return self.assets.filter("blueprint", category, name)

    def get_blueprint(self, name):
        c = self.assets.db.cursor()
        c.execute("select key, path, desc from assets where type = 'blueprint' and name = ?", (name,))
        meta = c.fetchone()
        if meta is not None:
            blueprint = self.assets.read(meta[0], meta[1])
            return blueprint, meta[0], meta[1], meta[2]
        else:
            return None
