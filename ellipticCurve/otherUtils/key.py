# Reference to https://github.com/AntonKueltz/fastecdsa

from binascii import hexlify
from typing import Callable, Tuple
from ellipticCurve.curve.curve import *


@dataclass
class Key:
    priKey: int
    pubKey: Point

    def __init__(self, priKey, pubKey):
        self.priKey = priKey
        self.pubKey = pubKey

    def hex(self):
        return '{:x}'.format(self.priKey).zfill(64)

def gen_keypair(curve: Curve,
                randfunc: Callable = None) -> Tuple[int, Point]:
    randfunc = randfunc or urandom
    private_key = gen_private_key(curve, randfunc)
    public_key = get_public_key(private_key, curve)
    return private_key, public_key


def gen_private_key(curve: Curve,
                    randfunc: Callable = None) -> int:
    order_bits = 0
    order = curve.n
    while order > 0:
        order >>= 1
        order_bits += 1
    order_bytes = (order_bits + 7) // 8
    extra_bits = order_bytes * 8 - order_bits
    rand = int(hexlify(randfunc(order_bytes)), 16)
    rand >>= extra_bits
    while rand >= curve.n:
        rand = int(hexlify(randfunc(order_bytes)), 16)
        rand >>= extra_bits
    return rand


def get_public_key(d: int, curve: Curve) -> Point:
    return d * curve.G
