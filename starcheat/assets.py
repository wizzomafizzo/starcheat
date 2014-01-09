"""
Module for reading and indexing Starbound assets
"""

# TODO: investigate those massive json files at the top level. if they turn out
# to always be up to date (and include mods?) we could ditch a lot of this code

# TODO: this file should end up similar to save_file in that it has no external
# deps. need to:
# - remove all use of the config module, make them arguments to the classes
# - move all logging/exception handling to gui files
# - custom exception classes

import os, json, re, sqlite3, logging
from platform import system

from config import Config

# source: http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html
def parse_json(filename):
    """
    Parse a JSON file
    First remove comments and then use the json module package
    Comments look like :
    // ...
    or
    /*
    ...
    */
    """

    # Regular expression for comments
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )

    with open(filename) as f:
        content = ''.join(f.readlines())

        # Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        # Return json file
        return json.loads(content)

class AssetsDb():
    def __init__(self):
        """Master assets database."""
        self.mods_folder = os.path.normpath(os.path.join(Config().read("assets_folder"),
                                                         "..", "mods"))
        self.assets_db = Config().read("assets_db")
        try:
            open(self.assets_db)
        except FileNotFoundError:
            self.init_db()

        self.db = sqlite3.connect(self.assets_db)

    def init_db(self):
        """Create and populate a brand new assets database."""
        logging.info("Creating new assets db")

        tables = ("create table items (name text, filename text, folder text, icon text, category text)",
                  "create table blueprints (name text, filename text, folder text, category text)")
        db = sqlite3.connect(self.assets_db)
        c = db.cursor()

        for q in tables:
            c.execute(q)
        db.commit()
        db.close()

        logging.info("Adding vanilla items")
        Items().add_all_items()
        try:
            for mod in os.listdir(self.mods_folder):
                folder = os.path.join(self.mods_folder, mod, "assets")
                if os.path.isdir(folder):
                    logging.info("Adding %s items" % (mod))
                    Items(folder).add_all_items()
        except FileNotFoundError:
            pass

        logging.info("Adding vanilla blueprints")
        Blueprints().add_all_blueprints()
        try:
            for mod in os.listdir(self.mods_folder):
                folder = os.path.join(self.mods_folder, mod, "assets")
                if os.path.isdir(folder):
                    logging.info("Adding %s blueprints" % (mod))
                    Blueprints(folder).add_all_blueprints()
        except FileNotFoundError:
            pass

    def rebuild_db(self):
        logging.info("Rebuilding assets db")
        tables = ("items", "blueprints")
        c = self.db.cursor()
        for t in tables:
            c.execute("drop table %s" % t)
        self.db.commit()
        self.init_db()

class Blueprints():
    def __init__(self, folder=None):
        """Everything dealing with indexing and parsing blueprint asset files."""
        # override folder
        if folder == None:
            self.blueprints_folder = os.path.join(Config().read("assets_folder"), "recipes")
        else:
            self.blueprints_folder = os.path.join(folder, "recipes")
        self.db = AssetsDb().db

    def file_index(self):
        """Return a list of all valid blueprints files."""
        index = []
        for root, dirs, files in os.walk(self.blueprints_folder):
            for f in files:
                if re.match(".*\.recipe", f) != None:
                    index.append((f, root))
        logging.info("Found " + str(len(index)) + " blueprint files")
        return index

    def add_all_blueprints(self):
        """Parse and insert every indexable blueprint asset."""
        index = self.file_index()
        blueprints = []
        logging.info("Started indexing blueprints")
        for f in index:
            full_path = os.path.join(f[1], f[0])

            try:
                info = parse_json(full_path)
            except ValueError:
                continue

            name = f[0].partition(".")[0]
            filename = f[0]
            folder = f[1]

            try:
                category = info["groups"][1]
            except (KeyError, IndexError):
                category = "other"

            blueprints.append((name, filename, folder, category))

        c = self.db.cursor()
        q = "insert into blueprints values (?, ?, ?, ?)"
        c.executemany(q, blueprints)
        self.db.commit()
        logging.info("Finished indexing blueprints")

    def get_all_blueprints(self):
        """Return a list of every indexed blueprints."""
        c = self.db.cursor()
        c.execute("select * from blueprints order by name collate nocase")
        return c.fetchall()

    def get_categories(self):
        """Return a list of all unique blueprint categories."""
        c = self.db.cursor()
        c.execute("select distinct category from blueprints order by category")
        return c.fetchall()

    def filter_blueprints(self, category, name):
        """Filter blueprints based on category and name."""
        if category == "<all>":
            category = "%"
        name = "%" + name + "%"
        c = self.db.cursor()
        q = "select * from blueprints where category like ? and name like ? order by name collate nocase"
        c.execute(q, (category, name))
        result = c.fetchall()
        return result

