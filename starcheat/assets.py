"""
Module for reading and indexing Starbound assets
"""

# TODO: this file should end up similar to save_file in that it has no external
# deps. need to:
# - remove all use of the config module, make them arguments to the classes
# - move all logging/exception handling to gui files
# - custom exception classes

import os, json, re, sqlite3, logging
from platform import system

from stardb.storage import BlockFile
from stardb.databases import AssetDatabase

from config import Config

comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)
ignore_items = re.compile(".*\.(png|config|frames|coinitem|db|DS_Store)")

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

    with open(filename) as f:
        content = ''.join(f.readlines())

        # TODO: really annoying.. hopefully this is fixed after the patch
        if filename.endswith(".grapplinghook"):
            content = content.replace("[-.", "[-0.")

        # Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        # Return json file
        return json.loads(content)

def load_asset_file(filename):
    return parse_json(filename)

# TODO: there is some bug where assets w/ a 55 character path will generate their
# hash keys incorrectly. workaround needs to be put in place for it
# NOTE: because we need to be backwards compatible with the old assets and the stored
# paths are all relative i'm going to make up a prefix for all asset paths in pak
# files. thinking like: __pak_starbound__/items/foo/bar.sword
class StarAssets():
    def __init__(self, starbound_folder):
        self.starbound_folder = starbound_folder
        pak_filename = os.path.join(starbound_folder, "assets", "packed.pak")
        pak_file = open(pak_filename, 'rb')
        bf = BlockFile(pak_file)

        self.db = AssetDatabase(bf)
        self.db.open()
        self.index = self.db.getFileList()
        logging.info("%i total assets" % len(self.index))

    def load_asset(self, asset_key):
        """Parse and return Starbound asset JSON data."""
        try:
            asset = self.db[asset_key].decode("utf-8")
        except KeyError:
            logging.warning("Asset key %s does not exist" % asset_key)
            return None

        # TODO: really annoying.. hopefully this is fixed after the patch
        if asset_key.endswith(".grapplinghook"):
            asset = asset.replace("[-.", "[-0.")

        # Looking for comments
        match = comment_re.search(asset)
        while match:
            # single line comment
            asset = asset[:match.start()] + asset[match.end():]
            match = comment_re.search(asset)

        # Return json data
        return json.loads(asset)

    def check_all_assets(self):
        self.blueprints()
        self.blueprints().index_data()
        self.items()
        self.items().index_data()
        self.species()
        self.species().index_data()

    def blueprints(self):
        return StarBlueprints(self)

    def items(self):
        return StarItems(self)

    def species(self):
        return StarSpecies(self)

class StarBlueprints():
    def __init__(self, assets):
        self.assets = assets
        self.blueprints = self.all()

        print(len(self.blueprints))

    def all(self):
        keys = []
        for asset in self.assets.index:
            if asset.startswith("/recipes") and asset.endswith(".recipe"):
                keys.append(asset)
        return keys

    def index_data(self):
        index = []
        for blueprint in self.blueprints:
            info = self.assets.load_asset(blueprint)
            if info == None:
                continue
            name = os.path.basename(blueprint).split(".")[0]
            filename = os.path.basename(blueprint)
            folder = os.path.dirname(blueprint)
            try:
                category = info["groups"][1]
            except IndexError:
                category = "other"
            index.append((name, filename, folder, category))
        print(len(index), index[0])
        return index

class StarItems():
    def __init__(self, assets):
        self.assets = assets
        self.items = self.all()

        print(len(self.items))

    def all(self):
        keys = []
        for asset in self.assets.index:
            if asset.startswith("/items") and re.match(ignore_items, asset) == None:
                keys.append(asset)
            elif asset.endswith(".object"):
                keys.append(asset)
            elif asset.endswith(".techitem"):
                keys.append(asset)
        return keys

    def index_data(self):
        index = []

        for item in self.items:
            info = self.assets.load_asset(item)
            if info == None:
                continue

            # figure out the item's name. it can be a few things
            name = False
            item_name_keys = ["itemName", "name", "objectName"]
            for key in item_name_keys:
                try:
                    name = info[key]
                    continue
                except KeyError:
                    pass
            # don't import items without names
            if not name:
                logging.warning("No item name for %s" % item)
                continue

            filename = os.path.basename(item)
            folder = os.path.dirname(item)
            category = os.path.basename(item).split(".")[1]

            try:
                icon = info["inventoryIcon"]
            except KeyError:
                logging.warning("Missing icon for %s" % item)
                icon = "/interface/inventory/x.png"

            index.append((name, filename, folder, icon, category))

        print(len(index), index[0])
        return index

