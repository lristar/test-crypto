from bitcoin.trans.exchange import *


class Script:
    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

    @classmethod
    def parse(cls, s):
        length = read_varInt(s)
        cmds = []
        count = 0
        while count < length:
            current = s.read(1)
            count += 1
            current_bytes = current[0]
            if 1 <= current_bytes <= 75:
                n = current_bytes
                cmds.append(s.read(n))
                count += n
            elif current_bytes == 76:
                data_length = little_endian_to_int(s.read(1))
                cmds.append(s.read(data_length))
                count += 1
            elif current_bytes == 77:
                data_length = little_endian_to_int(s.read(2))
                cmds.append(s.read(data_length))
                count += 2
            else:
                op_code = current_bytes
                cmds.append(op_code)
        if count != length:
            raise SyntaxError('parsing script failed')
        return cls(cmds)

    def serialize(self):
        return self


if __name__ == '__main__':
    s = Script()
    s.parse("adafdf")