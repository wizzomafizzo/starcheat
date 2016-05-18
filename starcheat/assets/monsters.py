import logging
import random


class Monsters(object):
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

    def is_monster(self, key):
        if key.endswith(".monstertype"):
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        asset_data = self.assets.read(key, path)

        if asset_data is None:
            return

        if "type" in asset_data:
            return (key, path, "monster", "", asset_data["type"], "")
        else:
            logging.warning("Invalid monster: %s" % key)

    def all(self):
        """Return a list of all unique monster types."""
        q = "select distinct name from assets where type = 'monster' order by name"
        c = self.assets.db.cursor()
        c.execute(q)
        return c.fetchall()

    def random_monster(self):
        """Return type of a random monster as a string."""
        return random.choice(self.all())[0]

    def monster_seed(self):
        """Return a random monster seed as a string."""
        # okay, so i can't figure out exactly what this should be, but this
        # number seems to cause no crashes so far
        return str(random.randint(1, 9999999999999999999))
