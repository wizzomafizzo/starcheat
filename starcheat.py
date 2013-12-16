#!/usr/bin/python3

import sys
from struct import *

# extremely helpful: https://github.com/McSimp/starbound-research
# (name, format, offset)
data_version = 424 # TODO: implement check
data_format = (
    # TODO: check names make sense
    ("header", "8c", 8),
    ("version", ">i", 4),
    ("global_vlq", "__global_vlq__", 0),
    ("uuid", "b16c", 1+16),
    ("name", "__vlq_str__", 0),
    ("race", "__vlq_str__", 0),
    ("gender", "b", 1),
    ("hair_group", "__vlq_str__", 0),
    ("hair_type", "__vlq_str__", 0),
    ("hair_color", "__vlq_str__", 0),
    ("body_color", "__vlq_str__", 0),
    # TODO: these might still exist... best make vlq str handle zero len
    #("beard_group", "__vlq_str__", 0),
    #("beard_type", "__vlq_str__", 0),
    #("beard_color", "__vlq_str__", 0),
    #("face_type", "__vlq_str__", 0),
    #("face_group", "__vlq_str__", 0),
    ("unknown1", "6x", 6),
    ("idle1", "__vlq_str__", 0),
    ("idle2", "__vlq_str__", 0),
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
    ("body_material", "__vlq_str__", 0),
    ("damage_config", "__vlq_str__", 0),
    ("health", ">2f", 2*4),
    ("energy", ">2f", 2*4),
    ("warmth", ">2f", 2*4),
    ("food", ">2f", 2*4),
    ("breath", ">2f", 2*4),
    ("invulnerable", "b", 1),
    ("glow", ">3f", 3*4),
    ("unknown_list1", "__str_list__", 0),
    ("unknown_list2", "__str_list__", 0),
    ("description", "__vlq_str__", 0),
    ("play_time", ">d", 8),
    ("inv_size", "__vlq__", 0),
    ("pixels", ">q", 8),
    ("main_bag", "__bag__", 0),
    ("tile_bag", "__bag__", 0),
    ("action_bar", "__bag__", 0),
    ("equipment", "__bag__", 0),
    ("wieldable", "__bag__", 0),
    ("swap_active", "__item_desc__", 0),
    ("left_hand_bag", "__vlq__", 0),
    ("left_hand_slot", "__vlq__", 0),
    ("right_hand_bag", "__vlq__", 0),
    ("right_hand_slot", "__vlq__", 0),
    ("blueprint_library", "__blueprint_lib__", 0),
    ("tech", "__tech__", 0),
    ("head", "__item_desc__", 0),
    ("chest", "__item_desc__", 0),
    ("legs", "__item_desc__", 0),
    ("back", "__item_desc__", 0),
    ("head_glamor", "__item_desc__", 0),
    ("chest_glamor", "__item_desc__", 0),
    ("legs_glamor", "__item_desc__", 0),
    ("back_glamor", "__item_desc__", 0),
    ("primary_tool", "__item_desc__", 0),
    ("alt_tool", "__item_desc__", 0),
    ("suppres_tools", "b", 0),
    ("the_rest", "__the_rest__", 0)
)

# TODO: standard opts (packed data, cur offset) -> (unpacked, new offset)
def unpack_vlq_str(data):
    vlq = vlq2int(data)
    pat = str(vlq[0]) + "c"
    string = unpack_from(pat, data, vlq[1]), (vlq[1] + vlq[0])
    return get_str(string[0]), string[1]

def unpack_tech(data):
    total_size = vlq2int(data)
    offset = total_size[1]
    tech = unpack_from(str(total_size[0])+"c", data, offset)
    offset = offset + len(tech)
    return tech, offset

def unpack_str_list(data):
    list_total = vlq2int(data)
    offset = list_total[1]
    str_list = []
    for i in range(list_total[0]):
        raw = unpack_vlq_str(data[offset:])
        str_list.append(raw[0])
        offset = offset + raw[1]
    return str_list, offset

def pack_variant(var):
    pass

# why "variant"?
# TODO: unpack variant
def unpack_variant(data):
    offset = 0
    def inc(x): nonlocal offset; offset = offset + x

    variant_type = vlq2int(data)
    inc(variant_type[1])

    variant = 0
    # TODO: dict this?
    # 0 = ??
    # 1 = ??
    # 2 = double (be)
    # 3 = boolean
    # 4 = vlq
    # 5 = vlq string
    #     <vlq len of string><string>
    # 6 = variant list
    #     <vlq total variants><variant>...
    # 7 = variant dict
    #     empty dicts are allowed (\x07\x00)
    #     <vlq total dict items><vlq key string len><key string><variant>...
    if variant_type[0] == 2:
        variant = unpack_from(">d", data, offset)
        inc(8)
    elif variant_type[0] == 3:
        variant = unpack_from("b", data, offset)
        inc(1)
    elif variant_type[0] == 4:
        vlq = vlq2int(data[offset:])
        variant = vlq[0]
        inc(vlq[1])
    elif variant_type[0] == 5:
        vlq_str = unpack_vlq_str(data[offset:])
        variant = vlq_str[0]
        inc(vlq_str[1])
    elif variant_type[0] == 6:
        count = vlq2int(data[offset:])
        inc(count[1])
        sub_vars = []
        for i in range(count[0]):
            sub_var = unpack_variant(data[offset:])
            sub_vars.append(sub_var[0])
            inc(sub_var[1])
        variant = sub_vars
    elif variant_type[0] == 7:
        dict_count = vlq2int(data[offset:])
        dict_items = []
        inc(dict_count[1])
        if dict_count[0] != 0:
            for i in range(dict_count[0]):
                key = unpack_vlq_str(data[offset:])
                inc(key[1])
                value = unpack_variant(data[offset:])
                inc(value[1])
                dict_items.append((key[0], value[0]))
        variant = dict_items

    return variant, offset