class StarSpecies():
    def __init__(self, assets):
        self.assets = assets
        self.species = self.all()

        print(len(self.species))

    def all(self):
        keys = []
        for asset in self.assets.index:
            if asset.startswith("/species") and asset.endswith(".species"):
                keys.append(asset)
        return keys

    def index_data(self):
        index = []
        for species in self.species:
            info = self.assets.load_asset(species)
            if info == None:
                continue

            filename = os.path.basename(species)
            folder = os.path.dirname(species)

            try:
                name = info["kind"]
            except KeyError:
                logging.warning("No kind key for species %s" % species)
                continue

            index.append((name, filename, folder))

        print(len(index), index[0])
        return index

def mod_asset_folder(mod_folder):
    """Read mod assets folder from modinfo file."""
    # TODO: this still doesn't work if mod contains multiple modinfo files
    # like tabula rasa
    path = "."
    for file in os.listdir(mod_folder):
        if file.endswith(".modinfo"):
            modinfo = os.path.join(mod_folder, file)
            try:
                path = parse_json(modinfo)["path"]
            except ValueError:
                # gosh this is hard...
                last_ditch = os.path.join(mod_folder, "assets")
                if os.path.isdir(last_ditch):
                    path = last_ditch

    return os.path.realpath(os.path.join(mod_folder, path))

class AssetsDb():
    def __init__(self):
        """Master assets database."""
        self.mods_folder = os.path.normpath(os.path.join(Config().read("starbound_folder"), "mods"))
        self.assets_db = Config().read("assets_db")
        self.db = sqlite3.connect(self.assets_db)

    def init_db(self):
        """Create and populate a brand new assets database."""
        logging.info("Creating new assets db")

        tables = ("create table items (name text, filename text, folder text, icon text, category text)",
                  "create table blueprints (name text, filename text, folder text, category text)",
                  "create table species (name text, filename text, folder text)")
        db = sqlite3.connect(self.assets_db)
        c = db.cursor()

        for q in tables:
            c.execute(q)
        db.commit()
        db.close()

    def get_total_indexed(self):
        c = self.db.cursor()
        tables = ("(select count(*) from items)",
                  "(select count(*) from blueprints)",
                  "(select count(*) from species)")
        q = "select " + " + ".join([x for x in tables])
        try:
            c.execute(q)
        except sqlite3.OperationalError:
            # database probably corrupt
            return 0
        return c.fetchone()[0]

    def rebuild_db(self):
        logging.info("Rebuilding assets db")
        tables = ("items", "blueprints", "species")
        c = self.db.cursor()
        for t in tables:
            c.execute("drop table %s" % t)
        self.db.commit()
        self.init_db()
        # TODO: bit weird these are here but not in init_db
        # this is only so the options dialog rebuild db works for now
        logging.info("Adding items")
        Items().add_all_items()
        logging.info("Adding blueprints")
        Blueprints().add_all_blueprints()
        logging.info("Adding species")
        Species().add_all_species()

class Blueprints():
    def __init__(self):
        """Everything dealing with indexing and parsing blueprint asset files."""
        # override folder
        self.db = AssetsDb().db

    def file_index(self, folder):
        """Return a list of all valid blueprints files."""
        index = []
        logging.info("Indexing " + folder)
        if not os.path.isdir(folder):
            logging.warning("Missing " + folder)
            return index
        for root, dirs, files in os.walk(folder):
            for f in files:
                if re.match(".*\.recipe", f) != None:
                    index.append((f, root))
        logging.info("Found " + str(len(index)) + " blueprint files")
        return index

    def add_all_blueprints(self):
        """Parse and insert every indexable blueprint asset."""
        mods_folder = os.path.join(Config().read("starbound_folder"), "mods")
        assets_folder = Config().read("assets_folder")

        index = self.file_index(os.path.join(assets_folder, "recipes"))

        if os.path.isdir(mods_folder):
            for mod in os.listdir(mods_folder):
                path = os.path.join(mods_folder, mod)
                if not os.path.isdir(path): continue
                assets = mod_asset_folder(path)
                if os.path.isdir(os.path.join(assets, "recipes")):
                    index += self.file_index(os.path.join(assets, "recipes"))
                else:
                    logging.debug("No blueprints in " + mod)

        blueprints = []
        logging.info("Started indexing blueprints")
        for f in index:
            full_path = os.path.join(f[1], f[0])

            try:
                info = load_asset_file(full_path)
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

    def get_blueprints_total(self):
        c = self.db.cursor()
        c.execute("select count(*) from blueprints")
        return c.fetchone()[0]

