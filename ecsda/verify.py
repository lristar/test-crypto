from ecsda.sign import signaTrue
from ellipticCurve.mathUtils.quickMod import *
from ellipticCurve.curve.curve import *


def vertify(point: Point, z, sig: signaTrue):
    s_inv = quickM(sig.s, point.curve.n - 2, point.curve.n)
    u = z * s_inv % point.curve.n
    v = sig.r * s_inv % point.curve.n
    total = u * point.curve.G + v * point
    return total.x == sig.r
