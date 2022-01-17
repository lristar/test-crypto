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

    def point(self, x, y):
        return Point(x, y, self.a, self.b, self.p)

    @staticmethod
    def include(point):
        if (point.y ** 2) % point.p == ((point.x ** 3) + (point.a * point.x) + point.b) % point.p:
            return True
        return False


class Point:
    def __init__(self, x, y, a, b, p):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.p = p

    def __add__(self, other):
        if self.x == other.x and (self.y + other.y) % self.p == 0:
            return self.__class__(0, 0, self.a, self.b, self.p)
        if self.x == 0 and self.y == 0:
            return other
        if self.x != other.x or self.y != other.y:
            k = self.modAll((self.y - other.y), (self.x - other.x), self.p)
        else:
            k = self.modAll((3 * (self.x ** 2) + self.a), 2 * self.y, self.p)
        x3 = (k ** 2 - (self.x + other.x)) % self.p
        y3 = ((k * (self.x - x3)) - self.y) % self.p
        return self.__class__(x3, y3, self.a, self.b, self.p)

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

