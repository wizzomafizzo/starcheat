"""
Module for reading and indexing Starbound assets
"""

import os
import json
import re
import sqlite3
import logging
import random

from io import BytesIO
from PIL import Image

import starbound
import starbound.btreedb4

# Regular expression for comments
comment_re = re.compile(
    '("(\\[\s\S]|[^"])*")|((^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?)',
    re.DOTALL | re.MULTILINE
)

ignore_assets = re.compile(".*\.(db|ds_store|ini|psd|patch)", re.IGNORECASE)
ignore_items = re.compile(".*\.(png|config|frames|lua)", re.IGNORECASE)

replace_directive_re = re.compile(
    "(?:\?replace((?:;[a-fA-F0-9]{1,6}=[a-fA-F0-9]{1,6}){1,}))"
)

# available colors for text
colors = ["Red", "Orange", "Yellow", "Green", "Blue",
          "Black", "White", "Magenta", "DarkMagenta",
          "Gray", "LightGray", "DarkGray", "DarkGreen",
          "Pink", "Clear"]


def parse_json(content, key):
    decoder = json.JSONDecoder(strict=False)
    # Looking for comments
    # Allows for // inside of the " " JSON data
    content = comment_re.sub(lambda m: m.group(1) or '', content)

    # Return json file
    return decoder.decode(content)


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

def read_color_directives(data):
    unpack_dir = data.split("?replace;")
    directives = []
    for directive in unpack_dir[1:]:
        unpack_gr = directive.split(";")
        groups = []
        for group in unpack_gr:
            groups.append(group.split("="))
        directives.append(groups)
    return directives

def make_color_directives(colors):
    string = ""
    for directive in colors:
        if len(directive) == 0:
            continue
        string += "?replace"
        for group in directive:
            string += ";%s=%s" % (group[0], group[1])
    return string

def asset_category(keyStr):
    """
    Returns the asset key extension as the category
    :param keyStr: the asset's key.
    """
    extension = os.path.splitext(keyStr)[1]
    if extension == '':
        return ''
    else:
        return extension[1:]  # removes the . from the extension

# from: http://stackoverflow.com/a/7548779
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    if lv == 1:  # might not be supported in starbound
        v = int(value, 16)*17
        return v, v, v
    if lv == 3:  # might not be supported in starbound
        return tuple(int(value[i:i+1], 16)*17 for i in range(0, 3))
    if lv == 6:
        # only allow values that can be split into 3 decimals <= 255
        return tuple(int(value[i:i+int(lv/3)], 16) for i in range(0, lv, int(lv/3)))
    return None

def unpack_color_directives(data):
    # won't grab fade directives
    replace_matches = replace_directive_re.findall(data)
    groups = []
    for directive in replace_matches:
        unpack_gr = directive.split(";")
        for group in unpack_gr[1:]:
            hexkey, hexval = tuple(group.split("="))
            rgbkey = hex_to_rgb(hexkey)
            rgbval = hex_to_rgb(hexval)
            if rgbkey is not None and rgbval is not None:
                groups.append((rgbkey,rgbval))
    return dict(groups)

def replace_colors(image, dict_colors):
    pixel_data = image.load()

    result_img = image.copy()
    result_pixel_data = result_img.load()
    for (key, value) in dict_colors.items():
        for y in range(result_img.size[1]):
            for x in range(result_img.size[0]):
                pixel = pixel_data[x,y]
                if pixel[0] == key[0] and pixel[1] == key[1] and pixel[2] == key[2]:
                    if result_img.mode == "RGBA":
                        result_pixel_data[x,y] = (value + (pixel[3],))
                    elif result_img.mode == "RGB":
                        result_pixel_data[x,y] = value
    return result_img

def string_color(name):
    if name in colors:
        return "^" + name + ";"
    else:
        return ""