class Items():
    def __init__(self):
        """Everything dealing with indexing and parsing item asset files."""
        self.db = AssetsDb().db
        self.starbound_folder = Config().read("starbound_folder")

    def file_index(self, assets_folder):
        """Return a list of every indexable Starbound item asset."""
        index = []
        logging.info("Indexing " + assets_folder)

        items_folder = os.path.join(assets_folder, "items")
        if not os.path.isdir(items_folder):
            # if this folder is gone the rest is probably screwed too
            logging.warning("Missing " + items_folder)
            return index
        # TODO: there is an ignore list in a config file we could use
        ignore_items = re.compile(".*\.(png|config|frames|coinitem|db|ds_store)", re.IGNORECASE)
        # regular items
        for root, dirs, files in os.walk(items_folder):
            for f in files:
                # don't care about png and config and all that
                if re.match(ignore_items, f) == None:
                    index.append((f, root))

        objects_folder = os.path.join(assets_folder, "objects")
        # objects
        for root, dirs, files in os.walk(objects_folder):
            for f in files:
                if re.match(".*\.object$", f) != None:
                    index.append((f, root))

        tech_folder = os.path.join(assets_folder, "tech")
        # techs
        for root, dirs, files in os.walk(tech_folder):
            for f in files:
                if re.match(".*\.techitem$", f) != None:
                    index.append((f, root))

        logging.info("Found " + str(len(index)) + " item files")
        return index

    def add_all_items(self):
        """Insert metadata for every possible item into the database."""
        mods_folder = os.path.join(self.starbound_folder, "mods")
        index = self.file_index(Config().read("assets_folder"))

        # Index mods
        if os.path.isdir(mods_folder):
            for mod in os.listdir(mods_folder):
                path = os.path.join(mods_folder, mod)
                if not os.path.isdir(path): continue
                assets = mod_asset_folder(path)
                if os.path.isdir(os.path.join(assets)):
                    index += self.file_index(os.path.join(assets))
                else:
                    logging.debug("No assets in " + mod)

        items = []
        logging.info("Started indexing items")
        for f in index:
            # load the asset's json file
            full_path = os.path.join(f[1], f[0])
            try:
                info = load_asset_file(full_path)
            except ValueError:
                logging.exception("Unable to index asset: " + full_path)
                continue

            # figure out the item's name. it can be a few things
            name = False
            item_name_keys = ["itemName", "name", "objectName"]
            for key in item_name_keys:
                try:
                    name = info[key]
                    continue
                except KeyError:
                    pass
            # don't import items without names
            # i think technically we can without problems but idk how safe exactly
            if not name:
                logging.warning("No item name for %s" % full_path)
                continue

            filename = f[0]
            path = f[1]
            # just use the file extension as category
            category = f[0].partition(".")[2]

            # get full path to an inventory icon
            try:
                asset_icon = info["inventoryIcon"]
                if re.match(".*\.techitem$", f[0]) != None:
                    icon = os.path.join(self.starbound_folder, "assets", asset_icon[1:])
                    # index dynamic tech chip items too
                    # TODO: do we keep the non-chip items in or not? i don't
                    #       think you're meant to have them outside tech slots
                    chip_name = name + "-chip"
                    items.append((chip_name, filename, path, icon, category))
                else:
                    icon = os.path.join(f[1], info["inventoryIcon"])
            except KeyError:
                inv_assets = os.path.join(self.starbound_folder, "assets", "interface", "inventory")
                if re.search("(sword|shield)", category) != None:
                    cat = category.replace("generated", "")
                    icon = os.path.join(inv_assets, cat + ".png")
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
        item = load_asset_file(os.path.join(meta[0], meta[1]))
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
            return self.missing_icon(), 0

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
        return os.path.join(self.starbound_folder, "assets", "interface", "inventory", "x.png")

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

    def get_items_total(self):
        c = self.db.cursor()
        c.execute("select count(*) from items")
        return c.fetchone()[0]

