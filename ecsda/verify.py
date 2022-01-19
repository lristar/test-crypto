from ecsda.sign import signaTrue
from ellipticCurve.mathUtils.quickMod import *
from ellipticCurve.curve.curve import *


def vertify(point: Point, z, sig: signaTrue,pub):
    inverse_s = quickM(sig.s, point.curve.n - 2, point.curve.n)  # 对s求逆
    # Solve for the random point
    a = point.curve.G * (z * (inverse_s % point.curve.n))  # elliptic_multiply()为乘法
    b = pub * (sig.r * (inverse_s % point.curve.n))  # 公钥验证
    recovered_random_point = a + b
    return recovered_random_point.x == sig.r
