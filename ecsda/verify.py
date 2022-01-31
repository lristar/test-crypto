from ecsda.sign import signaTrue
from ellipticCurve.mathUtils.quickMod import *
from ellipticCurve.curve.curve import *


def vertify(pub: Point, z, sig: signaTrue):
    inverse_s = quickM(sig.s, pub.curve.n - 2, pub.curve.n)  # 对s求逆
    # Solve for the random pub
    a = pub.curve.G * (z * (inverse_s % pub.curve.n))
    b = pub * (sig.r * (inverse_s % pub.curve.n))  # 公钥验证
    recovered_random_pub = a + b
    return recovered_random_pub.x == sig.r
