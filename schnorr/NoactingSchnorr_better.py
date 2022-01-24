from ellipticCurve.curve.EllipticCurve import *
from ellipticCurve.curve.curve import Point
from ellipticCurve.otherUtils.key import *
import random
from hashlib import sha256

PLAINTEXT = "I am lzy"


def double_hash(message):
    hashed_message = sha256(message.encode('utf-8')).hexdigest()
    hashed_message = sha256(hashed_message.encode('utf-8')).hexdigest()  # 双重哈希对消息进行加密
    return int(hashed_message, 20)


class AliceP:
    def __init__(self, pri, m, r=None):
        self.pri = pri
        self.r = r
        self.m = double_hash(m)

    def Create_r(self):
        r = random.randint(0, 99)
        self.r = r

    def Create_C_Z(self, G: Point) -> Tuple[int, int]:
        c = (self.m * (self.r * G)).x
        z = self.r + c * self.pri
        return c, z


class BobP:
    def __init__(self, pub: Point, m, c=None, z=None):
        self.pub = pub
        self.c = c
        self.z = z
        self.m = double_hash(m)

    def Verify(self, G: Point):
        R = self.z * G - (self.c * self.pub)
        c2 = (self.m * R).x
        return c2 == self.c


def noActingProcessBetter() -> bool:
    pri_key, pub_key = gen_keypair(secp256k1)
    al = AliceP(pri_key, PLAINTEXT)
    al.Create_r()
    c, z = al.Create_C_Z(secp256k1.G)
    bob = BobP(pub_key, PLAINTEXT, c=c, z=z)
    return bob.Verify(secp256k1.G)


if __name__ == '__main__':
    noActingProcessBetter()