def unpack_blueprint_library(data):
    offset = 0
    def inc(x): nonlocal offset; offset = offset + x

    total_size = vlq2int(data)
    inc(total_size[1])
    blueprint_count = vlq2int(data[offset:])
    inc(blueprint_count[1])

    blueprints = []
    for i in range(blueprint_count[0]):
        blueprint = unpack_item_desc(data[offset:])
        blueprints.append(blueprint[0])
        inc(blueprint[3])

    return blueprints, offset

def pack_item_desc(var):
    pass

def unpack_item_desc(data):
    offset = 0
    def inc(x): nonlocal offset; offset = offset + x

    name = unpack_vlq_str(data)
    inc(name[1])
    count = vlq2int(data[offset:])
    inc(count[1])
    variant = unpack_variant(data[offset:])
    inc(variant[1])

    return name[0], count[0], variant[0], offset

# heh
def pack_bag(var):
    pass

def unpack_bag(data):
    offset = 0
    def inc(x): nonlocal offset; offset = offset + x

    size = vlq2int(data)
    inc(size[1])
    items = []
    for i in range(size[0]):
        item = unpack_item_desc(data[offset:])
        items.append((item[0], item[1], item[2]))
        inc(item[3])
    return items, offset

def get_str(bytes):
    return "".join(map(chr,map(ord,bytes)))

# TODO: learn how these work... theory makes sense but this bit manipulation is magic
# TODO: licenses?
# Source: https://github.com/metachris/binary-serializer/blob/master/python/bincalc.py
def int2vlq(n):
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

# Source: http://stackoverflow.com/questions/6776553/python-equivalent-of-perls-w-packing-format
def vlq2int(data):
    value = 0
    offset = 0
    while True:
        tmp = data[offset]
        value = (value<<7) | (tmp&0x7f)
        offset += 1
        if tmp & 0x80 == 0:
            break
    return value, offset

# TODO: split this into separate class for reading the file?
class Player():
    def __init__(self, player_filename):
        player_file = open(player_filename, mode="rb")
        self.player_data = player_file.read()
        self.offset = 0
        self.data = {}

        for var in data_format:
            self.unpack_var(var)

        player_file.close()

    def inc(self, x): self.offset = self.offset + x

    def unpack_var(self, var):
        # TODO: not too keen on the nonlocal variable use
        name = var[0]
        pattern = var[1]
        length = var[2]

        # TODO: switch to a dict or something of types if there are many more...
        if pattern == "__vlq_str__":
            raw = unpack_vlq_str(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(raw[1])
        elif pattern == "__global_vlq__":
            raw = vlq2int(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(2)
        elif pattern == "__the_rest__":
            var_val = self.player_data[self.offset:]
            self.inc(len(var_val))
        elif pattern == "__vlq__":
            raw = vlq2int(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(raw[1])
        elif pattern == "__bag__":
            raw = unpack_bag(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(raw[1])
        elif pattern == "__item_desc__":
            raw = unpack_item_desc(self.player_data[self.offset:])
            # TODO: don't like this, need to make standard'
            var_val = (raw[0], raw[1], raw[2])
            self.inc(raw[3])
        elif pattern == "__blueprint_lib__":
            raw = unpack_blueprint_library(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(raw[1])
        elif pattern == "__tech__":
            raw = unpack_tech(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(raw[1])
        elif pattern == "__str_list__":
            raw = unpack_str_list(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(raw[1])
        else:
            raw = unpack_from(pattern, self.player_data, self.offset)
            var_val = raw
            self.inc(length)

        self.data[name] = var_val

    def pack_var(self, var):
        name = var[0]
        pattern = var[1]
        length = var[2]
        data = self.data[name]

        if pattern == "__vlq_str__":
            vlq = int2vlq(len(data))
            return vlq + data.encode("utf-8")
        elif pattern == "__global_vlq__":
            pass
        elif pattern == "__the_rest__":
            return data
        elif pattern == "__vlq__":
            return int2vlq(data)
        else:
            return pack(pattern, *data)

    def export(self, filename=None):
        header_data = b""
        player_data = b""

        for i in data_format[3:]:
            player_data = player_data + self.pack_var(i)

        header = self.pack_var(data_format[0])
        version = self.pack_var(data_format[1])
        global_vlq = int2vlq(len(player_data))
        header_data = header + version + global_vlq
        file_data = header_data + player_data

        if filename:
            file = open(filename, "wb")
            file.write(file_data)
            file.close()
            return filename
        else:
            return file_data

if __name__ == '__main__':
    player_filename = sys.argv[1]
    player = Player(player_filename)

    #player.data["health"] = (300.0, 300.0) # works for like a second
    #player.data["name"] = "PIX HACK"
    #player.data["pixels"] = (99999999,)

    for i in data_format:
        print(i[0], ":", player.data[i[0]])

    #print(player.export("test.player"))
    #print(player.export())