class Species():
    def __init__(self):
        """Everything dealing with indexing and parsing species asset files."""
        self.starbound_folder = Config().read("starbound_folder")
        # TODO: this feels too hacky. remove it
        try:
            self.humanoid_config = load_asset_file(os.path.join(self.starbound_folder,
                                                                "assets", "humanoid.config"))
        except FileNotFoundError:
            logging.exception("Missing humanoid.config")
            self.humanoid_config = None
        self.db = AssetsDb().db

    def file_index(self, folder):
        """Return a list of all valid species files from a given folder."""
        index = []
        logging.info("Indexing " + folder)
        if not os.path.isdir(folder):
            # if this folder is gone the rest is probably screwed too
            logging.warning("Missing " + folder)
            return index
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.endswith(".species"):
                    index.append((f, root))
        logging.info("Found " + str(len(index)) + " species files")

        return index

    def add_all_species(self):
        """Parse and insert every indexable species asset."""
        mods_folder = os.path.join(self.starbound_folder, "mods")
        assets_folder = os.path.join(self.starbound_folder, "assets")

        index = self.file_index(os.path.join(assets_folder, "species"))

        if os.path.isdir(mods_folder):
            for mod in os.listdir(mods_folder):
                path = os.path.join(mods_folder, mod)
                if not os.path.isdir(path): continue
                assets = mod_asset_folder(path)
                if os.path.isdir(os.path.join(assets, "species")):
                    index += self.file_index(os.path.join(assets, "species"))
                else:
                    logging.debug("No species in " + mod)

        species = []
        logging.info("Started indexing species")
        for f in index:
            full_path = os.path.join(f[1], f[0])
            filename = f[0]
            # top assets folder
            path = os.path.realpath(os.path.join(f[1], ".."))

            try:
                info = load_asset_file(full_path)
            except ValueError:
                continue

            try:
                name = info["kind"]
            except (KeyError, IndexError):
                logging.warning("Could not read species file %s" % (f[0]))

            species.append((name, filename, path))

        c = self.db.cursor()
        q = "insert into species values (?, ?, ?)"
        c.executemany(q, species)
        self.db.commit()
        logging.info("Finished indexing species")

    def get_species_list(self):
        """Return a formatted list of all species."""
        c = self.db.cursor()
        c.execute("select distinct name from species order by name")
        names = [x[0] for x in c.fetchall()]
        formatted = []
        for s in names:
            try:
                formatted.append(s[0].upper() + s[1:])
            except IndexError:
                formatted.append(s)
                logging.exception("Unable to format species: %s", s)
        return formatted

    def get_species(self, name):
        """Look up a species from the index and return contents of species files."""
        c = self.db.cursor()
        c.execute("select * from species where name = ?", (name,))
        species = c.fetchone()
        try:
            species_data = load_asset_file(os.path.join(species[2], "species", species[1]))
        except TypeError:
            # corrupt save, no race set
            logging.warning("No race set on player")
            return "", ""
        return species, species_data

    def get_all_species(self):
        c = self.db.cursor()
        c.execute("select * from species")
        return c.fetchall()

    def get_facial_hair(self, name, gender):
        species = self.get_species(name)
        return self.get_gender_data(species, gender)["facialHair"]

    def get_facial_mask(self, name, gender):
        species = self.get_species(name)
        return self.get_gender_data(species, gender)["facialMask"]

    def get_hair(self, name, gender):
        species = self.get_species(name)
        return self.get_gender_data(species, gender)["hair"]

    def get_personality(self):
        # BUG: remove this workaround. okay for now since appearance isn't working anyway
        if self.humanoid_config == None:
            return []
        else:
            return self.humanoid_config["charGen"]["personalities"]

    def get_gender_data(self, species_data, gender):
        if gender == "male":
            return species_data[1]["genders"][0]
        else:
            return species_data[1]["genders"][1]

    def get_preview_image(self, name, gender):
        species = self.get_species(name.lower())
        try:
            return os.path.join(species[0][2], self.get_gender_data(species, gender)["characterImage"][1:])
        except IndexError:
            # corrupt save, no race set
            logging.warning("No race set on player")
            return os.path.join(self.starbound_folder, "assets", "interface", "inventory", "x.png")

    def get_species_total(self):
        c = self.db.cursor()
        c.execute("select count(*) from species")
        return c.fetchone()[0]

if __name__ == "__main__":
    assets = StarAssets("/opt/starbound")
    assets.check_all_assets()
