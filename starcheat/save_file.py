"""
Import/export Starbound .player save files

This module allows you to import a Starbound .player save file as a dictionary,
edit it how you like and then export it again.

It can also be run from the command line to dump the contents, like this:
$ python ./save_file.py <.player file>
"""

import sys, binascii
from struct import *

# compatible save version(s)
data_version = range(424, 429)
# this is the complete data format definition for a .player file. formats
# surrounded by double underscores are special types with unpack/repack
# functions defined later in the file. everything else is standard formats for
# the python struct module. the offsets define how many bytes an attribute is
# with None types meaning they're variable length
# and this is extremely helpful: https://github.com/McSimp/starbound-research
# (name, format, offset)
data_format = (
    ("header", "8c", 8),
    ("version", ">i", 4),
    ("global_vlq", "__global_vlq__", None),
    ("uuid", "b16c", 1+16),
    ("name", "__vlq_str__", None),
    ("race", "__vlq_str__", None),
    ("gender", "b", 1),
    ("hair_group", "__vlq_str__", None),
    ("hair_type", "__vlq_str__", None),
    ("hair_directive", "__vlq_str__", None),
    ("body_directive", "__vlq_str__", None),
    ("beard_group", "__vlq_str__", None),
    ("beard_type", "__vlq_str__", None),
    ("beard_directive", "__vlq_str__", None),
    ("face_type", "__vlq_str__", None),
    ("face_group", "__vlq_str__", None),
    ("face_directive", "__vlq_str__", None),
    ("idle1", "__vlq_str__", None),
    ("idle2", "__vlq_str__", None),
    ("head_offset", ">2f", 2*4),
    ("arm_offset", ">2f", 2*4),
    ("fav_color", "4B", 4),
    ("god_mode", "b", 1), # not working?
    ("body_temp_range_low", ">2f", 2*4),
    ("ideal_temp", ">f", 4),
    ("base_max_warmth", ">f", 4),
    ("warmth_transfer_rate", ">f", 4),
    ("warmth_transfer_rate_cap", ">f", 4),
    ("comfort_regen", ">f", 4),
    ("base_max_health", ">f", 4),
    ("base_max_energy", ">f", 4),
    ("energy_regen_rate", ">f", 4),
    ("base_max_food", ">f", 4),
    ("food_deplete_rate", ">f", 4),
    ("base_max_breath", ">f", 4),
    ("breath_replenish_rate", ">f", 4),
    ("breath_deplete_rate", ">f", 4),
    ("wind_chill_factor", ">f", 4),
    ("body_material", "__vlq_str__", None),
    ("damage_config", "__vlq_str__", None),
    ("health", ">2f", 2*4),
    ("energy", ">2f", 2*4),
    ("warmth", ">2f", 2*4),
    ("food", ">2f", 2*4),
    ("breath", ">2f", 2*4),
    ("invulnerable", "b", 1), # not working?
    ("glow", ">3f", 3*4),
    ("active_effects", "__str_list__", None),
    ("active_effects_sources", "__str_list__", None),
    ("description", "__vlq_str__", None),
    ("play_time", ">d", 8),
    ("inv", "__inv__", None),
    ("blueprint_lib", "__blueprint_lib__", None),
    ("tech", "__tech__", None), # TODO: just pulled in as raw bytes atm
    ("head", "__item_desc__", None),
    ("chest", "__item_desc__", None),
    ("legs", "__item_desc__", None),
    ("back", "__item_desc__", None),
    ("head_glamor", "__item_desc__", None),
    ("chest_glamor", "__item_desc__", None),
    ("legs_glamor", "__item_desc__", None),
    ("back_glamor", "__item_desc__", None),
    ("primary_tool", "__item_desc__", None),
    ("alt_tool", "__item_desc__", None),
    ("suppress_items", "b", 1),
    ("the_rest", "__the_rest__", None)
)

race_types = ("Apex", "Avian", "Floran", "Glitch", "Human", "Hylotl")

def unpack_str(bytes):
    """Convert a list of bytes to a string."""
    return "".join(map(chr,map(ord,bytes)))

def pack_str(var):
    """Convert a string to a list of bytes."""
    return str(var).encode("utf-8")

# TODO: learn how these work... theory makes sense but this bit manipulation is magic
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

# big endian double
def unpack_variant2(data):
    # TODO: can these be plain pack()?
    return unpack_from(">d", data, 0), 8

