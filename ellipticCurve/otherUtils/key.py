# Reference to https://github.com/AntonKueltz/fastecdsa

from binascii import hexlify
from typing import Callable, Tuple
from ellipticCurve.curve import *



def gen_keypair(curve: EllipticCurve,
                randfunc: Callable = None) -> Tuple[int, Point]:
    randfunc = randfunc or urandom
    private_key = gen_private_key(curve, randfunc)
    public_key = get_public_key(private_key, curve)
    return private_key, public_key


def gen_private_key(curve: EllipticCurve,
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


def get_public_key(d: int, curve: EllipticCurve):
    return curve.G().multi(d)