class Assets():
    def __init__(self, db_file, starbound_folder):
        self.starbound_folder = starbound_folder
        self.mods_folder = os.path.join(self.starbound_folder, "giraffe_storage", "mods")
        self.db = sqlite3.connect(db_file)
        self.vanilla_assets = os.path.join(self.starbound_folder, "assets", "packed.pak")
        self.image_cache = {}

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
        logging.info("Creating new assets index...")
        if not asset_files:
            asset_files = self.find_assets()

        blueprints = Blueprints(self)
        items = Items(self)
        species = Species(self)
        monsters = Monsters(self)
        techs = Techs(self)

        new_index_query = "insert into assets values (?, ?, ?, ?, ?, ?)"
        c = self.db.cursor()

        for asset in asset_files:
            yield (asset[0], asset[1])

            tmp_data = None

            if asset_category(asset[0]) != '':
                if asset[0].endswith(".png"):
                    tmp_data = (asset[0], asset[1], "image", "", "", "")
                elif blueprints.is_blueprint(asset[0]):
                    tmp_data = blueprints.index_data(asset)
                elif species.is_species(asset[0]):
                    tmp_data = species.index_data(asset)
                elif items.is_item(asset[0]):
                    tmp_data = items.index_data(asset)
                elif monsters.is_monster(asset[0]):
                    tmp_data = monsters.index_data(asset)
                elif techs.is_tech(asset[0]):
                    tmp_data = techs.index_data(asset)
            else:
                logging.warning("Skipping invalid asset (no file extension) %s in %s" % (asset[0], asset[1]))

            if tmp_data is not None:
                c.execute(new_index_query, tmp_data)

        self.db.commit()
        logging.info("Finished creating index")

    def find_assets(self):
        """Scan all Starbound assets and return key/file list.

        Includes mod files, .pak files.

        """
        index = []
        vanilla_path = os.path.join(self.starbound_folder, "assets")
        logging.info("Scanning vanilla assets")
        vanilla_assets = self.scan_asset_folder(vanilla_path)
        [index.append(x) for x in vanilla_assets]

        mods_path = self.mods_folder
        if not os.path.isdir(mods_path):
            return index

        for mod in os.listdir(mods_path):
            mod_folder = os.path.join(mods_path, mod)
            if os.path.isdir(mod_folder):
                logging.info("Scanning mod folder: " + mod)
                mod_assets = self.scan_asset_folder(mod_folder)
                [index.append(x) for x in mod_assets]
            elif mod_folder.endswith(".modpak"):
                logging.info("Scanning modpak: " + mod)
                mod_assets = self.scan_modpak(mod_folder)
                [index.append(x) for x in mod_assets]
        return index

    def scan_modpak(self, modpak):
        # TODO: may need support for reading the mod folder from the pakinfo file
        db = starbound.open_file(modpak)
        index = [(x, modpak) for x in db.get_index()]
        return index

    def scan_asset_folder(self, folder):
        pak_path = os.path.join(folder, "packed.pak")

        if os.path.isfile(pak_path):
            db = starbound.open_file(pak_path)
            index = [(x, pak_path) for x in db.get_index()]
            return index
        else:
            # old style, probably a mod
            index = []
            mod_assets = None
            files = os.listdir(folder)

            # TODO: will need more logic to handle .modpack with modinfo inside.
            found_mod_info = False

            for f in files:
                if f.endswith(".modinfo"):
                    modinfo = os.path.join(folder, f)
                    try:
                        modinfo_data = load_asset_file(modinfo)
                        path = "./"
                        if "path" in modinfo_data.keys():
                            path = modinfo_data["path"]
                        mod_assets = os.path.join(folder, path)
                        found_mod_info = True
                    except ValueError:
                        # really old mods
                        folder = os.path.join(folder, "assets")
                        if os.path.isdir(folder):
                            mod_assets = folder

            if mod_assets is None:
                return index
            elif found_mod_info and self.is_packed_file(mod_assets):
                # TODO: make a .pak scanner function that works for vanilla and mods
                pak_path = os.path.normpath(mod_assets)
                db = starbound.open_file(pak_path)
                for x in db.get_index():
                    # removes thumbs.db etc from user pak files
                    if re.match(ignore_assets, x) is None:
                        index.append((x, pak_path))
                return index
            elif not os.path.isdir(mod_assets):
                return index

            # now we can scan!
            for root, dirs, files in os.walk(mod_assets):
                for f in files:
                    if re.match(ignore_assets, f) is None:
                        asset_folder = os.path.normpath(mod_assets)
                        asset_file = os.path.normpath(os.path.join(root.replace(folder, ""), f))
                        index.append((asset_file, asset_folder))
            return index


    def is_packed_file(self, path):
        """
            Returns true if the asset path is a file (will be assuming from the index that it is a packed type)
            Returns false if the asset path is a folder (legacy/non-packed mods)
        """
        return os.path.isfile(path)

    def read(self, key, path, image=False):
        if self.is_packed_file(path):
            key = key.lower()
            db = starbound.open_file(path)

            # try the cache first
            if image and key in self.image_cache:
                return self.image_cache[key]

            try:
                data = db.get(key)
            except KeyError:
                if image and path != self.vanilla_assets:
                    img = self.read(key, self.vanilla_assets, image)
                    self.image_cache[key] = img
                    return img
                else:
                    logging.exception("Unable to read db asset '%s' from '%s'" % (key, path))
                    return None
            if image:
                img = data
                self.image_cache[key] = img
                return img
            else:
                try:
                    asset = parse_json(data.decode("utf-8"), key)
                    return asset
                except ValueError:
                    logging.exception("Unable to read db asset '%s' from '%s'" % (key, path))
                    return None
        else:
            asset_file = os.path.join(path, key[1:])
            try:
                if image:
                    img = open(asset_file, "rb").read()
                    self.image_cache[key] = img
                    return img
                else:
                    asset = load_asset_file(asset_file)
                    return asset
            except (FileNotFoundError, ValueError):
                if image and path != self.vanilla_assets:
                    if self.is_packed_file(self.vanilla_assets):
                        img = self.read(key.replace("\\", "/"), self.vanilla_assets, image)
                        self.image_cache[key] = img
                        return img
                    else:
                        img = self.read(key, self.vanilla_assets, image)
                        self.image_cache[key] = img
                        return img
                else:
                    logging.exception("Unable to read asset file '%s' from '%s'" % (key, path))
                    return None

    def blueprints(self):
        return Blueprints(self)

    def items(self):
        return Items(self)

    def species(self):
        return Species(self)

    def player(self):
        return Player(self)

    def monsters(self):
        return Monsters(self)

    def techs(self):
        return Techs(self)

    def images(self):
        return Images(self)

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

    def missing_icon(self):
        return self.read("/interface/inventory/x.png", self.vanilla_assets, image=True)

    def get_mods(self):
        """Return a list of all unique mod paths."""
        c = self.db.cursor()
        c.execute("select distinct path from assets order by category")
        all_assets = [x[0].replace(self.starbound_folder,"") for x in c.fetchall()]
        return [x for x in all_assets if not x.endswith("packed.pak")]