def pack_variant2(var):
    return pack(">d", *var)

# boolean
def unpack_variant3(data):
    return unpack_from("b", data, 0), 1

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
    dict_items = []
    if total[0] != 0:
        for i in range(total[0]):
            key = unpack_vlq_str(data[offset:])
            offset += key[1]
            value = unpack_variant(data[offset:])
            offset += value[1]
            dict_items.append((key[0], value[0]))
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
    return (variant_type[0], unpacked[0]), offset

def pack_variant(var):
    variant_type = var[0]
    packed_variant = variant_types[variant_type][1](var[1])
    return pack_vlq(variant_type) + packed_variant

# <vlq str len><str item name><vlq no. items><variant>
# not sure why the count is always +1?
def unpack_item_desc(data):
    name = unpack_vlq_str(data)
    offset = name[1]
    count = unpack_vlq(data[offset:])
    offset += count[1]
    variant = unpack_variant(data[offset:])
    offset += variant[1]
    return (name[0], count[0]-1, variant[0]), offset

def pack_item_desc(var):
    name = pack_vlq_str(var[0])
    count = pack_vlq(var[1]+1)
    variant = pack_variant(var[2])
    return name + count + variant

# <vlq stream len><vlq no. blueprints><item desc>...
def unpack_blueprint_library(data):
    total_size = unpack_vlq(data)
    offset = total_size[1]
    blueprint_count = unpack_vlq(data[offset:])
    offset += blueprint_count[1]
    blueprints = []
    for i in range(blueprint_count[0]):
        blueprint = unpack_item_desc(data[offset:])
        blueprints.append(blueprint[0])
        offset += blueprint[1]
    return blueprints, offset

def pack_blueprint_library(var):
    blueprint_count = pack_vlq(len(var))
    blueprints = b""
    for blueprint in var:
        blueprints += pack_item_desc(blueprint)
    blueprint_list = blueprint_count + blueprints
    return pack_vlq(len(blueprint_list)) + blueprint_list

# dunno about this yet, just get it raw
def unpack_tech(data):
    total_size = unpack_vlq(data)
    offset = total_size[1]
    tech = unpack_from(str(total_size[0])+"c", data, offset)
    offset += len(tech)
    return tech, offset

def pack_tech(var):
    return pack_vlq(len(var)) + b"".join(var)

# <vlq no. slots><item desc>...
def unpack_bag(data):
    slot_count = unpack_vlq(data)
    offset = slot_count[1]
    items = []
    for i in range(slot_count[0]):
        item = unpack_item_desc(data[offset:])
        items.append(item[0])
        offset += item[1]
    return items, offset

def pack_bag(var):
    bag = b""
    for item in var:
        bag += pack_item_desc(item)
    return pack_vlq(len(var)) + bag

# data format for inventory type
inv_type = (
    ("inv_size", "__vlq__", None),
    ("pixels", ">q", 8),
    ("main_bag", "__bag__", None),
    ("tile_bag", "__bag__", None),
    ("action_bar", "__bag__", None),
    ("equipment", "__bag__", None),
    ("wieldable", "__bag__", None),
    ("swap_active", "__item_desc__", None),
    ("left_hand_bag", "__vlq__", None),
    ("left_hand_slot", "__vlq__", None),
    ("right_hand_bag", "__vlq__", None),
    ("right_hand_slot", "__vlq__", None)
)

def unpack_inv(data):
    offset = 0
    inv_vars = {}
    for var in inv_type:
        unpacked = unpack_var(var, data[offset:])
        inv_vars[var[0]] = unpacked[0]
        offset += unpacked[1]
    return inv_vars, offset

def pack_inv(data):
    inv_data = b""
    for var in inv_type[1:]:
        inv_data += pack_var(var, data[var[0]])
    inv_size = pack_vlq(len(inv_data))
    return inv_size + inv_data

# just grabs any remaining bytes
def unpack_the_rest(data):
    return data, len(data)

def pack_the_rest(var):
    return var

def empty_slot():
    return ("", 0, (7, []))

