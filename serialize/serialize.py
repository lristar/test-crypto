from ellipticCurve.curve.curve import *
from dataclasses import dataclass
from typing import Callable, Tuple
import struct


@dataclass
class signaTrue:
    r: int
    s: int

    def der(self):
        rbin = self.r.to_bytes(32, byteorder='big')
        print('start', rbin)
        # 去掉多余的空的bytes 在开始的时候 避免在后面加0x00时有冲突
        rbin.lstrip(b'\x00')
        print('send1', rbin)
        if rbin[0] & 0x80:
            rbin = b'\x00' + rbin
        print('send2', rbin)
        print('rlen',len(rbin))
        print("rbin-len",bytes([2, len(rbin)]))
        result = bytes([2, len(rbin)]) + rbin
        print("result:", result)
        sbin = self.s.to_bytes(32, byteorder='big')
        # 去掉多余的空的bytes 在开始的时候 避免在后面加0x00时有冲突
        sbin = sbin.lstrip(b'\x00')
        print("sbin:start", sbin)
        if sbin[0] & 0x80:
            sbin = b'\x00' + sbin
        print("sbin:end", sbin)
        print('slen', len(sbin))
        print("sbin-len", bytes([2, len(sbin)]))
        result += bytes([2, len(sbin)]) + sbin
        print("all:", bytes([0x30, len(result)]) + result)
        return bytes([0x30, len(result)]) + result

    @staticmethod
    def decParse(b: bytes) -> Tuple[int, int]:
        rlen = b[3]
        r = b[4:4+rlen]
        s = b[4 + rlen + 2:]
        return int.from_bytes(r, 'big'), int.from_bytes(s, 'big')


