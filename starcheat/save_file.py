"""
Import/export Starbound .player save files

This module allows you to import a Starbound .player save file as a dictionary,
edit it how you like and then export it again.

It can also be run from the command line to dump the contents, like this:
$ python ./save_file.py <.player file>
"""

import sys, logging, struct
from pprint import pprint
from struct import pack, unpack_from

# compatible save version
data_version = "SBVJ01"
# this is the complete data format definition for a .player file. formats
# surrounded by double underscores are special types with unpack/repack
# functions defined later in the file. everything else is standard formats for
# the python struct module. the offsets define how many bytes an attribute is
# with None types meaning they're variable length
# and this is extremely helpful: https://github.com/McSimp/starbound-research
# (name, format, offset)
data_format = (
    ("header", "6c", 6),
    ("save", "__starsave__", None),
    ("the_rest", "__the_rest__", None)
)

def unpack_str(bytes):
    """Convert a list of bytes to a string."""
    return "".join(map(chr,map(ord,bytes)))

def pack_str(var):
    """Convert a string to a list of bytes."""
    return str(var).encode("utf-8")

# source: http://stackoverflow.com/questions/6776553/python-equivalent-of-perls-w-packing-format
def unpack_vlq(data):
    """Return the first VLQ number and byte offset from a list of bytes."""
    logging.debug("Unpacking VLQ")
    offset = 0
    value = 0
    while True:
        tmp = data[offset]
        value = (value<<7) | (tmp&0x7f)
        offset += 1
        if tmp & 0x80 == 0:
            break
    return value, offset

# source: https://github.com/metachris/binary-serializer/blob/master/python/bincalc.py
def pack_vlq(n):
    """Convert an integer to a VLQ and return a list of bytes."""
    logging.debug("Packing VLQ")
    value = int(n)
    if value == 0:
        return bytearray([0x00])
    result = bytearray()
    round = 0
    while value > 0:
        # only use the lower 7 bits of this byte (big endian)
        # if subsequent length byte, set highest bit to 1, else just insert the value with
        # sets length-bit to 1 on all but first
        result.insert(0, value & 127 | 128 if round > 0 else value & 127)
        value >>= 7
        round += 1
    return result

# i don't know how the hell this works. thanks starrypy dude
# source: https://github.com/CarrotsAreMediocre/StarryPy/blob/master/packets/data_types.py
# funny license
def unpack_vlqs(data):
    logging.debug("Unpacking VLQS")
    value = 0
    offset = 0
    while True:
        tmp = data[offset]
        value = (value << 7) | (tmp & 0x7f)
        offset += 1
        if tmp & 0x80 == 0:
            break
    if (value & 1) == 0x00:
        return (value >> 1), offset
    else:
        return -((value >> 1)+1), offset

def pack_vlqs(var):
    logging.debug("Packing VLQS")
    value = abs(var * 2)
    if var < 0:
        value -= 1
    return pack_vlq(value)

# <vlq len of str><str>
def unpack_vlq_str(data):
    logging.debug("Unpacking string")
    if data[0] == "\x00":
        return "", 0
    vlq = unpack_vlq(data)
    pat = str(vlq[0]) + "c"
    string = unpack_from(pat, data, vlq[1]), (vlq[1] + vlq[0])
    return unpack_str(string[0]), string[1]

def pack_vlq_str(var):
    logging.debug("Packing string")
    if var == "":
        return b"\x00"
    vlq = pack_vlq(len(var))
    string = pack_str(var)
    return vlq + string

# <vlq total items><vlq str len><str>...
def unpack_str_list(data):
    logging.debug("Unpacking string list")
    list_total = unpack_vlq(data)
    offset = list_total[1]
    str_list = []
    for i in range(list_total[0]):
        vlq_str = unpack_vlq_str(data[offset:])
        str_list.append(vlq_str[0])
        offset += vlq_str[1]
    return str_list, offset

def pack_str_list(var):
    logging.debug("Packing string list")
    list_total = len(var)
    str_list = b""
    for string in var:
        str_list += pack_vlq_str(string)
    return pack_vlq(list_total) + str_list

# unset value, 0 bytes
def unpack_variant1(data):
    logging.debug("Unpacking variant1")
    return None, 0