# unpack any starbound save type
def unpack_var(var, data):
    name = var[0]
    pattern = var[1]
    length = var[2]

    if pattern in save_file_types:
        return save_file_types[pattern][0](data)
    else:
        # TODO: same here, can we make it pack()?
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
    "__vlq__": (unpack_vlq, pack_vlq),
    "__vlq_str__": (unpack_vlq_str, pack_vlq_str),
    "__global_vlq__": (unpack_vlq, pack_vlq), # this isn't used normally
    "__inv__": (unpack_inv, pack_inv),
    "__the_rest__": (unpack_the_rest, pack_the_rest),
    "__bag__": (unpack_bag, pack_bag),
    "__item_desc__": (unpack_item_desc, pack_item_desc),
    "__blueprint_lib__": (unpack_blueprint_library, pack_blueprint_library),
    "__tech__": (unpack_tech, pack_tech),
    "__str_list__": (unpack_str_list, pack_str_list)
}

# variant types
# (unpack func, pack func)
variant_types = (
    # unknown
    (None, None),
    # unknown
    (None, None),
    # big endian double
    (unpack_variant2, pack_variant2),
    # boolean
    (unpack_variant3, pack_variant3),
    # vlq
    (unpack_vlq, pack_vlq),
    # vlq string
    (unpack_vlq_str, pack_vlq_str),
    # list of variants
    (unpack_variant6, pack_variant6),
    # dict of variants
    (unpack_variant7, pack_variant7)
)

class PlayerSave():
    def __init__(self, filename):
        self.data = {}
        self.import_save(filename)
        self.filename = filename

    def import_save(self, filename=None):
        save_file = open(filename, mode="rb")
        save_data = save_file.read()

        # do a version check first
        version = unpack_from(data_format[1][1],
                              save_data,
                              data_format[0][2])
        if (version[0] in data_version) == False:
            raise Exception("Wrong save format version")

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

        if filename:
            save_file = open(filename, "wb")
            save_file.write(file_data)
            save_file.close()
            return filename
        else:
            return file_data

    def dump(self):
        for i in data_format:
            print(i[0], ":", self.data[i[0]])

    def get_uuid(self):
        raw_uuid = self.data["uuid"][1:]
        uuid = b""
        for i in raw_uuid:
            uuid += binascii.hexlify(i)
        return uuid.decode("utf-8")

    def get_save_ver(self):
        return str(self.data["version"][0])

    def get_food(self):
        return self.data["food"]

    def get_max_food(self):
        return self.data["base_max_food"][0]

    def get_health(self):
        return self.data["health"]

    def get_max_health(self):
        return self.data["base_max_health"][0]

    def get_max_warmth(self):
        return self.data["base_max_warmth"][0]

    def get_warmth(self):
        return self.data["warmth"]

    def get_energy(self):
        return self.data["energy"]

    def get_max_energy(self):
        return self.data["base_max_energy"][0]

    def get_energy_regen(self):
        return self.data["energy_regen_rate"][0]

    def get_gender(self):
        if self.data["gender"][0] == 0:
            return "male"
        else:
            return "female"

    def get_breath(self):
        return self.data["breath"]

    def get_max_breath(self):
        return self.data["base_max_breath"][0]

    def get_head(self):
        return self.data["head"], self.data["head_glamor"]

    def get_chest(self):
        return self.data["chest"], self.data["chest_glamor"]

    def get_legs(self):
        return self.data["legs"], self.data["legs_glamor"]

    def get_back(self):
        return self.data["back"], self.data["back_glamor"]

    def get_main_bag(self):
        return self.data["inv"]["main_bag"]

    def get_tile_bag(self):
        return self.data["inv"]["tile_bag"]

    def get_action_bar(self):
        return self.data["inv"]["action_bar"]

    def get_wieldable(self):
        return self.data["inv"]["wieldable"]

    def set_main_bag(self, bag):
        self.data["inv"]["main_bag"] = bag

    def set_tile_bag(self, bag):
        self.data["inv"]["tile_bag"] = bag

    def set_action_bar(self, bag):
        self.data["inv"]["action_bar"] = bag

    def set_wieldable(self, bag):
        self.data["inv"]["wieldable"] = bag

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

    def get_race(self):
        return (self.data["race"][0].upper() + self.data["race"][1:])

    def get_pixels(self):
        return self.data["inv"]["pixels"][0]

    def get_name(self):
        return self.data["name"]

    def get_description(self):
        return self.data["description"]

    # blueprints are stored identically to inventory slots but as far as i've
    # seen there is never any variant data stored. let's just convert to a
    # regular list
    def get_blueprints(self):
        blueprints = [x[0] for x in self.data["blueprint_lib"]]
        return blueprints

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

if __name__ == '__main__':
    player = PlayerSave(sys.argv[1])
    player.dump()
