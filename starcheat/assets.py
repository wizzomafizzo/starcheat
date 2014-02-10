"""
Module for reading and indexing Starbound assets
"""

# TODO: this file should end up similar to save_file in that it has no external
# deps. need to:
# - custom exception classes

import os, json, re, sqlite3, logging
from io import BytesIO

from PIL import Image

from stardb.storage import BlockFile
from stardb.databases import AssetDatabase

# Regular expression for comments
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

ignore_assets = re.compile(".*\.(db|ds_store)", re.IGNORECASE)
ignore_items = re.compile(".*\.(png|config|frames)", re.IGNORECASE)

def parse_json(content, key):
    if key.endswith(".grapplinghook"):
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
    with open(filename) as f:
        content = ''.join(f.readlines())
        return parse_json(content, filename)

def read_default_color(species_data):
    color = []
    if type(species_data[0]) is str:
        return []
    for group in species_data[0].keys():
        color.append([group, species_data[0][group]])
    return color

class Assets():
    def __init__(self, db_file, starbound_folder):
        self.starbound_folder = starbound_folder
        self.db = sqlite3.connect(db_file)
        self.vanilla_assets = os.path.join(self.starbound_folder, "assets", "packed.pak")

    def init_db(self):
        c = self.db.cursor()
        c.execute("drop table if exists assets")
        c.execute("""create table assets
        (key text, path text, type text, category text, name text, desc text)""")
        self.db.commit()

    def total_indexed(self):
        c = self.db.cursor()
        try:
            c.execute("select count(*) from assets")
        except sqlite3.OperationalError:
            # database may be corrupt
            return 0
        return c.fetchone()[0]

    def create_index(self, asset_files=False):
        if not asset_files:
            asset_files = self.find_assets()

        blueprints = Blueprints(self)
        items = Items(self)
        species = Species(self)

        new_index_query = "insert into assets values (?, ?, ?, ?, ?, ?)"
        c = self.db.cursor()

        for asset in asset_files:
            yield (asset[0], asset[1])

            tmp_data = None
            if asset[0].endswith(".png"):
                tmp_data = (asset[0], asset[1], "image", "", "", "")
            elif blueprints.is_blueprint(asset[0]):
                tmp_data = blueprints.index_data(asset)
            elif species.is_species(asset[0]):
                tmp_data = species.index_data(asset)
            elif items.is_item(asset[0]):
                tmp_data = items.index_data(asset)

            if tmp_data != None:
                c.execute(new_index_query, tmp_data)

        self.db.commit()

    def find_assets(self):
        """Scan all Starbound assets and return key/file list.

        Includes mod files, .pak files.

        """
        index = []
        vanilla_path = os.path.join(self.starbound_folder, "assets")
        vanilla_assets = self.scan_asset_folder(vanilla_path)
        [index.append(x) for x in vanilla_assets]

        mods_path = os.path.join(self.starbound_folder, "mods")
        if not os.path.isdir(mods_path):
            return index

        for mod in os.listdir(mods_path):
            mod_folder = os.path.join(mods_path, mod)
            if os.path.isdir(mod_folder):
                mod_assets = self.scan_asset_folder(mod_folder)
                [index.append(x) for x in mod_assets]

        return index

    def scan_asset_folder(self, folder):
        pak_path = os.path.join(folder, "packed.pak")

        if os.path.isfile(pak_path):
            pak_file = open(pak_path, 'rb')
            bf = BlockFile(pak_file)
            db = AssetDatabase(bf)
            db.open()
            index = [(x, pak_path) for x in db.getFileList()]
            return index
        else:
            # old style, probably a mod
            # TODO: do packed mods still use the path key?
            index = []
            mod_assets = None
            files = os.listdir(folder)
            logging.debug(files)
            for f in files:
                if f.endswith(".modinfo"):
                    modinfo = os.path.join(folder, f)
                    try:
                        modinfo_data = load_asset_file(modinfo)
                        path = modinfo_data["path"]
                        mod_assets = os.path.join(folder, path)
                    except ValueError:
                        # really old mods
                        folder = os.path.join(folder, "assets")
                        if os.path.isdir(folder):
                            mod_assets = folder
            logging.debug(mod_assets)

            if mod_assets == None:
                return index
            elif not os.path.isdir(mod_assets):
                return index

            # now we can scan!
            for root, dirs, files in os.walk(mod_assets):
                for f in files:
                    if re.match(ignore_assets, f) == None:
                        asset_root = os.path.normpath(os.path.join(root.replace(folder, ""), f))
                        index.append((asset_root, folder))
            return index

    def read(self, key, path, image=False):
        if path.endswith(".pak"):
            pak_file = open(path, 'rb')
            bf = BlockFile(pak_file)
            db = AssetDatabase(bf)
            db.open()

            try:
                data = db[key]
            except KeyError:
                logging.warning("Unable to read db asset '%s' from '%s'" % (key, path))
                return None

            if image:
                return data
            else:
                asset = parse_json(data.decode("utf-8"), key)
                return asset
        else:
            asset_file = os.path.join(path, key[1:])
            try:
                if image:
                    return open(asset_file).read()
                else:
                    asset = load_asset_file(asset_file)
                    return asset
            except FileNotFoundError:
                logging.warning("Unable to read asset file '%s' from '%s'" % (key, path))
                return None

    def blueprints(self):
        return Blueprints(self)

    def items(self):
        return Items(self)

    def species(self):
        return Species(self)

    def get_all(self, asset_type):
        c = self.assets.db.cursor()
        c.execute("select * from assets where type = ? order by name collate nocase", (asset_type,))
        return c.fetchall()

    def get_categories(self, asset_type):
        c = self.assets.db.cursor()
        c.execute("select distinct category from assets where type = ? order by category", (asset_type,))
        return [x[0] for x in c.fetchall()]

    def filter(self, asset_type, category, name):
        if category == "<all>":
            category = "%"
        name = "%" + name + "%"
        c = self.db.cursor()
        q = """select * from assets where type = ? and category like ?
        and (name like ? or desc like ?) order by desc, name collate nocase"""
        c.execute(q, (asset_type, category, name, name))
        result = c.fetchall()
        return result

    def get_total(self, asset_type):
        c = self.assets.db.cursor()
        c.execute("select count(*) from assets where type = ?", (asset_type))
        return c.fetchone()[0]

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
        name = os.path.basename(asset[0]).split(".")[0]
        asset_type = "blueprint"
        asset_data = self.assets.read(key, path)

        if asset_data == None: return

        try:
            category = asset_data["groups"][1]
        except (KeyError, IndexError):
            category = "other"

        return (key, path, asset_type, category, name, "")

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