class Images():
    def __init__(self, assets):
        """For loading and searching image assets."""
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

    def filter_images(self, name):
        """Find image assets from their filename/asset key."""
        q = "select key, path from assets where type = 'image' and key like ?"
        c = self.assets.db.cursor()
        name = "%"+name+"%"
        c.execute(q, (name,))
        return c.fetchall()

    def get_image(self, name):
        """Find an image asset from its key, return PIL Image."""
        # only care about the first hit
        asset = self.filter_images(name)[0]
        data = self.assets.read(asset[0], asset[1], True)
        return Image.open(BytesIO(data)).convert("RGBA")

    def color_image(self, image, item_data):
        data_keys = item_data.keys()
        new_image = image

        def get_replace(img_str):
            match = re.search("\?replace.+", img_str)
            if match is not None:
                return match.group()
            else:
                return None

        def do_replace(item_key, new_image):
            if type(item_key) is not str:
                return new_image

            replace = get_replace(item_key)
            if replace is not None:
                replace = unpack_color_directives(replace)
                new_image = replace_colors(new_image, replace)
            return new_image

        if "directives" in data_keys:
            replace = unpack_color_directives(item_data["directives"])
            new_image = replace_colors(new_image, replace)
        elif "colorOptions" in data_keys:
            pass
        elif "image" in data_keys:
            new_image = do_replace(item_data["image"], new_image)
        elif "largeImage" in data_keys:
            new_image = do_replace(item_data["largeImage"], new_image)
        elif "inventoryIcon" in data_keys:
            new_image = do_replace(item_data["inventoryIcon"], new_image)
        elif "materialHueShift" in data_keys:
            pass
        elif "drawables" in data_keys:
            pass

        return new_image


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

        if asset_data is None: return

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

    def get_blueprint(self, name):
        c = self.assets.db.cursor()
        c.execute("select key, path, desc from assets where type = 'blueprint' and name = ?", (name,))
        meta = c.fetchone()
        if meta is not None:
            blueprint = self.assets.read(meta[0], meta[1])
            return blueprint, meta[0], meta[1], meta[2]
        else:
            return None

