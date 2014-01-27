"""
Import/export Starbound .player save files

This module allows you to import a Starbound .player save file as a dictionary,
edit it how you like and then export it again.

It can also be run from the command line to dump the contents, like this:
$ python ./save_file.py <.player file>
"""

import sys, pprint
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

def unpack_vlqs(data):
    vlq = unpack_vlq(data)
    return (vlq[0] - 1), vlq[1]

# <vlq len of str><str>
def unpack_vlq_str(data):
    if data[0] == "\x00":
        return "", 0
    vlq = unpack_vlq(data)
    pat = str(vlq[0]) + "c"
    string = unpack_from(pat, data, vlq[1]), (vlq[1] + vlq[0])
    return unpack_str(string[0]), string[1]

def pack_vlq_str(var):
    if var == "":
        return b"\x00"
    vlq = pack_vlq(len(var))
    string = pack_str(var)
    return vlq + string

# <vlq total items><vlq str len><str>...
def unpack_str_list(data):
    list_total = unpack_vlq(data)
    offset = list_total[1]
    str_list = []
    for i in range(list_total[0]):
        vlq_str = unpack_vlq_str(data[offset:])
        str_list.append(vlq_str[0])
        offset += vlq_str[1]
    return str_list, offset

def pack_str_list(var):
    list_total = len(var)
    str_list = b""
    for string in var:
        str_list += pack_vlq_str(string)
    return pack_vlq(list_total) + str_list

# unset value, 0 bytes
def unpack_variant1(data):
    return None, 0

def pack_variant1(var):
    return b'\x01'

# big endian double
def unpack_variant2(data):
    # TODO: can these be plain unpack()?
    return unpack_from(">d", data, 0)[0], 8

def pack_variant2(var):
    return pack(">d", *var)

# boolean
def unpack_variant3(data):
    variant = unpack_from("b", data, 0)
    if variant[0] == 1:
        return True, 1
    else:
        return False, 1

def pack_variant3(var):
    return pack("b", *var)

# variant list
# <vlq total><variant>...
def unpack_variant6(data):
    total = unpack_vlq(data)
    offset = total[1]
    variants = []
    for i in range(total[0]):
        variant = unpack_variant(data[offset:])
        variants.append(variant[0])
        offset += variant[1]
    return variants, offset

def pack_variant6(var):
    total = len(var)
    variant_list = b""
    for variant in var:
        variant_list += pack_variant(variant)
    return pack_vlq(total) + variant_list

# variant dict
# <vlq total><vlq key str len><str key><variant>...
def unpack_variant7(data):
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
    total = len(var)
    dict_items = b""
    for k, v in var:
        key = pack_vlq_str(k)
        value = pack_variant(v)
        dict_items += key + value
    return pack_vlq(total) + dict_items

def unpack_variant(data):
    variant_type = unpack_vlq(data)
    offset = variant_type[1]
    unpacked = variant_types[variant_type[0]][0](data[offset:])
    offset += unpacked[1]
    return unpacked[0], offset

def pack_variant(var):
    variant_type = var[0]
    packed_variant = variant_types[variant_type][1](var[1])
    return pack_vlq(variant_type) + packed_variant

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
    # need a way to figure the right list item on the fly
    save["data"] = save_data[0][0]
    offset += save_data[1]
    return save, offset

def pack_starsave(var):
    return pack_variant(var)

# just grabs any remaining bytes
def unpack_the_rest(data):
    return data, len(data)

def pack_the_rest(var):
    return var

# unpack any starbound save type
def unpack_var(var, data):
    name = var[0]
    pattern = var[1]
    length = var[2]

    if pattern in save_file_types:
        return save_file_types[pattern][0](data)
    else:
        # TODO: same here, can we make it unpack()?
        return unpack_from(pattern, data, 0), length

def pack_var(var, data):
    name = var[0]
    pattern = var[1]
    length = var[2]

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
    # 4: vlqs (signed vlq)
    (unpack_vlqs, pack_vlq),
    # 5: vlq string
    (unpack_vlq_str, pack_vlq_str),
    # 6: list of variants
    (unpack_variant6, pack_variant6),
    # 7: dict of variants
    (unpack_variant7, pack_variant7)
)

class WrongSaveVer(Exception):
    pass