class Items():
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

    def is_item(self, key):
        if key.endswith(".object"):
            return True
        elif key.endswith(".techitem"):
            return True
        elif key.startswith("/items") and re.match(ignore_items, key) == None:
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        asset_type = "item"
        category = os.path.basename(asset[0]).split(".")[1]
        asset_data = self.assets.read(key, path)

        if asset_data == None: return

        name = False
        item_name_keys = ["itemName", "name", "objectName"]
        for item_name in item_name_keys:
            try:
                name = asset_data[item_name]
            except KeyError:
                pass

        desc = ""
        if "shortdescription" in asset_data:
            desc = asset_data["shortdescription"]

        if not name:
            logging.warning("Invalid item: %s" % key)
            return
        else:
            if key.endswith(".techitem"):
                name = name + "-chip"
            return (key, path, asset_type, category, name, desc)

    def filter_items(self, category, name):
        """Search for indexed items based on name and category."""
        return self.assets.filter("item", category, name)

    def get_all_items(self):
        """Return a list of every indexed item."""
        c = self.assets.db.cursor()
        c.execute("select * from assets where type = 'item' order by name collate nocase")
        return c.fetchall()

    def get_item(self, name):
        """
        Find the first hit in the DB for a given item name, return the
        parsed asset file and location.
        """
        c = self.assets.db.cursor()
        c.execute("select key, path, desc from assets where type = 'item' and name = ?", (name,))
        meta = c.fetchone()
        item = self.assets.read(meta[0], meta[1])
        return item, meta[0], meta[1], meta[2]

    def get_categories(self):
        """Return a list of all unique indexed item categories."""
        c = self.assets.db.cursor()
        c.execute("select distinct category from assets where type = 'item' order by category")
        return c.fetchall()

    def get_item_icon(self, name):
        """Return the path and spritesheet offset of a given item name."""
        try:
            item = self.get_item(name)
            icon_file = item[0]["inventoryIcon"]
            icon = icon_file.split(':')
            if len(icon) < 2:
                icon = [icon[0], 0]
        except (TypeError, KeyError):
            return None

        if icon[0] != "/":
            icon[0] = os.path.dirname(item[1]) + "/" + icon[0]

        icon_data = self.assets.read(icon[0], item[2], image=True)
        if icon_data == None:
            return None

        item_icon = Image.open(BytesIO(icon_data))

        icon_type = str(icon[1])
        if icon_type.startswith("chest"):
            item_icon = item_icon.crop((16, 0, 16+16, 16))
        elif icon_type.startswith("pants"):
            item_icon = item_icon.crop((32, 0, 32+16, 16))
        else:
            item_icon = item_icon.crop((0, 0, 16, 16))

        inv_icon = Image.new("RGBA", (16,16))
        inv_icon.paste(item_icon)
        return inv_icon

    def get_item_image(self, name):
        """Return a vaild item image path for given item name."""
        # TODO: support for frame selectors
        # TODO: support for generated item images
        if name == "generatedsword":
            return Image.open(BytesIO(self.sword_icon())).convert("RGBA")
        elif name == "generatedshield":
            return Image.open(BytesIO(self.shield_icon())).convert("RGBA")
        elif name == "generatedgun":
            return Image.open(BytesIO(self.sword_icon())).convert("RGBA")

        try:
            item = self.get_item(name)
            icon_file = item[0]["image"]
            icon = icon_file.split(':')
            icon = icon[0]
        except KeyError:
            logging.warning("No image key for "+name)
            return None

        if icon[0] != "/":
            icon = os.path.dirname(item[1]) + "/" + icon

        icon_data = self.assets.read(icon, item[2], image=True)

        if icon_data == None:
            logging.warning("Unable to read %s from %s" % (icon, item[2]))
            return None

        item_image = Image.open(BytesIO(icon_data)).convert("RGBA")
        return item_image

    def missing_icon(self):
        """Return the image data for the default inventory placeholder icon."""
        return self.assets.read("/interface/inventory/x.png", self.assets.vanilla_assets, image=True)

    def sword_icon(self):
        return self.assets.read("/interface/inventory/sword.png", self.assets.vanilla_assets, image=True)

    def shield_icon(self):
        return self.assets.read("/interface/inventory/shield.png", self.assets.vanilla_assets, image=True)

    def generate_gun(self, item):
        image_folder = item[0]["name"].replace(item[0]["rarity"].lower(), "")
        image_folder = image_folder.replace("plasma", "")
        generated_gun = {
            "itemName": "generatedgun",
            "level": 1.0,
            "levelScale": 2.0,
            "projectileType": "piercingbullet",
            "rarity": "common",
            "recoilTime": 0.1,
            "shortdescription": "Cheater's Remorse",
            "spread": 2,
            "twoHanded": True,
            "weaponType": "Sniper Rifle",
            "classMultiplier": 1.0,
            "projectile": { "level": 1.0, "power": 2.0 },
            "firePosition": [0.0, 0.0],
            "fireTime": 0.5,
            "generated": True,
            "handPosition": [-5.0, -2.0],
            "inspectionKind": "gun",
            "muzzleEffect": {
                "animation": "/animations/muzzleflash/bulletmuzzle3/bulletmuzzle3.animation",
                "fireSound": [ { "file": "/sfx/gun/sniper3.wav" } ]
            },
            "drawables": [
                {
                    "image": "/items/guns/randomgenerated/%s/butt/1.png" % image_folder,
                    "position": [ -8.0, 0.0 ]
                },
                {
                    "image": "/items/guns/randomgenerated/%s/middle/1.png" % image_folder,
                    "position": [ 0.0, 0.0 ]
                },
                {
                    "image": "/items/guns/randomgenerated/%s/barrel/1.png" % image_folder,
                    "position": [ 12.0, 0.0 ]
                }
            ],
            "inventoryIcon": [
                {
                    "image": "/items/guns/randomgenerated/%s/butt/1.png" % image_folder,
                    "position": [ -8.0, 0.0 ]
                },
                {
                    "image": "/items/guns/randomgenerated/%s/middle/1.png" % image_folder,
                    "position": [ 0.0, 0.0 ]
                },
                {
                    "image": "/items/guns/randomgenerated/%s/barrel/1.png" % image_folder,
                    "position": [ 12.0, 0.0 ]
                }
            ]
        }

        if "rarity" in item[0]:
            generated_gun["rarity"] = item[0]["rarity"]

        if "inspectionKind" in item[0]:
            generated_gun["inspectionKind"] = item[0]["inspectionKind"]

        if "handPosition" in item[0]:
            generated_gun["handPosition"] = [float(item[0]["handPosition"][0]),
                                             float(item[0]["handPosition"][1])]

        #if "firePosition" in item[0]:
        #    generated_gun["firePosition"] = [float(item[0]["firePosition"][0]),
        #                                     float(item[0]["firePosition"][1])]

        if "rateOfFire" in item[0]:
            generated_gun["fireTime"] = float(item[0]["rateOfFire"][0])

        if "recoilTime" in item[0]:
            generated_gun["fireTime"] = float(item[0]["recoilTime"])

        if "weaponType" in item[0]:
            generated_gun["weaponType"] = item[0]["weaponType"]
            generated_gun["shortdescription"] = "Cheater's " + item[0]["weaponType"]

        if "spread" in item[0]:
            generated_gun["spread"] = float(item[0]["spread"][0])

        if "muzzleFlashes" in item[0] and "fireSound" in item[0]:
            generated_gun["muzzleEffect"] = {
                "animation": item[0]["muzzleFlashes"][0],
                "fireSound": [ { "file": item[0]["fireSound"][0] } ]
            }

        if "projectileTypes" in item[0]:
            generated_gun["projectileType"] = item[0]["projectileTypes"][0]

        return generated_gun

    def generate_sword(self, item):
        try:
            image_folder = item[0]["name"].replace(item[0]["rarity"].lower(), "")
        except KeyError:
            image_folder = item[0]["name"]
        image_folder = re.sub("(uncommon|common|crappy)", "", image_folder)
        generated_sword = {
            "generated": True,
            "inspectionKind": "sword",
            "itemName": "generatedsword",
            "shortdescription": "Immersion Ruiner",
            "fireAfterWindup": True,
            "fireTime": 0.5,
            "level": 1.0,
            "levelScale": 2.0,
            "rarity": "common",
            "firePosition": [ 12.5, 3.0 ],
            "soundEffect": { "fireSound": [ { "file": "/sfx/melee/swing_hammer.wav" } ] },
            "weaponType": "uncommontier2hammer",
            "drawables": [ { "image": "/items/swords/randomgenerated/%s/handle/1.png" % image_folder },
                           { "image": "/items/swords/randomgenerated/%s/blade/1.png" % image_folder } ],
            "inventoryIcon": [ { "image": "/items/swords/randomgenerated/%s/handle/1.png" % image_folder },
                               { "image": "/items/swords/randomgenerated/%s/blade/1.png" % image_folder } ],
            "primaryStances": item[0]["primaryStances"]
        }

        generated_sword["primaryStances"]["projectileType"] = item[0]["primaryStances"]["projectileTypes"][0]
        generated_sword["primaryStances"]["projectile"]["level"] = 1.0
        generated_sword["primaryStances"]["projectile"]["power"] = 5.0

        if "altStances" in item[0]:
            generated_sword["altStances"] = item[0]["altStances"]
            generated_sword["altStances"]["projectileType"] = item[0]["altStances"]["projectileTypes"][0]
            generated_sword["altStances"]["projectile"]["level"] = 1.0
            generated_sword["altStances"]["projectile"]["power"] = 5.0

        if "inspectionKind" in item[0]:
            generated_sword["inspectionKind"] = item[0]["inspectionKind"]

        if "rateOfFire" in item[0]:
            generated_sword["fireTime"] = float(item[0]["rateOfFire"][0])

        generated_sword["weaponType"] = item[0]["name"]
        generated_sword["shortdescription"] = "Cheater's " + item[0]["name"]

        return generated_sword

    def generate_shield(self, item):
        generated_shield = {
            "generated": True,
            "itemName": "generatedshield",
            "rarity": "common",
            "shortdescription": "Cheater's Shield",
            "level": 1.0,
            "levelScale": 2.0,
            "maxStack": 1,
            "hitSound": "/sfx/melee/shield_block_metal2.wav",
            "inspectionKind": "",
            "knockbackDamageKind": "",
            "knockbackPower": 10,
            "recoil": 0.2,
            "damagePoly": [[-8,0], [8,18], [8,-18]],
            "shieldPoly": [[-8,0], [-8,12], [8,20], [8,-24], [-8,-12]],
            "statusEffects": [ { "amount": 30, "kind": "Shield" } ],
            "drawables": [
                { "image": "/items/shields/randomgenerated/tieredshields/tier1/images/1.png" }
            ],
            "inventoryIcon": [
                { "image": "/items/shields/randomgenerated/tieredshields/tier1/images/1.png:icon" }
            ]
        }

        #if "kind" in item[0]:
        #    generated_shield["inspectionKind"] = item[0]["kind"]

        if "shortdescription" in item[0]:
            generated_shield["shortdescription"] = item[0]["shortdescription"]

        if "rarity" in item[0]:
            generated_shield["rarity"] = item[0]["rarity"]

        if "hitSound" in item[0]:
            generated_shield["hitSound"] = item[0]["hitSound"]

        if "recoil" in item[0]["baseline"]:
            generated_shield["recoil"] = item[0]["baseline"]["recoil"]

        if "knockbackPower" in item[0]["baseline"]:
            generated_shield["knockbackPower"] = item[0]["baseline"]["knockbackPower"]

        if "knockbackDamageKind" in item[0]["baseline"]:
            generated_shield["knockbackDamageKind"] = item[0]["baseline"]["knockbackDamageKind"]

        if "statusEffects" in item[0]["baseline"]:
            generated_shield["statusEffects"] = item[0]["baseline"]["statusEffects"]

        if "shieldPoly" in item[0]["baseline"]:
            generated_shield["shieldPoly"] = item[0]["baseline"]["shieldPoly"]

        if "damagePoly" in item[0]["baseline"]:
            generated_shield["damagePoly"] = item[0]["baseline"]["damagePoly"]

        return generated_shield

