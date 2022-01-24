from ellipticCurve.curve.EllipticCurve import *
from ellipticCurve.curve.curve import Point
from ellipticCurve.otherUtils.key import *
import random


class AliceP:
    def __init__(self, pri, r=None, c=None):
        self.pri = pri
        self.r = r
        self.c = c

    def Create_r(self):
        r = random.randint(0, 99)
        self.r = r

    def Create_R(self, G: Point):
        return self.r * G

    def Get_c(self, c):
        self.c = c

    def Create_z(self):
        return self.r + self.c * self.pri


class BobP:
    def __init__(self, pub, c=None, R: Point = None):
        self.pub = pub
        self.c = c
        self.R = R

    def Get_R(self, R):
        self.R = R

    def Create_c(self):
        c = random.randint(0, 99)
        self.c = c
        return c

    def Verify(self, G: Point, z):
        return z * G == self.R + self.c * self.pub


def Process():
    pri_key, pub_key = gen_keypair(secp256k1)
    al = AliceP(pri_key)
    bob = BobP(pub_key)
    al.Create_r()
    R = al.Create_R(secp256k1.G)
    bob.Get_R(R)
    c = bob.Create_c()
    al.Get_c(c)
    z = al.Create_z()
    return bob.Verify(secp256k1.G, z)


