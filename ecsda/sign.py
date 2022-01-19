from dataclasses import dataclass
from ellipticCurve.curve.curve import *
import secrets
from hashlib import sha256

@dataclass
class signaTrue:
    def __init__(self, r, s):
        self.r = r
        self.s = s


@dataclass
class sign:
    curve: "Curve"

    def create_Sign(self, message, priv):
        z = self.get_Message(message)
        k = 0  # 产生一个0到P的随机数，其中randbelow()为secrets包的内置函数
        while k == 0:
            k = secrets.randbelow(5)
        r = (self.curve.G * k).x
        k_inv = quickMod.quickM(k, self.curve.p - 2, self.curve.p)
        s = (z + r * priv) * k_inv % self.curve.p
        if s > self.curve.p/2:
            s = self.curve.p - s
        return signaTrue(r, s)

    def GetK(self):
        k = 0  # 产生一个0到P的随机数，其中randbelow()为secrets包的内置函数
        while k == 0:
            k = secrets.randbelow(5)
        return k

    def get_Message(self,message):
        hashed_message = sha256(message.encode('utf-8')).hexdigest()
        hashed_message = sha256(hashed_message.encode('utf-8')).hexdigest()  # 双重哈希对消息进行加密
        return int(hashed_message, 20)




