class Player(object):
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

        # haven't found any definitions for these in the assets
        self.mode_types = {
            "hardcore": "Hardcore",
            "normal": "Normal",
            "casual": "Casual",
        }

    def get_mode_type(self, name):
        """Return a mode type key name from its pretty name."""
        for key in self.mode_types.keys():
            if name == self.mode_types[key]:
                return key

    def sort_bag(self, bag, sort_by):
        def get_category(slot):
            name = slot["content"]["name"]
            item = self.assets.items().get_item_index(name)
            if item is not None:
                return item[3]
            else:
                return ""

        sort_map = {
            "name": lambda x: x["content"]["name"],
            "count": lambda x: x["content"]["count"],
            "category": get_category
        }

        filtered = [x for x in bag if x is not None]
        sorted_bag = sorted(filtered, key=sort_map[sort_by])
        # TODO: only handles main/tile bags atm
        sorted_bag += [None] * (40 - len(sorted_bag))

        return sorted_bag
