# A library to read Starbound's SBAsset format.
# I know it's terrible
import struct
import logging
# Make sure the file is a valid pak, then get various information from it.


def get_pak_info(pak):
    # Check that the pak is valid
    header = pak.read(8)
    assert header == b'SBAsset6', 'Unrecognized format!'
    # Find the metadata and file index
    index_offset = pak.read(8)
    index_offset = struct.unpack('>q', index_offset)[0]
    logging.debug(index_offset)
    pak.seek(index_offset)
    index_header = pak.read(5)
    assert index_header == b'INDEX', 'Index offset incorrect!'
    # Get metadata information
    meta_count = read_varint(pak)
    metadata = {}
    for x in range (0, meta_count):
        key_len = read_varint(pak)
        print(pak.tell())
        key = str(struct.unpack(str(key_len) + 's', pak.read(key_len))[0], "utf-8")
        print(key)
        metadata[key] = read_dynamic(pak)
    # Locate the beginning of the file index
    file_count = read_varint(pak)
    file_offset = pak.tell()
    return metadata, file_count, file_offset


# Given an index, file path, and pak, returns a file from the pak
def get_file(pak, file_offset, file_length):
    pak.seek(file_offset)
    file = pak.read(file_length)
    return file


# Given a pak, the pak's file offset, and the number of files in the pak, creates an index
def create_file_index(pak, index_offset, file_count):
    pak.seek(index_offset)
    path_len = struct.unpack('>B', pak.read(1))[0]
    index = {}
    for x in range(1, file_count):
        path = str(struct.unpack(str(path_len) + 's', pak.read(path_len))[0], "utf-8")
        file_offset = struct.unpack('>q', pak.read(8))[0]
        file_length = struct.unpack('>q', pak.read(8))[0]
        file_info = [file_offset, file_length]
        path_len = struct.unpack('>B', pak.read(1))[0]
        index.update({path:[file_offset, file_length]})
    return index


# Blatantly stolen from py-starbound, thanks blixt
def read_bytes(stream):
    length = read_varint(stream)
    return stream.read(length)


def read_varint(stream):
    """Read while the most significant bit is set, then put the 7 least
    significant bits of all read bytes together to create a number.

    """
    value = 0
    while True:
        byte = ord(stream.read(1))
        if not byte & 0b10000000:
            return value << 7 | byte
        value = value << 7 | (byte & 0b01111111)


def read_varint_signed(stream):
    value = read_varint(stream)

    # Least significant bit represents the sign.
    if value & 1:
        return -(value >> 1)
    else:
        return value >> 1


def read_dynamic(stream):
    type_id = ord(stream.read(1))
    if type_id == 1:
        return None
    elif type_id == 2:
        return struct.unpack('>d', stream.read(8))[0]
    elif type_id == 3:
        return stream.read(1) != b'\0'
    elif type_id == 4:
        return read_varint_signed(stream)
    elif type_id == 5:
        return read_string(stream)
    elif type_id == 6:
        return read_list(stream)
    elif type_id == 7:
        return read_map(stream)
    raise ValueError('Unknown dynamic type 0x%02X' % type_id)


def read_list(stream):
    length = read_varint(stream)
    return [read_dynamic(stream) for _ in range(length)]


def read_map(stream):
    length = read_varint(stream)
    value = dict()
    for _ in range(length):
        key = read_string(stream)
        value[key] = read_dynamic(stream)
    return value


def read_string(stream):
  return read_bytes(stream).decode('utf-8')