class PlayerSave():
    def __init__(self, filename):
        self.data = {}
        self.import_save(filename)
        self.filename = filename
        # TODO: don't forget to update seflf.data with this on export
        self.entity = self.data["save"]["data"]

    def import_save(self, filename=None):
        save_file = open(filename, mode="rb")
        save_data = save_file.read()

        # do a version check first
        save_ver = unpack_str(unpack_var(data_format[0], save_data)[0])
        if save_ver != data_version:
            raise WrongSaveVer("Wrong save format version detected")

        offset = 0
        for var in data_format:
            unpacked = unpack_var(var, save_data[offset:])
            self.data[var[0]] = unpacked[0]
            offset += unpacked[1]
        save_file.close()

    def export_save(self, filename=None):
        player_data = b""
        for var in data_format[3:]:
            player_data += pack_var(var, self.data[var[0]])

        header = pack_var(data_format[0], self.data["header"])
        version = pack_var(data_format[1], self.data["version"])
        global_vlq = pack_vlq(len(player_data))
        header_data = header + version + global_vlq
        file_data = header_data + player_data

        if filename != None:
            save_file = open(filename, "wb")
            save_file.write(file_data)
            save_file.close()
            return filename
        else:
            return file_data

    def dump(self):
        pprint.pprint(self.data)

    def get_header(self):
        return unpack_str(self.data["header"])

    def get_uuid(self):
        return self.entity["uuid"]

    def get_food(self):
        return self.entity["status"]["foodSchema"]["value"]

    def get_max_food(self):
        return self.entity["status"]["foodSchema"]["max"]

    def get_health(self):
        return self.entity["status"]["healthSchema"]["value"]

    def get_max_health(self):
        return self.entity["status"]["healthSchema"]["max"]

    def get_max_warmth(self):
        return self.entity["status"]["warmthSchema"]["max"]

    def get_warmth(self):
        return self.entity["status"]["warmthSchema"]["value"]

    def get_energy(self):
        return self.entity["status"]["energySchema"]["value"]

    def get_max_energy(self):
        return self.entity["status"]["energySchema"]["value"]

    def get_energy_regen(self):
        return self.entity["statusParameters"]["energyReplenishmentRate"]

    def get_gender(self):
        return self.entity["identity"]["gender"]

    def get_breath(self):
        return self.entity["status"]["breathSchema"]["value"]

    def get_max_breath(self):
        return self.entity["status"]["breathSchema"]["max"]

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

    def get_race(self):
        return self.entity["identity"]["species"]

    def get_pixels(self):
        return self.entity["inventory"]["money"]

    def get_name(self):
        return self.entity["identity"]["name"]

    def get_description(self):
        return self.entity["description"]

    # blueprints are stored identically to inventory slots but as far as i've
    # seen there is never any variant data stored. let's just convert to a
    # regular list
    def get_blueprints(self):
        blueprints = [x[0] for x in self.data["blueprint_lib"]]
        return blueprints

    # here be setters
    def set_blueprints(self, blueprints):
        self.data["blueprint_lib"] = [(x, 1, (7, [])) for x in blueprints]

    def set_name(self, name):
        self.data["name"] = name

    def set_race(self, race):
        self.data["race"] = race.lower()

    def set_pixels(self, pixels):
        self.data["inv"]["pixels"] = (int(pixels),)

    def set_description(self, description):
        self.data["description"] = description

    def set_gender(self, gender):
        bit = 0
        if gender == "female":
            bit = 1
        self.data["gender"] = (bit,)

    def set_health(self, current, maximum):
        self.data["health"] = (current, maximum)

    def set_max_health(self, maximum):
        self.data["base_max_health"] = (maximum,)

    def set_energy(self, current, maximum):
        self.data["energy"] = (current, maximum)

    def set_max_energy(self, maximum):
        self.data["base_max_energy"] = (maximum,)

    def set_food(self, current, maximum):
        self.data["food"] = (current, maximum)

    def set_max_food(self, maximum):
        self.data["base_max_food"] = (maximum,)

    def set_warmth(self, maximum):
        self.data["warmth"] = (self.data["warmth"][0], maximum)

    def set_max_warmth(self, maximum):
        self.data["base_max_warmth"] = (maximum,)

    def set_breath(self, current, maximum):
        self.data["breath"] = (current, maximum)

    def set_max_breath(self, maximum):
        self.data["base_max_breath"] = (maximum,)

    def set_energy_regen(self, rate):
        self.data["energy_regen_rate"] = (rate,)

    def set_main_bag(self, bag):
        self.data["inv"]["main_bag"] = bag

    def set_tile_bag(self, bag):
        self.data["inv"]["tile_bag"] = bag

    def set_action_bar(self, bag):
        self.data["inv"]["action_bar"] = bag

    def set_wieldable(self, bag):
        self.data["inv"]["wieldable"] = bag

    # equipment gets set in two places, there is an individual slot and then
    # a bag for each equpment group. unusual behaviour if you don't set both
    def set_head(self, main, glamor):
        self.data["head"] = main
        self.data["inv"]["equipment"][0] = main
        self.data["head_glamor"] = glamor
        self.data["inv"]["equipment"][4] = glamor

    def set_chest(self, main, glamor):
        self.data["chest"] = main
        self.data["inv"]["equipment"][1] = main
        self.data["chest_glamor"] = glamor
        self.data["inv"]["equipment"][5] = glamor

    def set_legs(self, main, glamor):
        self.data["legs"] = main
        self.data["inv"]["equipment"][2] = main
        self.data["legs_glamor"] = glamor
        self.data["inv"]["equipment"][6] = glamor

    def set_back(self, main, glamor):
        self.data["back"] = main
        self.data["inv"]["equipment"][3] = main
        self.data["back_glamor"] = glamor
        self.data["inv"]["equipment"][7] = glamor

if __name__ == '__main__':
    player = PlayerSave(sys.argv[1])
    player.dump()