class Items():
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

    def is_item(self, key):
        if key.endswith(".object"):
            return True
        elif key.endswith(".techitem"):
            return True
        elif key.endswith(".codexitem"):
            return True
        elif key.startswith("items", 1) and re.match(ignore_items, key) is None:
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        asset_type = "item"
        category = asset_category(key)
        asset_data = self.assets.read(key, path)

        if asset_data is None: return

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
            logging.warning("Skipping invalid item asset (no name set) %s in %s" % (key, path))
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

    def get_item_index(self, name):
        """Return raw item index entry."""
        c = self.assets.db.cursor()
        c.execute("select * from assets where type = 'item' and name = ?", (name,))
        return c.fetchone()

    def get_item(self, name):
        """
        Find the first hit in the DB for a given item name, return the
        parsed asset file and location.
        """
        logging.debug("Lookup item: " + name)
        c = self.assets.db.cursor()
        c.execute("select key, path, desc from assets where type = 'item' and name = ?", (name,))
        meta = c.fetchone()
        if meta is not None:
            item = self.assets.read(meta[0], meta[1])
            return item, meta[0], meta[1], meta[2]
        else:
            return None

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

        if icon[0][0] != "/":
            icon[0] = os.path.dirname(item[1]) + "/" + icon[0]

        icon_data = self.assets.read(icon[0], item[2], image=True)
        if icon_data is None:
            return None

        item_icon = Image.open(BytesIO(icon_data))
        orig_size = item_icon.size

        icon_type = str(icon[1])
        if icon_type.startswith("chest"):
            item_icon = item_icon.crop((16, 0, 16+16, 16))
            size = (16, 16)
        elif icon_type.startswith("pants"):
            item_icon = item_icon.crop((32, 0, 32+16, 16))
            size = (16, 16)
        elif icon_type.startswith("back"):
            item_icon = item_icon.crop((48, 0, 48+16, 16))
            size = (16, 16)
        elif icon_type.startswith("head"):
            item_icon = item_icon.crop((0, 0, 16, 16))
            size = (16, 16)
        else:
            size = orig_size

        inv_icon = Image.new("RGBA", size)
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
        elif name == "sapling":
            return Image.open(BytesIO(self.sapling_icon())).convert("RGBA")

        try:
            item = self.get_item(name)
            icon_file = item[0]["image"]
            icon = icon_file.split(':')
            icon = icon[0]
        except (KeyError, TypeError):
            logging.warning("No image key for "+name)
            return None

        if icon[0] != "/":
            icon = os.path.dirname(item[1]) + "/" + icon

        icon_data = self.assets.read(icon, item[2], image=True)

        if icon_data is None:
            logging.warning("Unable to read %s from %s" % (icon, item[2]))
            return None

        item_image = Image.open(BytesIO(icon_data)).convert("RGBA")

        return item_image

    def missing_icon(self):
        """Return the image data for the default inventory placeholder icon."""
        return self.assets.read("/interface/inventory/x.png",
                                self.assets.vanilla_assets, image=True)

    def sword_icon(self):
        return self.assets.read("/interface/inventory/sword.png",
                                self.assets.vanilla_assets, image=True)

    def shield_icon(self):
        return self.assets.read("/interface/inventory/shield.png",
                                self.assets.vanilla_assets, image=True)

    def sapling_icon(self):
        return self.assets.read("/objects/generic/sapling/saplingicon.png",
                                self.assets.vanilla_assets,
                                image=True)

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

        # if "firePosition" in item[0]:
        #     generated_gun["firePosition"] = [float(item[0]["firePosition"][0]),
        #                                      float(item[0]["firePosition"][1])]

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

        if "projectileTypes" in item[0]["primaryStances"]:
            generated_sword["primaryStances"]["projectileType"] = item[0]["primaryStances"]["projectileTypes"][0]
            generated_sword["primaryStances"]["projectile"]["level"] = 1.0
            generated_sword["primaryStances"]["projectile"]["power"] = 5.0

        if "altStances" in item[0]:
            generated_sword["altStances"] = item[0]["altStances"]
            if "projectileTypes" in item[0]["altStances"]:
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
            "recoilTime": 0.2,
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

        # if "kind" in item[0]:
        #     generated_shield["inspectionKind"] = item[0]["kind"]

        if "shortdescription" in item[0]:
            generated_shield["shortdescription"] = item[0]["shortdescription"]

        if "rarity" in item[0]:
            generated_shield["rarity"] = item[0]["rarity"]

        if "hitSound" in item[0]:
            generated_shield["hitSound"] = item[0]["hitSound"]

        if "recoil" in item[0]["baseline"]:
            generated_shield["recoilTime"] = item[0]["baseline"]["recoil"]

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

    def generate_sapling(self, item):
        sapling = {
            "foliageHueShift": -0.0,
            "foliageName": "brains",
            "stemHueShift": -0.0,
            "stemName": "metal"
        }

        return sapling

    def generate_filledcapturepod(self, item, player_uuid):
        filledcapturepod = {
            "projectileConfig": {
                "actionOnReap": [
                    {
                        "action": "spawnmonster",
                        "arguments": {
                            "aggressive": True,
                            "damageTeam": 0,
                            "damageTeamType": "friendly",
                            "familyIndex": 0,
                            "killCount": None,
                            "level": 1.0,
                            "ownerUuid": player_uuid,
                            "persistent": True,
                            "seed": self.assets.monsters().monster_seed()
                        },
                        "offset": [0,2],
                        "type": self.assets.monsters().random_monster()
                    }
                ],
                "level": 7,
                "speed": 70
            }
        }

        return filledcapturepod


