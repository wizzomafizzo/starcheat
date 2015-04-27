import re
import os
import logging

from io import BytesIO
from PIL import Image
from PIL import ImageChops

from assets.common import asset_category


ignore_items = re.compile(".*\.(png|config|frames|lua)", re.IGNORECASE)


def trim(im):
    """Trim whitespace from image."""
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def trim_and_square(icon):
    """Trim whitespace and pad icon to be square."""
    icon = trim(icon)
    larger = icon.size[0]
    if icon.size[1] > larger:
        larger = icon.size[1]
    new_icon = Image.new("RGBA", (larger, larger))
    try:
        new_icon.paste(icon, icon.getbbox())
    except ValueError:
        return icon
    return new_icon


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

        if asset_data is None:
            return
        if type(asset_data) is list:
            logging.debug("Skipping mod patch file %s in %s" % (key, path))
            return

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

        item = self.get_item(name)
        if item is None or "inventoryIcon" not in item[0]:
            return

        icon_file = item[0]["inventoryIcon"]
        icon_name = icon_file.split(':')
        if len(icon_name) < 2:
            icon_name = [icon_name[0], 0]

        if icon_name[0][0] != "/":
            icon_name[0] = os.path.dirname(item[1]) + "/" + icon_name[0]

        icon_data = self.assets.read(icon_name[0], item[2], image=True)
        if icon_data is None:
            return None

        icon = Image.open(BytesIO(icon_data))

        icon_type = str(icon_name[1])
        if icon_type.startswith("chest"):
            icon = icon.crop((16, 0, 16+16, 16))
        elif icon_type.startswith("pants"):
            icon = icon.crop((32, 0, 32+16, 16))
        elif icon_type.startswith("back"):
            icon = icon.crop((48, 0, 48+16, 16))
        elif icon_type.startswith("head"):
            icon = icon.crop((0, 0, 16, 16))

        if icon.size[0] != icon.size[1]:
            icon = trim_and_square(icon)

        return icon.convert("RGBA")

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

        item = self.get_item(name)
        if item is None or "image" not in item[0]:
            return

        icon_file = item[0]["image"]
        icon = icon_file.split(':')
        icon = icon[0]

        if icon[0] != "/":
            icon = os.path.dirname(item[1]) + "/" + icon

        icon_data = self.assets.read(icon, item[2], image=True)

        if icon_data is None:
            logging.warning("Unable to read %s from %s" % (icon, item[2]))
            return

        icon = Image.open(BytesIO(icon_data)).convert("RGBA")

        if icon.size[0] != icon.size[1]:
            icon = trim_and_square(icon)

        return icon

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
