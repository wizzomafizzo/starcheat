#!/usr/bin/python

from struct import *
import sys

player_filename = sys.argv[1]

# (name, format, offest)
data_format = (
    # File header
    ("header", "8c", 8),
    ("version", ">i", 4),
    ("global_vlq", "__global_vlq__", "__vlq__"),
    ("uuid", "b16c", (1+16)),
    # Player customisation
    ("name", "__vlq_str__", "__vlq__"),
    ("race", "__vlq_str__", "__vlq__"),
    ("gender", "b", 1),
    ("hair_group", "__vlq_str__", "__vlq__"),
    ("hair_type", "__vlq_str__", "__vlq__"),
    ("hair_color", "__vlq_str__", "__vlq__"),
    ("body_color", "__vlq_str__", "__vlq__"),
    #("beard_group", "__vlq_str__", "__vlq__"),
    #("beard_type", "__vlq_str__", "__vlq__"),
    #("beard_color", "__vlq_str__", "__vlq__"),
    #("face_type", "__vlq_str__", "__vlq__"),
    #("face_group", "__vlq_str__", "__vlq__"),
    ("unknown1", "6x", 6),
    ("idle1", "__vlq_str__", "__vlq__"),
    ("idle2", "__vlq_str__", "__vlq__"),
    ("pers_offset", "4c", 4),
    # Status entity
    ("status", ">b20f", (1+(20*4))),
    ("body_material", "__vlq_str__", "__vlq__"),
    ("damage_config", "__vlq_str__", "__vlq__"),
    # Player status
    ("health", ">2f", (2*4)),
    ("energy", ">2f", (2*4)),
    ("warmth", ">2f", (2*4)),
    ("food", ">2f", (2*4)),
    ("breath", ">2f", (2*4)),
    ("invulnerable", "b", 1),
    # What is this? May need a new datatype for string lists
    #("glow", ">3fc", (3*4+1)),
    #("unknown_string_1", "__vlq_str__", "__vlq__"),
    #("unknown_string_2", "__vlq_str__", "__vlq__"),
    #("unknown_string_3", "__vlq_str__", "__vlq__"),
    #("unknown_string_4", "__vlq_str__", "__vlq__"),
    #("unknown_string_5", "__vlq_str__", "__vlq__"),
    #("unknown_string_6", "__vlq_str__", "__vlq__"),
    #("unknown_bool", "b", 1),
    #("description", "__vlq_str__", "__vlq__"),
    #("play_time", ">d", 8),
    ("the_rest", "__the_rest__", "__the_rest__")
)

def get_vlq_str(bytes):
    vlq = vlq2int(bytes)
    pat = str(vlq[0]) + "c"
    string = unpack_from(pat, bytes, vlq[1]), (vlq[1] + vlq[0])
    return get_str(string[0]), string[1]

def get_str(bytes):
    return "".join(map(chr,map(ord,bytes)))

# TODO: Learn how these work... theory makes sense but this bit manipulation is magic
# TODO: Licenses?
# https://github.com/metachris/binary-serializer/blob/master/python/bincalc.py
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

# http://stackoverflow.com/questions/6776553/python-equivalent-of-perls-w-packing-format
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

class Player():
    def __init__(self, player_filename):
        player_file = open(player_filename, mode="r+b")
        self.player_data = player_file.read()
        self.offset = 0
        self.data = {}
        for var in data_format:
            self.unpack_var(var)
        player_file.close()

    def inc(self, x): self.offset = self.offset + x

    def unpack_var(self, var):
        name = var[0]
        pattern = var[1]
        length = var[2]
        if pattern == "__vlq_str__":
            raw = get_vlq_str(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(raw[1])
        elif pattern == "__global_vlq__":
            raw = vlq2int(self.player_data[self.offset:])
            var_val = raw[0]
            self.inc(2)
        elif pattern == "__the_rest__":
            var_val = self.player_data[self.offset:]
            self.inc(len(var_val))
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
            return int2vlq(data)
        elif pattern == "__the_rest__":
            return data
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
        if filename:
            file = open(filename, "wb")
            file.write(header_data + player_data)
            file.close()
            return filename
        else:
            return header_data + player_data

player = Player(player_filename)

player.data["health"] = (300.0, 300.0) # works for like a second
player.data["name"] = "TEST"

for i in data_format:
    print(i[0], ":", player.data[i[0]])

print(player.export("test.player"))
#print(player.export())