class Species():
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder
        self.humanoid_config = self.assets.read("/humanoid.config", self.assets.vanilla_assets)

    def is_species(self, key):
        if key.endswith(".species"):
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        asset_data = self.assets.read(key, path)

        if asset_data == None: return

        if "kind" in asset_data:
            return (key, path, "species", "", asset_data["kind"], "")
        else:
            logging.warning("Invalid species: %s" % key)

    def get_species_list(self):
        """Return a formatted list of all species."""
        c = self.assets.db.cursor()
        c.execute("select distinct name from assets where type = 'species' order by name")
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
        c = self.assets.db.cursor()
        c.execute("select * from assets where type = 'species' and name = ?", (name.lower(),))
        species = c.fetchone()
        species_data = self.assets.read(species[0], species[1])
        if species_data == None:
            # corrupt save, no race set
            logging.warning("No race set on player")
            return "", ""
        else:
            return species, species_data

    def get_appearance_data(self, name, gender, key):
        species = self.get_species(name)
        # there is another json extension here where strings that have a , on
        # the end are treated as 1 item lists. there are also some species with
        # missing keys
        try:
            results = self.get_gender_data(species, gender)[key]
        except KeyError:
            return []
        if type(results) is str:
            return (results,)
        else:
            return results

    def get_facial_hair_types(self, name, gender, group):
        return self.get_appearance_data(name, gender, "facialHair")

    def get_facial_hair_groups(self, name, gender):
        return self.get_appearance_data(name, gender, "facialHairGroup")

    def get_facial_mask_types(self, name, gender, group):
        return self.get_appearance_data(name, gender, "facialMask")

    def get_facial_mask_groups(self, name, gender):
        return self.get_appearance_data(name, gender, "facialMaskGroup")

    def get_hair_types(self, name, gender, group):
        return self.get_appearance_data(name, gender, "hair")

    def get_hair_groups(self, name, gender):
        groups = self.get_appearance_data(name, gender, "hairGroup")
        if len(groups) == 0:
            return ("hair",)
        else:
            return groups

    def get_personality(self):
        return self.humanoid_config["charGen"]["personalities"]

    def get_gender_data(self, species_data, gender):
        if gender == "male":
            return species_data[1]["genders"][0]
        else:
            return species_data[1]["genders"][1]

    def get_default_colors(self, species):
        # just use first option
        species_data = self.get_species(species)[1]
        def val(key):
            if key in species_data:
                return read_default_color(species_data[key])
            else:
                return ""

        colors = {
            "bodyColor": val("bodyColor"),
            "undyColor": val("undyColor"),
            "hairColor": val("hairColor")
        }
        # TODO: there is an unbelievably complicated method for choosing default
        # player colors. i'm not sure if it's worth going into too much considering
        # it will only be used if a player switches species
        # it might be easier to just leave this out entirely. let user add/remove
        # their own directive colors
        directives = {
            "body": [colors["bodyColor"]],
            "emote": [colors["bodyColor"], colors["undyColor"]],
            "hair": [colors["hairColor"]],
            "facial_hair": [colors["bodyColor"]],
            "facial_mask": [colors["bodyColor"]]
        }
        return directives

    def get_preview_image(self, name, gender):
        species = self.get_species(name.lower())
        try:
            key = self.get_gender_data(species, gender)["characterImage"]
            return self.assets.read(key, species[0][1], image=True)
        except FileNotFoundError:
            # corrupt save, no race set
            logging.warning("No race set on player")
            return self.assets.read("/interface/inventory/x.png", self.assets.vanilla_assets, image=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    assets = Assets("assets.db", "/opt/starbound")
    assets.init_db()
    logging.info("Started indexing...")
    count = 0
    for i in assets.create_index():
        count += 1
    print(count)
    logging.info("Finished!")
