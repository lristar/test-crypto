from ellipticCurve.curve.EllipticCurve import *
from ellipticCurve.curve.curve import Point
from ellipticCurve.otherUtils.key import *
import random
import hashlib


class AliceP:
    def __init__(self, pri, pub, r=None):
        self.pri = pri
        self.pub = pub
        self.r = r

    def Create_r(self):
        r = random.randint(0, 99)
        self.r = r

    def Create_z(self, G: Point) -> Tuple[Point, int]:
        R = self.r * G
        c = (R + self.pub).x
        z = self.r + c * self.pri
        return R, z


class BobP:
    def __init__(self, pub: Point, c=None, R: Point = None, z=None):
        self.pub = pub
        self.c = c
        self.R = R
        self.z = z

    def Get_R(self, R: Point, z):
        self.R = R
        self.z = z

    def Create_c(self):
        c = (self.R + self.pub).x
        self.c = c

    def Verify(self, G: Point):
        return self.z * G == self.R + (self.c * self.pub)


def noActingProcess():
    pri_key, pub_key = gen_keypair(secp256k1)
    al = AliceP(pri_key, pub_key)
    al.Create_r()
    R, z = al.Create_z(secp256k1.G)
    bob = BobP(pub_key)
    bob.Get_R(R, z)
    bob.Create_c()
    return bob.Verify(secp256k1.G)


if __name__ == '__main__':
    noActingProcess()