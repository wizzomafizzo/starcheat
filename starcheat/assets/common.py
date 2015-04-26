import os
import re

# available colors for text
colors = ["Red", "Orange", "Yellow", "Green", "Blue",
          "Black", "White", "Magenta", "DarkMagenta",
          "Gray", "LightGray", "DarkGray", "DarkGreen",
          "Pink", "Clear"]

replace_directive_re = re.compile(
    "(?:\?replace((?:;[a-fA-F0-9]{1,6}=[a-fA-F0-9]{1,6}){1,}))"
)


def string_color(name):
    if name in colors:
        return "^" + name + ";"
    else:
        return ""


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


def unpack_color_directives(data):
    if data is None:
        return {}
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
                groups.append((rgbkey, rgbval))
    return dict(groups)


def replace_colors(image, dict_colors):
    pixel_data = image.load()

    result_img = image.copy()
    result_pixel_data = result_img.load()
    for (key, value) in dict_colors.items():
        for y in range(result_img.size[1]):
            for x in range(result_img.size[0]):
                pixel = pixel_data[x, y]
                if pixel[0] == key[0] and pixel[1] == key[1] and pixel[2] == key[2]:
                    if result_img.mode == "RGBA":
                        result_pixel_data[x, y] = (value + (pixel[3],))
                    elif result_img.mode == "RGB":
                        result_pixel_data[x, y] = value
    return result_img