class Items():
    def __init__(self, folder=None):
        """Everything dealing with indexing and parsing item asset files."""
        # folder override
        if folder == None:
            self.assets_folder = Config().read("assets_folder")
        else:
            self.assets_folder = folder

        self.items_folder = os.path.join(self.assets_folder, "items")
        self.objects_folder = os.path.join(self.assets_folder, "objects")
        self.tech_folder = os.path.join(self.assets_folder, "tech")
        self.ignore_items = ".*\.(png|config|frames|coinitem)"
        self.db = AssetsDb().db

    def file_index(self):
        """Return a list of every indexable Starbound item asset."""
        index = []
        # regular items
        for root, dirs, files in os.walk(self.items_folder):
            for f in files:
                # don't care about png and config and all that
                if re.match(self.ignore_items, f) == None:
                    index.append((f, root))
        # objects
        for root, dirs, files in os.walk(self.objects_folder):
            for f in files:
                if re.match(".*\.object$", f) != None:
                    index.append((f, root))
        # techs
        for root, dirs, files in os.walk(self.tech_folder):
            for f in files:
                if re.match(".*\.techitem$", f) != None:
                    index.append((f, root))
        logging.info("Found " + str(len(index)) + " item files")
        return index

    def add_all_items(self):
        """Insert metadata for every possible item into the database."""
        index = self.file_index()
        items = []

        logging.info("Started indexing items")
        for f in index:
            # load the asset's json file
            full_path = os.path.join(f[1], f[0])
            try:
                info = parse_json(full_path)
            except ValueError:
                continue

            # figure out the item's name. it can be a few things
            try:
                name = info["itemName"]
            except KeyError:
                try:
                    name = info["name"]
                except KeyError:
                    name = info["objectName"]

            filename = f[0]
            path = f[1]
            # just use the file extension as category
            category = f[0].partition(".")[2]

            # get full path to an inventory icon
            try:
                asset_icon = info["inventoryIcon"]
                if re.match(".*\.techitem$", f[0]) != None:
                    icon = self.assets_folder + asset_icon
                    # index dynamic tech chip items too
                    # TODO: do we keep the non-chip items in or not? i don't
                    #       think you're meant to have them outside tech slots
                    chip_name = name + "-chip"
                    items.append((chip_name, filename, path, icon, category))
                else:
                    icon = os.path.join(f[1], info["inventoryIcon"])
            except KeyError:
                if re.search("(sword|shield)", category) != None:
                    cat = category.replace("generated", "")
                    icon = os.path.join(self.assets_folder, "interface", "inventory", cat + ".png")
                else:
                    icon = self.missing_icon()

            items.append((name, filename, path, icon, category))

        c = self.db.cursor()
        q = "insert into items values (?, ?, ?, ?, ?)"
        c.executemany(q, items)
        self.db.commit()
        logging.info("Finished indexing items")

    def get_all_items(self):
        """Return a list of every indexed item."""
        c = self.db.cursor()
        c.execute("select * from items order by name collate nocase")
        return c.fetchall()

    def get_item(self, name):
        """
        Find the first hit in the DB for a given item name, return the
        parsed asset file and location.
        """
        c = self.db.cursor()
        c.execute("select folder, filename from items where name = ?", (name,))
        meta = c.fetchone()
        item = parse_json(os.path.join(meta[0], meta[1]))
        return item, meta[0], meta[1]

    def get_categories(self):
        """Return a list of all unique indexed item categories."""
        c = self.db.cursor()
        c.execute("select distinct category from items order by category")
        return c.fetchall()

    def get_item_icon(self, name):
        """Return the path and spritesheet offset of a given item name."""
        c = self.db.cursor()
        c.execute("select icon from items where name = ?", (name,))
        try:
            icon_file = c.fetchone()[0]
            # TODO: just double check the split usage, may be deprecated
            if system() != 'Windows':
                icon = icon_file.split(':')
            else:
                icon = icon_file.rsplit(':', icon_file.count(':') - 1)
            if len(icon) < 2:
                icon = icon[0], 0
        except TypeError:
            return None

        try:
            open(icon[0])
        except FileNotFoundError:
            return None

        if icon[1] == "chest":
            return icon[0], 16
        elif icon[1] == "pants":
            return icon[0], 32

        return icon[0], 0

    def get_item_image(self, name):
        """Return a vaild item image path for given item name."""
        item = self.get_item(name)

        # TODO: support for frame selectors
        # TODO: support for generated item images
        if "image" in item[0]:
            if re.search(":", item[0]["image"]):
                image = item[0]["image"].partition(":")[0]
            else:
                image = item[0]["image"]

            try:
                path = os.path.join(item[1], image)
                open(path)
                return path
            except FileNotFoundError:
                logging.exception("Unable to open icon file")
        else:
            return None

    def missing_icon(self):
        """Return the path to the default inventory placeholder icon."""
        return os.path.join(self.assets_folder, "interface", "inventory", "x.png")

    def filter_items(self, category, name):
        """Search for indexed items based on name and category."""
        if category == "<all>":
            category = "%"
        name = "%" + name + "%"
        c = self.db.cursor()
        c.execute("select * from items where category like ? and name like ? order by name collate nocase",
                  (category, name))
        result = c.fetchall()
        return result
