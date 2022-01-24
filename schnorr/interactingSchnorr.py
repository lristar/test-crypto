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
    # create private key and publish key
    pri_key, pub_key = gen_keypair(secp256k1)
    # init Alice People
    al = AliceP(pri_key)
    # init Bob People
    bob = BobP(pub_key)
    # Alice create random r
    al.Create_r()
    # Alice use random r to create R (R = r*G)
    R = al.Create_R(secp256k1.G)
    # Alice send R to Bob
    bob.Get_R(R)
    # Bob create random c
    c = bob.Create_c()
    # Bob send c to Alice
    al.Get_c(c)
    # Alice create z through the use of which Bob create the random
    z = al.Create_z()
    # Bob verify
    return bob.Verify(secp256k1.G, z)


