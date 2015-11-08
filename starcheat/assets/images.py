import re

from io import BytesIO
from PIL import Image

from assets.common import replace_colors
from assets.common import unpack_color_directives


class Images(object):
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
        try:
            asset = self.filter_images(name)[0]
        except IndexError:
            return
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