class Species():
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder
        self.humanoid_config = self.assets.read("/humanoid.config",
                                                self.assets.vanilla_assets)

    def is_species(self, key):
        if key.endswith(".species"):
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        asset_data = self.assets.read(key, path)

        if asset_data is None:
            return

        if "kind" in asset_data:
            return (key, path, "species", "", asset_data["kind"].lower(), "")
        else:
            logging.warning("Species missing kind key: %s in %s" % (key, path))

    def get_species_list(self):
        """Return a formatted list of all species."""
        c = self.assets.db.cursor()
        c.execute("select distinct name from assets where type = 'species' order by name")

        names = [x[0] for x in c.fetchall()]
        formatted = []

        for s in names:
            if s == "dummy":
                continue

            try:
                formatted.append(s[0].upper() + s[1:])
            except IndexError:
                formatted.append(s)
                logging.exception("Unable to format species: %s", s)

        return formatted

    def get_species(self, name):
        """Look up a species from the index and return contents of species
        files."""
        c = self.assets.db.cursor()
        c.execute("select * from assets where type = 'species' and name = ?",
                  (name.lower(),))
        species = c.fetchone()
        if species is None:
            # species is not indexed
            logging.warning("Unable to load species: %s", name)
            return None
        species_data = self.assets.read(species[0], species[1])
        if species_data is None:
            # corrupt save, no race set
            logging.warning("No race set on player")
            return None
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
            if key in species_data.keys() and species_data[key] is not None:
                default = read_default_color(species_data[key])
                if default == []:
                    return ""
                else:
                    replace = make_color_directives([default])
                    return replace
            else:
                return ""

        colors = {
            "bodyColor": val("bodyColor"),
            "undyColor": val("undyColor"),
            "hairColor": val("hairColor")
        }
        # TODO: there is an unbelievably complicated method for choosing
        # default player colors. i'm not sure if it's worth going into too much
        # considering it will only be used if a player switches species
        # it might be easier to just leave this out entirely. let user
        # add/remove their own directive colors
        directives = {
            "body": [colors["bodyColor"]],
            "emote": [colors["bodyColor"], colors["undyColor"]],
            "hair": [colors["hairColor"]],
            "facial_hair": [colors["bodyColor"]],
            "facial_mask": [colors["bodyColor"]]
        }
        return directives

    def get_preview_image(self, name, gender):
        """Return raw image data for species placeholder pic.

        I don't think this is actually used anywhere in game. Some mods don't
        include it."""

        species = self.get_species(name.lower())
        try:
            try:
                key = self.get_gender_data(species, gender)["characterImage"]
            except TypeError:
                return None
            return self.assets.read(key, species[0][1], image=True)
        except FileNotFoundError:
            # corrupt save, no race set
            logging.warning("No race set on player")
            return None

    def render_player(self, player):
        """Return an Image of a fully rendered player from a save."""

        name = player.get_race()
        gender = player.get_gender()
        asset_loc = self.get_species(name)[0][1]

        # crop the spritesheets and replace colours
        def grab_sprite(sheet_path, rect, directives):
            sheet = self.assets.read(sheet_path, asset_loc, True)
            img = Image.open(BytesIO(sheet)).convert("RGBA").crop(rect)
            if directives != "":
                img = replace_colors(img, unpack_color_directives(directives))
            return img

        default_rect = (43, 0, 86, 43)
        # TODO: should use the .bbox to figure this out
        personality = player.get_personality()
        personality_offset = int(re.search("\d$", personality).group(0)) * 43
        body_rect = (personality_offset, 0, personality_offset+43, 43)

        body_img = grab_sprite("/humanoid/%s/%sbody.png" % (name, gender),
                               body_rect,
                               player.get_body_directives())
        frontarm_img = grab_sprite("/humanoid/%s/frontarm.png" % name,
                                   body_rect,
                                   player.get_body_directives())
        backarm_img = grab_sprite("/humanoid/%s/backarm.png" % name,
                                  body_rect,
                                  player.get_body_directives())
        head_img = grab_sprite("/humanoid/%s/%shead.png" % (name, gender),
                               default_rect,
                               player.get_body_directives())

        hair = player.get_hair()
        hair_img = None
        if hair[0] != "":
            hair_img = self.get_hair_image(
                name, hair[0],
                hair[1], gender,
                player.get_hair_directives()
            )

        facial_hair = player.get_facial_hair()
        facial_hair_img = None
        if facial_hair[0] != "":
            facial_hair_img = self.get_hair_image(
                name, facial_hair[0],
                facial_hair[1], gender,
                player.get_facial_hair_directives()
            )

        facial_mask = player.get_facial_mask()
        facial_mask_img = None
        if facial_mask[0] != "":
            facial_mask_img = self.get_hair_image(
                name, facial_mask[0],
                facial_mask[1], gender,
                player.get_facial_mask_directives()
            )

        # new blank canvas!
        base_size = 43
        base = Image.new("RGBA", (base_size, base_size))

        # the order of these is important!

        # back arm first
        base.paste(backarm_img)
        # then the head
        base.paste(head_img, mask=head_img)

        # hair if set
        if hair_img is not None:
            try:
                base.paste(hair_img, mask=hair_img)
            except ValueError:
                logging.exception("Bad hair image: %s, %s", hair[0], hair[1])

        # body
        base.paste(body_img, mask=body_img)
        base.paste(frontarm_img, mask=frontarm_img)

        # facial mask if set
        if facial_mask_img is not None:
            try:
                base.paste(facial_mask_img, mask=facial_mask_img)
            except ValueError:
                logging.exception("Bad facial mask image: %s, %s",
                                  facial_mask[0], facial_mask[1])

        # facial hair if set
        if facial_hair_img is not None:
            try:
                base.paste(facial_hair_img, mask=facial_hair_img)
            except ValueError:
                logging.exception("Bad facial hair image: %s, %s",
                                  facial_hair[0], facial_hair[1])

        return base.resize((base_size*3, base_size*3))

    def get_hair_image(self, name, hair_type, hair_group, gender, directives):
        # TODO: bbox is from .frame file, need a way to read them still
        species = self.get_species(name.lower())
        image_path = "/humanoid/%s/%s/%s.png" % (name, hair_type, hair_group)

        try:
            image = self.assets.read(image_path, species[0][1], image=True)
            image = Image.open(BytesIO(image)).convert("RGBA").crop((43, 0,
                                                                     86, 43))
            return replace_colors(image, unpack_color_directives(directives))
        except OSError:
            logging.exception("Missing hair image: %s", image_path)
            return

    def generate_name(self, species_name):
        # now sure how this format is intended to work, but files are consistent
        # enough to cheat like this. may break in the future
        species = self.get_species(species_name.lower())
        namegen_config_path = "/species/" + species[1]["kind"] + "namegen.config"
        namegen_config = self.assets.read(namegen_config_path,
                                          species[0][1])
        final_name = ""
        names = namegen_config["names"][1][1:]
        for group in names:
            random_name = random.choice(group[1:])
            final_name += random_name
        return final_name


