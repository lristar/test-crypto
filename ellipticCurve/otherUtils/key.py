# Reference to https://github.com/AntonKueltz/fastecdsa

from binascii import hexlify
from typing import Callable, Tuple
from ellipticCurve.curve.curve import *


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
    print("order:", order)
    while order > 0:
        order >>= 1
        order_bits += 1
    print("order_bits", order_bits)
    order_bytes = (order_bits + 7) // 8
    print("order_bytes",order_bytes)
    extra_bits = order_bytes * 8 - order_bits
    print("extra_bits", extra_bits)
    rand = int(hexlify(randfunc(order_bytes)), 16)
    rand >>= extra_bits
    while rand >= curve.n:
        rand = int(hexlify(randfunc(order_bytes)), 16)
        rand >>= extra_bits
    print("rand:", rand)
    return rand


def get_public_key(d: int, curve: Curve) -> Point:
    return d * curve.G

