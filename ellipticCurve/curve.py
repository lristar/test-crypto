from cryptos import *

from ellipticCurve.mathUtils.quickMod import *


class EllipticCurve:
    def __init__(self, a, b, p, n, G_x, G_y):
        self.a = a
        self.b = b
        self.p = p
        self.n = n
        self.G_x = G_x
        self.G_y = G_y

    @property
    def G(self):
        return Point(self.G_x, self.G_y, self)

    def include(self, point):
        if (point.G_y ** 2) % self.p == ((point.G_x ** 3) + (self.a * point.G_x) + self.b) % self.p:
            return True
        return False


class Point:
    def __init__(self, x, y, curve):
        self.G_x = x
        self.G_y = y
        self.curve = curve

    def __add__(self, other):
        if self.G_x == other.G_x and (self.G_x + other.y) % self.curve.p == 0:
            return self.__class__(0, 0, self.curve)
        if self.G_x == 0 and self.G_y == 0:
            return other
        if self.G_x != other.G_x or self.G_y != other.y:
            k = self.modAll((self.G_y - other.G_y), (self.G_x - other.G_x), self.curve.p)
        else:
            k = self.modAll((3 * (self.G_x ** 2) + self.curve.a), 2 * self.G_y, self.curve.p)
        x3 = (k ** 2 - (self.G_x + other.G_x)) % self.curve.p
        y3 = ((k * (self.G_x - x3)) - self.G_y) % self.curve.p
        return self.__class__(x3, y3, self.curve)

    def modAll(self, x, y, m):
        if x % y != 0:
            return x % m * quickMod(y, m - 2, m)
        return (x / y) % m


secp256k1 = EllipticCurve(
    a=0,
    b=7,
    p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
    n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141,
    G_x=0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    G_y=0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)
