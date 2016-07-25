import re
import os
import logging
import random

from io import BytesIO
from PIL import Image
from PIL import ImageChops

from assets.common import asset_category


ignore_items = re.compile(".*\.(png|config|frames|lua)", re.IGNORECASE)


def trim(im):
    """Trim whitespace from image."""
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def trim_and_square(icon):
    """Trim whitespace and pad icon to be square."""
    icon = trim(icon)

    if icon is None:
        return

    larger = icon.size[0]

    if icon.size[1] > larger:
        larger = icon.size[1]

    new_icon = Image.new("RGBA", (larger, larger))

    try:
        new_icon.paste(icon, icon.getbbox())
    except ValueError:
        return icon

    return new_icon


class Items(object):
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
        offset = asset[2]
        length = asset[3]
        asset_type = "item"
        category = asset_category(key)
        asset_data = self.assets.read(key, path, False, offset, length)
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
            return (key, path, offset, length, asset_type, category, name, desc)

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

        if icon is None:
            return
        else:
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
            return Image.open(BytesIO(self.gun_icon())).convert("RGBA")
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

    def gun_icon(self):
        return self.assets.read("/interface/inventory/gun.png",
                                self.assets.vanilla_assets, image=True)

    def shield_icon(self):
        return self.assets.read("/interface/inventory/shield.png",
                                self.assets.vanilla_assets, image=True)

    def sapling_icon(self):
        return self.assets.read("/objects/generic/sapling/saplingicon.png",
                                self.assets.vanilla_assets,
                                image=True)

    def generate_gun(self, item):
        d = item[0]

        # seems to be a newish key
        if "directories" in d and len(d["directories"]) > 0:
            image_folder = d["directories"][0]
        else:
            image_folder = d["name"].replace(d["rarity"].lower(), "")
            image_folder = image_folder.replace("plasma", "")
            image_folder = "/items/guns/randomgenerated/" + image_folder + "/"

        butts = self.assets.images().filter_images(image_folder + "butt/")
        middles = self.assets.images().filter_images(image_folder + "middle/")
        barrels = self.assets.images().filter_images(image_folder + "barrel/")

        if len(butts) > 0:
            butt = random.choice(butts)[0]
            butt_width = self.assets.images().get_image(butt).size[0]
        else:
            butt = ""
            butt_width = 0.0

        if len(middles) > 0:
            middle = random.choice(middles)[0]
            middle_width = self.assets.images().get_image(middle).size[0]
        else:
            middle = ""
            middle_width = 0.0

        if len(barrels) > 0:
            barrel = random.choice(barrels)[0]
        else:
            barrel = ""

        gun = {
            "itemName": "generatedgun",
            "generated": True,
            "maxStack": 1,
            "tooltipKind": "gun",
            "level": 1.0,
            "levelScale": 1.0,
            "projectile": {"level": 1.0, "power": 1.0},
            "projectileCount": random.randint(1, 10),
            "projectileSeparation": random.uniform(0.0, 1.0),
            "drawables": [  # TODO: palettes, some inv icons offset wrong
                {"image": butt, "position": [-(float(butt_width)), 0.0]},
                {"image": middle, "position": [0.0, 0.0]},
                {"image": barrel, "position": [float(middle_width), 0.0]}
            ]
        }

        gun["inventoryIcon"] = gun["drawables"]

        # this is made up, dunno how it really figures it
        if "rateOfFire" in d and len(d["rateOfFire"]) == 2:
            gun["fireTime"] = random.uniform(d["rateOfFire"][0] / 5,
                                             d["rateOfFire"][1] / 5)

        if "multiplier" in d:
            gun["multiplier"] = d["multiplier"]
            gun["classMultiplier"] = d["multiplier"]

        if "handPosition" in d and len(d["handPosition"]) == 2:
            gun["handPosition"] = [-d["handPosition"][0],
                                   -d["handPosition"][1]]

        if ("muzzleFlashes" in d and len(d["muzzleFlashes"]) > 0 and
                "fireSound" in d and len(d["fireSound"]) > 0):
            gun["muzzleEffect"] = {
                "animation": random.choice(d["muzzleFlashes"]),
                "fireSound": [{"file": random.choice(d["fireSound"])}]
            }

        if ("projectileTypes" in d and len(d["projectileTypes"]) > 0):
            gun["projectileType"] = random.choice(d["projectileTypes"])

        if "weaponType" in d:
            gun["shortdescription"] = "Cheater's " + d["weaponType"]

        if "hands" in d and len(d["hands"]) > 0 and d["hands"][0] == 2:
            gun["twoHanded"] = True
        else:
            gun["twoHanded"] = False

        def copy_key(name):
            if name in d:
                gun[name] = d[name]

        copy_key("baseDps")
        copy_key("directories")
        copy_key("firePosition")  # TODO: not correct
        copy_key("fireSound")
        copy_key("hands")
        copy_key("inaccuracy")
        copy_key("muzzleFlashes")
        copy_key("name")
        copy_key("nameGenerator")
        copy_key("palette")
        copy_key("projectileTypes")
        copy_key("rarity")
        copy_key("rateOfFire")
        copy_key("recoilTime")
        copy_key("weaponType")

        return gun

    def generate_sword(self, item):
        d = item[0]

        if "rarity" in d:
            image_folder = d["name"].replace(d["rarity"].lower(), "")
        else:
            image_folder = d["name"]
        image_folder = re.sub("(uncommon|common|crappy|new)", "", image_folder)
        image_folder = "/items/swords/randomgenerated/" + image_folder

        handles = self.assets.images().filter_images(image_folder + "/handle/")
        blades = self.assets.images().filter_images(image_folder + "/blade/")

        if len(handles) > 0:
            handle = random.choice(handles)[0]
        else:
            handle = ""

        if len(blades) > 0:
            blade = random.choice(blades)[0]
        else:
            blade = ""

        sword = {
            "generated": True,
            "itemName": "generatedsword",
            "tooltipKind": "sword",
            "parrySound": "",
            "level": 1,
            # TODO: palette
            "drawables": [{"image": handle},
                          {"image": blade}]
        }

        sword["inventoryIcon"] = sword["drawables"]

        ps = "primaryStances"
        if ps in d:
            sword[ps] = d[ps]
            sword[ps]["projectile"] = {
                "level": 1.0,
                "power": 1.0
            }
            if ("projectileTypes" in d[ps] and
                    len(d[ps]["projectileTypes"]) > 0):
                sword[ps]["projectileType"] = random.choice(d[ps]["projectileTypes"])

        als = "altStances"
        if als in d:
            sword[als] = d[als]
            sword[als]["projectile"] = sword[ps]["projectile"]
            if ("projectileTypes" in d[als] and
                    len(d[als]["projectileTypes"] > 0)):
                sword[als]["projectileType"] = random.choice(d[als]["projectileTypes"])
        else:
            sword[als] = sword[ps]

        if "rateOfSwing" in d and len(d["rateOfSwing"]) == 2:
            sword["fireTime"] = random.uniform(d["rateOfSwing"][0],
                                               d["rateOfSwing"][1])

        if "rarity" in d:
            sword["rarity"] = d["rarity"]
        else:
            sword["rarity"] = "common"

        if "weaponType" in d:
            sword["shortdescription"] = "Cheater's " + d["weaponType"]

        if "soundEffect" in d and len(d["soundEffect"]) > 0:
            sword["soundEffect"] = {
                "fireSound": [{"file": random.choice(d["soundEffect"])}]
            }

        def copy_key(name):
            if name in d:
                sword[name] = d[name]

        copy_key("fireAfterWindup")
        copy_key("firePosition")
        copy_key("weaponType")

        return sword

    def generate_shield(self, item):
        d = item[0]

        if "kind" in d:
            image_path = "%s/%s/images" % (os.path.dirname(item[1]),
                                           d["kind"])
            images = self.assets.images().filter_images(image_path)
            if len(images) > 0:
                image = random.choice(images)[0]
            else:
                image = ""
        else:
            image = ""

        shield = {
            "generated": True,
            "itemName": "generatedshield",
            "maxStack": 1,
            "tooltipKind": "shield",
            "level": 1.0,
            "levelScale": 1.0,
            "healthStuckAtZeroTime": 5.0,
            "perfectBlockTime": 0.15,
            "shieldSuppressedAfterDamageTime": 0.15,
            "drawables": [{"image": image}],
            "inventoryIcon": [{"image": image + ":icon"}]
        }

        if "rarity" in d:
            shield["rarity"] = d["rarity"]
        else:
            shield["rarity"] = "common"

        if "kind" in d:
            shield["shortdescription"] = "Cheater's " + d["kind"] + " Shield"

        def copy_key(name):
            if name in d:
                shield[name] = d[name]

        def copy_base(name):
            if name in d["baseline"]:
                shield[name] = d["baseline"][name]

        copy_key("breakParticle")
        copy_key("breakSound")
        copy_key("health")
        copy_key("healthRegen")
        copy_key("hitSound")
        copy_key("perfectBlockParticle")
        copy_key("perfectHitSound")
        copy_base("damagePoly")
        copy_base("knockbackDamageKind")
        copy_base("knockbackPower")
        copy_base("recoilTime")
        copy_base("shieldPoly")
        copy_base("statusEffects")

        return shield

    def generate_sapling(self, item):
        sapling = {
            # TODO: pick random for all
            "foliageHueShift": -0.0,
            "foliageName": "brains",
            "stemHueShift": -0.0,
            "stemName": "metal"
        }

        return sapling

    def generate_filledcapturepod(self, item, player_uuid):
        filledcapturepod = {
            "actionOnReap": [{
                "action": "spawnmonster",
                "arguments": {
                    "aggressive": True,
                    "damageTeam": 0,
                    "damageTeamType": "friendly",
                    "familyIndex": 0,
                    "killCount": None,
                    "level": 1,
                    "ownerUuid": player_uuid,
                    "persistent": True,
                    "seed": self.assets.monsters().monster_seed()
                },
                "level": 1,
                "offset": [0, 2],
                "type": self.assets.monsters().random_monster()
            }],
            "level": 7,
            "speed": 40
        }

        return filledcapturepod