def pack_variant1(var):
    logging.debug("Packing variant1")
    return b''

# big endian double
def unpack_variant2(data):
    logging.debug("Unpacking varian2")
    # TODO: can these be plain unpack()?
    return unpack_from(">d", data, 0)[0], 8

def pack_variant2(var):
    logging.debug("Packing variant2")
    return pack(">d", var)

# boolean
def unpack_variant3(data):
    logging.debug("Unpacking variant3")
    variant = unpack_from("b", data, 0)
    if variant[0] == 1:
        return True, 1
    else:
        return False, 1

def pack_variant3(var):
    logging.debug("Packing variant3")
    return pack("b", var)

# variant list
# <vlq total><variant>...
def unpack_variant6(data):
    logging.debug("Unpacking variant6")
    total = unpack_vlq(data)
    offset = total[1]
    variants = []
    for i in range(total[0]):
        variant = unpack_variant(data[offset:])
        variants.append(variant[0])
        offset += variant[1]
    return variants, offset

def pack_variant6(var):
    logging.debug("Packing variant6")
    total = len(var)
    variant_list = b""
    for variant in var:
        variant_list += pack_variant(variant)
    return pack_vlq(total) + variant_list

# variant dict
# <vlq total><vlq key str len><str key><variant>...
def unpack_variant7(data):
    logging.debug("Unpacking variant7")
    total = unpack_vlq(data)
    offset = total[1]
    dict_items = {}
    if total[0] != 0:
        for i in range(total[0]):
            key = unpack_vlq_str(data[offset:])
            offset += key[1]
            value = unpack_variant(data[offset:])
            offset += value[1]
            dict_items[key[0]] = value[0]
    return dict_items, offset

def pack_variant7(var):
    logging.debug("Packing variant7")
    total = len(var)
    dict_items = b""
    for k in var.keys():
        logging.debug(k)
        key = pack_vlq_str(k)
        value = pack_variant(var[k])
        dict_items += key + value
    return pack_vlq(total) + dict_items

def unpack_variant(data):
    variant_type = unpack_vlq(data)
    offset = variant_type[1]
    unpacked = variant_types[variant_type[0]][0](data[offset:])
    offset += unpacked[1]
    return unpacked[0], offset

def pack_variant(var):
    if var == None:
        return b'\x01' + variant_types[1][1](var)
    elif type(var) is float:
        return b'\x02' + variant_types[2][1](var)
    elif type(var) is bool:
        return b'\x03' + variant_types[3][1](var)
    elif type(var) is int:
        return b'\x04' + variant_types[4][1](var)
    elif type(var) is str:
        return b'\x05' + variant_types[5][1](var)
    elif type(var) is list:
        return b'\x06' + variant_types[6][1](var)
    elif type(var) is dict:
        return b'\x07' + variant_types[7][1](var)
    else:
        raise WrongSaveVer("Unsupported variant type")

def unpack_starsave(data):
    save = {}

    entity_name = unpack_vlq_str(data)
    save["entity_name"] = entity_name[0]
    offset = entity_name[1]

    variant_ver = unpack_from("<i", data, offset)
    save["variant_version"] = variant_ver[0]
    offset += 4

    save_data = unpack_variant6(data[offset:])
    # TODO: this will work but might break
    # need a way to figure the right list item on the fly?
    save["data"] = save_data[0][0]
    offset += save_data[1]

    return save, offset

def pack_starsave(var):
    data = b''
    logging.debug("Packing entity name")
    entity_name = pack_vlq_str(var["entity_name"])
    data += entity_name
    logging.debug("Packing variant version")
    variant_ver = pack("<i", var["variant_version"])
    data += variant_ver
    logging.debug("Packing save data")
    save_data = pack_variant6([var["data"]])
    data += save_data
    return data

# just grabs any remaining bytes
def unpack_the_rest(data):
    return data, len(data)

def pack_the_rest(var):
    return var

# unpack any starbound save type
def unpack_var(var, data):
    pattern = var[1]
    length = var[2]

    if pattern in save_file_types:
        return save_file_types[pattern][0](data)
    else:
        # TODO: same here, can we make it unpack()?
        return unpack_from(pattern, data, 0), length

def pack_var(var, data):
    pattern = var[1]

    if pattern in save_file_types:
        return save_file_types[pattern][1](data)
    else:
        return pack(pattern, *data)

