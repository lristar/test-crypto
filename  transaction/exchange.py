def little_endian_to_int(b):
    return int.from_bytes(b, 'little')


def int_to_little_endian(n: int, length: int):
    return n.to_bytes(length, 'little')


def read_varInt(s):
    i = s.read(1)[0]
    if i == 0xfd:
        return little_endian_to_int(s.read(2))
    elif i == 0xfe:
        return little_endian_to_int(s.read(4))
    elif i == 0xff:
        return little_endian_to_int(s.read(8))
    else:
        return i


def encode_varInt(s):
    if s < 0xfd:
        return bytes([s])
    elif s < 0x10000:
        return b'\xfd' + int_to_little_endian(s, 2)
    elif s < 0x100000000:
        return b'\xfe' + int_to_little_endian(s, 4)
    elif s < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(s, 8)
    else:
        raise ValueError('Integer too large: {}'.format(s))
