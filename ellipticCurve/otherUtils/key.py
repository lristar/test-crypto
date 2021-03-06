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


def gen_share_keypair(curve: Curve,
                      randfunc: Callable = None) -> Tuple[int, int, Point]:
    randfunc = randfunc or urandom
    private_key1 = gen_private_key(curve, randfunc)
    private_key2 = gen_private_key(curve, randfunc)
    public_key = gen_share_pub_key(private_key1, private_key2, curve)
    return private_key1, private_key2, public_key


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


def gen_share_pub_key(p1: int, p2: int, curve: Curve) -> Point:
    return (p1 * curve.G) + (p2 * curve.G)


def get_public_key(d: int, curve: Curve) -> Point:
    return d * curve.G


def other_gen_keypair(curve: Curve,
                      d: int) -> Tuple[int, Point]:
    private_key = other_private_key(d)
    public_key = get_public_key(private_key, curve)
    return private_key, public_key


def other_private_key(p: int):
    return p
