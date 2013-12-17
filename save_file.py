#!/usr/bin/python3

# module for importing/exporting save file data

from struct import *

data_version = 424
# extremely helpful: https://github.com/McSimp/starbound-research
# (name, format, offset)
data_format = (
    # TODO: check names make sense
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
    # TODO: these might still exist... best make vlq str handle zero len
    #("beard_group", "__vlq_str__", None),
    #("beard_type", "__vlq_str__", None),
    #("beard_color", "__vlq_str__", None),
    #("face_type", "__vlq_str__", None),
    #("face_group", "__vlq_str__", None),
    ("unknown1", "6x", 6),
    ("idle1", "__vlq_str__", None),
    ("idle2", "__vlq_str__", None),
    ("head_offset", ">2f", 2*4),
    ("arm_offset", ">2f", 2*4),
    ("fav_color", "4B", 4),
    ("god_mode", "b", 1),
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
    ("invulnerable", "b", 1),
    ("glow", ">3f", 3*4),
    ("unknown_list1", "__str_list__", None),
    ("unknown_list2", "__str_list__", None),
    ("description", "__vlq_str__", None),
    ("play_time", ">d", 8),
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
    ("right_hand_slot", "__vlq__", None),
    ("blueprint_lib", "__blueprint_lib__", None),
    ("tech", "__tech__", None),
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
    ("suppress_tools", "b", 1),
    ("the_rest", "__the_rest__", None)
)

# convert byte list to string
def unpack_str(bytes):
    return "".join(map(chr,map(ord,bytes)))

def pack_str(var):
    return str(var).encode("utf-8")

# TODO: learn how these work... theory makes sense but this bit manipulation is magic
# TODO: licenses?
# Source: http://stackoverflow.com/questions/6776553/python-equivalent-of-perls-w-packing-format
def unpack_vlq(data):
    offset = 0
    value = 0
    while True:
        tmp = data[offset]
        value = (value<<7) | (tmp&0x7f)
        offset += 1
        if tmp & 0x80 == 0:
            break
    return value, offset

# Source: https://github.com/metachris/binary-serializer/blob/master/python/bincalc.py
def pack_vlq(n):
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
    vlq = unpack_vlq(data)
    pat = str(vlq[0]) + "c"
    string = unpack_from(pat, data, vlq[1]), (vlq[1] + vlq[0])
    return unpack_str(string[0]), string[1]

def pack_vlq_str(var):
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

# seems to be the format for var metadata
# can be recursive
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
# not sure why the count is always +1
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
    offset = item_count[1]
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
    # this isn't used normally'
    "__global_vlq__": (unpack_vlq, pack_vlq),
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

    def import_save(self, filename=None):
        save_file = open(filename, mode="rb")
        save_data = save_file.read()

        # do a version check first
        version = unpack_from(data_format[1][1],
                              save_data,
                              data_format[0][2])
        if version[0] != data_version:
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