class Player():
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
            name = slot["__content"]["name"]
            item = self.assets.items().get_item_index(name)
            if item is not None:
                return item[3]
            else:
                return ""

        sort_map = {
            "name": lambda x: x["__content"]["name"],
            "count": lambda x: x["__content"]["count"],
            "category": get_category
        }

        filtered = [x for x in bag if x is not None]
        sorted_bag = sorted(filtered, key=sort_map[sort_by])
        # TODO: only handles main/tile bags atm
        sorted_bag += [None] * (40 - len(sorted_bag))

        return sorted_bag


class Monsters():
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


class Techs():
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

    def is_tech(self, key):
        if key.endswith(".tech"):
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        name = os.path.basename(asset[0]).split(".")[0]
        asset_data = self.assets.read(key, path)

        if asset_data is None:
            return

        return (key, path, "tech", "", name, "")

    def all(self):
        """Return a list of all techs."""
        c = self.assets.db.cursor()
        c.execute("select name from assets where type = 'tech' order by name")
        return [x[0] for x in c.fetchall()]

    def get_tech(self, name):
        q = "select key, path from assets where type = 'tech' and name = ?"
        c = self.assets.db.cursor()
        c.execute(q, (name,))

        tech = c.fetchone()
        if tech is None:
            return

        asset = self.assets.read(tech[0], tech[1])
        info = self.assets.read(tech[0]+"item", tech[1])
        icon = self.assets.read(info["inventoryIcon"], tech[1], image=True)

        if icon is None:
            icon = self.assets.items().missing_icon()

        return info, Image.open(BytesIO(icon)).convert("RGBA"), tech[0], asset

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
