import logging
import os
import re

from io import BytesIO
from PIL import Image

from assets.common import replace_colors
from assets.common import unpack_color_directives
from assets.common import make_color_directives


def read_default_color(species_data):
    color = []
    if type(species_data[0]) is str:
        return []
    for group in species_data[0].keys():
        color.append([group, species_data[0][group]])
    return color


class Species(object):
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
        return self.humanoid_config["personalities"]

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

    def render_part(self, player, player_image, part, slot):
        """Lookup, crop and color given item slot and apply to player render."""
        gender = player.get_gender()
        stance = player.get_personality()

        if part == "head":
            frame_key = "head", "normal"
        elif part == "legs":
            frame_key = "pants"+gender[0], stance
        elif part == "back":
            frame_key = "back", stance

        frame = self.assets.frames().lookup_frame(*frame_key)

        if slot is None:
            return player_image

        item = self.assets.items().get_item(slot["name"])

        if (item is None or
                not gender + "Frames" in item[0]):
            return player_image

        item_img_path = item[0][gender + "Frames"]

        if item_img_path[0] != "/":
            item_img_path = os.path.dirname(item[1]) + "/" + item_img_path

        item_img = self.assets.images().get_image(item_img_path)
        if item_img is None:
            return player_image

        item_img = item_img.crop(frame)
        item_img = self.assets.images().color_image(item_img, slot["parameters"])

        player_image.paste(item_img, mask=item_img)

        return player_image

    def render_chest(self, player, player_image, slot, part):
        """Lookup, crop and color given chest slot and apply to player render."""
        gender = player.get_gender()
        stance = player.get_personality()

        if slot is None:
            return player_image

        item = self.assets.items().get_item(slot["name"])

        if (item is None or not (gender + "Frames") in item[0]):
            return player_image

        frame_paths = item[0][gender + "Frames"]
        for k, v in frame_paths.items():
            if v[0] != "/":
                frame_paths[k] = os.path.dirname(item[1]) + "/" + v

        files = ["fsleeve", "chestm", "bsleeve"]
        if gender == "female":
            files = ["fsleevef", "chestf", "bsleevef"]

        color = lambda x: self.assets.images().color_image(x, slot["parameters"])
        if part == "fsleeve":
            fsleeve = self.assets.images().get_image(frame_paths["frontSleeve"])
            if fsleeve is None:
                return player_image
            fsleeve_frame = self.assets.frames().lookup_frame(files[0], stance)
            fsleeve = fsleeve.crop(fsleeve_frame)
            fsleeve = color(fsleeve)
            player_image.paste(fsleeve, mask=fsleeve)
        elif part == "bsleeve":
            bsleeve = self.assets.images().get_image(frame_paths["backSleeve"])
            if bsleeve is None:
                return player_image
            bsleeve_frame = self.assets.frames().lookup_frame(files[2], stance)
            bsleeve = bsleeve.crop(bsleeve_frame)
            bsleeve = color(bsleeve)
            player_image.paste(bsleeve, mask=bsleeve)
        elif part == "body":
            body = self.assets.images().get_image(frame_paths["body"])
            if body is None:
                return player_image
            body_frame = self.assets.frames().lookup_frame(files[1], stance)
            body = body.crop(body_frame)
            body = color(body)
            player_image.paste(body, mask=body)

        return player_image

    def render_player(self, player, armor=True):
        """Return an Image of a fully rendered player from a save."""
        name = player.get_race()
        gender = player.get_gender()
        species = self.get_species(name.lower())

        if species is None:
            return Image.open(BytesIO(self.assets.items().missing_icon()))

        asset_loc = species[0][1]

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

        head_slot = player.get_visible("head")
        chest_slot = player.get_visible("chest")
        legs_slot = player.get_visible("legs")
        back_slot = player.get_visible("back")
        do_head = armor and head_slot is not None

        # new blank canvas!
        base_size = 43
        base = Image.new("RGBA", (base_size, base_size))

        # the order of these is important!

        # back arm
        base.paste(backarm_img)
        if armor and chest_slot is not None:
            base = self.render_chest(player, base, chest_slot, "bsleeve")

        # backpack
        if armor and back_slot is not None:
            base = self.render_part(player, base, "back", back_slot)

        # then the head
        base.paste(head_img, mask=head_img)

        # TODO: support mask on head items
        if hair_img is not None:
            try:
                base.paste(hair_img, mask=hair_img)
            except ValueError:
                logging.exception("Bad hair image: %s, %s", hair[0], hair[1])

        # body
        base.paste(body_img, mask=body_img)
        if armor and legs_slot is not None:
            base = self.render_part(player, base, "legs", legs_slot)
        if armor and chest_slot is not None:
            base = self.render_chest(player, base, chest_slot, "body")

        # front arm
        base.paste(frontarm_img, mask=frontarm_img)
        if armor and chest_slot is not None:
            base = self.render_chest(player, base, chest_slot, "fsleeve")

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

        if do_head:
            base = self.render_part(player, base, "head", head_slot)

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
