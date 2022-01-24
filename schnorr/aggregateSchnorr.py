from ellipticCurve.curve.EllipticCurve import *
from ellipticCurve.curve.curve import Point
from ellipticCurve.otherUtils.key import *
import random
import hashlib
from hashlib import sha256

PLAINTEXT = "I am lzy"


def double_hash(message):
    hashed_message = sha256(message.encode('utf-8')).hexdigest()
    hashed_message = sha256(hashed_message.encode('utf-8')).hexdigest()  # 双重哈希对消息进行加密
    return int(hashed_message, 20)


class Alice:
    def __init__(self, pri, m, r=None):
        self.pri = pri
        self.r = r
        self.m = double_hash(m)

    def Create_r(self):
        r = random.randint(0, 99)
        self.r = r


class MidTreatment:
    def __init__(self, a: Alice, b: Alice):
        self.a = a
        self.b = b

    def CreateC_Z(self, G: Point) -> Tuple[int, int]:
        c = (self.a.m * ((self.a.r * G) + (self.b.r * G))).x
        z = (self.a.r + self.b.r) + (c * (self.a.pri + self.b.pri))
        return c, z


class Bob:
    def __init__(self, pub: Point, m, c=None, z=None):
        self.pub = pub
        self.c = c
        self.z = z
        self.m = double_hash(m)

    def Verify(self, G: Point):
        R = self.z * G - (self.c * self.pub)
        c2 = (self.m * R).x
        return c2 == self.c


def aggregateProcess() -> bool:
    p1, p2, pub_key = gen_share_keypair(secp256k1)
    al1 = Alice(p1, PLAINTEXT)
    al2 = Alice(p2, PLAINTEXT)
    al1.Create_r()
    al2.Create_r()
    mid = MidTreatment(al1, al2)
    c, z = mid.CreateC_Z(secp256k1.G)
    bob = Bob(pub_key, PLAINTEXT, c=c, z=z)
    return bob.Verify(secp256k1.G)


if __name__ == '__main__':
    aggregateProcess()
