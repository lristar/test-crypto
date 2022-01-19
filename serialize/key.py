from typing import Tuple

from ellipticCurve.curve.curve import *


def other_gen_keypair(curve: Curve, d: int) -> Tuple[int, Point]:
    private_key = other_private_key(d)
    public_key = get_public_key(private_key, curve)
    return private_key, public_key


def other_private_key(p: int):
    return p


def get_public_key(d: int, curve: Curve) -> Point:
    return d * curve.G
