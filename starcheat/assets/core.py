"""
Module for reading and indexing Starbound assets
"""

import os
import json
import re
import sqlite3
import logging

import starbound
import starbound.btreedb4

from assets.blueprints import Blueprints
from assets.items import Items
from assets.species import Species
from assets.player import Player
from assets.monsters import Monsters
from assets.techs import Techs
from assets.images import Images
from assets.frames import Frames
from assets.common import asset_category


# Regular expression for comments
comment_re = re.compile(
    '("(\\[\s\S]|[^"])*")|((^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?)',
    re.DOTALL | re.MULTILINE
)

ignore_assets = re.compile(".*\.(db|ds_store|ini|psd|patch)", re.IGNORECASE)


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


class Assets(object):
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
        frames = Frames(self)

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
                elif frames.is_frames(asset[0]):
                    tmp_data = frames.index_data(asset)
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

    def frames(self):
        return Frames(self)

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
        all_assets = [x[0].replace(self.starbound_folder, "") for x in c.fetchall()]
        return [x for x in all_assets if not x.endswith("packed.pak")]


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