# all the special save file types
# name: (unpack func, pack func)
save_file_types = {
    "__starsave__": (unpack_starsave, pack_starsave),
    "__the_rest__": (unpack_the_rest, pack_the_rest)
}

# variant types
# (unpack func, pack func)
variant_types = (
    # unknown
    (None, None),
    # 1: indicates value is empty (0 bytes)
    (unpack_variant1, pack_variant1),
    # 2: big endian double
    (unpack_variant2, pack_variant2),
    # 3: boolean
    (unpack_variant3, pack_variant3),
    # 4: vlqs
    (unpack_vlqs, pack_vlqs),
    # 5: vlq string
    (unpack_vlq_str, pack_vlq_str),
    # 6: list of variants
    (unpack_variant6, pack_variant6),
    # 7: dict of variants
    (unpack_variant7, pack_variant7)
)

def new_item(name, count, data):
    item = {
        "name": name,
        "count": count,
        "data": data
    }
    return item

class WrongSaveVer(Exception):
    pass

class PlayerSave():
    def __init__(self, filename):
        self.data = {}
        self.import_save(filename)
        self.filename = filename
        # this is just to shorten variable names, we copy it back on export
        self.entity = self.data["save"]["data"]

    def import_save(self, filename=None):
        logging.debug("Init save import: " + filename)
        save_file = open(filename, mode="rb")
        save_data = save_file.read()

        # do a version check first
        try:
            save_ver = unpack_str(unpack_var(data_format[0], save_data)[0])
        except struct.error:
                msg = "Save file is corrupt"
                logging.exception(msg)
                raise WrongSaveVer(msg)
        if save_ver != data_version:
            msg = "Wrong save format version"
            logging.exception(msg)
            raise WrongSaveVer(msg)

        # populate self.data with save data
        offset = 0
        for var in data_format:
            logging.debug("Unpacking " + var[0])
            try:
                unpacked = unpack_var(var, save_data[offset:])
            except:
                msg = "Save file is corrupt"
                logging.exception(msg)
                raise WrongSaveVer(msg)

            self.data[var[0]] = unpacked[0]
            offset += unpacked[1]

        save_file.close()

    def export_save(self, filename=None):
        logging.debug("Init save export: " + self.filename)
        self.data["save"]["data"] = self.entity
        player_data = b""

        for var in data_format:
            logging.debug("Packing " + var[0])
            player_data += pack_var(var, self.data[var[0]])

        if filename != None:
            save_file = open(filename, "wb")
            save_file.write(player_data)
            save_file.close()
            return filename
        else:
            return player_data

    def dump(self):
        pprint(self.data)

    # getters
    def get_header(self):
        return unpack_str(self.data["header"])

    def get_uuid(self):
        return self.entity["uuid"]

    # stats
    def get_food(self):
        return self.entity["status"]["foodSchema"]["value"], self.entity["status"]["foodSchema"]["max"]

    def get_max_food(self):
        return self.entity["statusParameters"]["baseMaxFood"]

    def get_health(self):
        return self.entity["status"]["healthSchema"]["value"], self.entity["status"]["healthSchema"]["max"]

    def get_max_health(self):
        return self.entity["statusParameters"]["baseMaxHealth"]

    def get_warmth(self):
        return self.entity["status"]["warmthSchema"]["value"], self.entity["status"]["warmthSchema"]["max"]

    def get_max_warmth(self):
        return self.entity["statusParameters"]["baseMaxWarmth"]

    def get_energy(self):
        return self.entity["status"]["energySchema"]["value"], self.entity["status"]["energySchema"]["max"]

    def get_max_energy(self):
        return self.entity["statusParameters"]["baseMaxEnergy"]

    def get_breath(self):
        return self.entity["status"]["breathSchema"]["value"], self.entity["status"]["breathSchema"]["max"]

    def get_max_breath(self):
        return self.entity["statusParameters"]["baseMaxBreath"]

    def get_energy_regen(self):
        return self.entity["statusParameters"]["energyReplenishmentRate"]

    def get_gender(self):
        return self.entity["identity"]["gender"]

    def get_head(self):
        equip = self.entity["inventory"]["equipment"]
        return equip[0], equip[4]

    def get_chest(self):
        equip = self.entity["inventory"]["equipment"]
        return equip[1], equip[5]

    def get_legs(self):
        equip = self.entity["inventory"]["equipment"]
        return equip[2], equip[6]

    def get_back(self):
        equip = self.entity["inventory"]["equipment"]
        return equip[3], equip[7]

    def get_main_bag(self):
        return self.entity["inventory"]["bag"]

    def get_tile_bag(self):
        return self.entity["inventory"]["tileBag"]

    def get_action_bar(self):
        return self.entity["inventory"]["actionBar"]

    def get_wieldable(self):
        return self.entity["inventory"]["wieldable"]

    def get_race(self, pretty=False):
        race = self.entity["identity"]["species"]
        if pretty:
            try:
                race = race[0].upper() + race[1:]
            except IndexError:
                logging.exception("Unable to format race: %s", race)
        return race

    def get_pixels(self):
        return self.entity["inventory"]["money"]

    def get_name(self):
        return self.entity["identity"]["name"]

    def get_description(self):
        return self.entity["description"]

    def get_blueprints(self):
        return self.entity["blueprints"]

    # here be setters
    def set_blueprints(self, blueprints):
        self.entity["blueprints"] = blueprints

    def set_name(self, name):
        self.entity["identity"]["name"] = name

    # TODO: at some point we need to run through and replace all "race"
    # references to species
    def set_race(self, race):
        self.entity["identity"]["species"] = race.lower()

    def set_pixels(self, pixels):
        self.entity["inventory"]["money"] = int(pixels)

    def set_description(self, description):
        self.entity["description"] = description

    def set_gender(self, gender):
        self.entity["identity"]["gender"] = gender.lower()

    # stats
    def set_health(self, current, max):
        self.entity["status"]["healthSchema"]["value"] = float(current)
        self.entity["status"]["healthSchema"]["max"] = float(max)

    def set_max_health(self, max):
        self.entity["statusParameters"]["baseMaxHealth"] = float(max)

    def set_energy(self, current, max):
        self.entity["status"]["energySchema"]["max"] = float(max)
        self.entity["status"]["energySchema"]["value"] = float(current)

    def set_max_energy(self, max):
        self.entity["statusParameters"]["baseMaxEnergy"] = float(max)

    def set_food(self, current, max):
        self.entity["status"]["foodSchema"]["max"] = float(max)
        self.entity["status"]["foodSchema"]["value"] = float(current)

    def set_max_food(self, max):
        self.entity["statusParameters"]["baseMaxFood"] = float(max)

    def set_max_warmth(self, max):
        self.entity["status"]["warmthSchema"]["max"] = float(max)
        self.entity["statusParameters"]["baseMaxWarmth"] = float(max)

    def set_max_breath(self, max):
        self.entity["status"]["breathSchema"]["max"] = float(max)
        self.entity["statusParameters"]["baseMaxBreath"] = float(max)

    def set_energy_regen(self, rate):
        self.entity["statusParameters"]["energyReplenishmentRate"] = float(rate)

    def set_main_bag(self, bag):
        self.entity["inventory"]["bag"] = bag

    def set_tile_bag(self, bag):
        self.entity["inventory"]["tileBag"] = bag

    def set_action_bar(self, bag):
        self.entity["inventory"]["actionBar"] = bag

    def set_wieldable(self, bag):
        self.entity["inventory"]["wieldable"] = bag

    def set_head(self, main, glamor):
        self.entity["inventory"]["equipment"][0] = main
        self.entity["inventory"]["equipment"][4] = glamor

    def set_chest(self, main, glamor):
        self.entity["inventory"]["equipment"][1] = main
        self.entity["inventory"]["equipment"][5] = glamor

    def set_legs(self, main, glamor):
        self.entity["inventory"]["equipment"][2] = main
        self.entity["inventory"]["equipment"][6] = glamor

    def set_back(self, main, glamor):
        self.entity["inventory"]["equipment"][3] = main
        self.entity["inventory"]["equipment"][7] = glamor

if __name__ == '__main__':
    #logging.basicConfig(filename="save_file.log", level=logging.DEBUG)
    player = PlayerSave(sys.argv[1])
    player.dump()
    print(player.export_save())
