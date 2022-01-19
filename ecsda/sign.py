from dataclasses import dataclass
from ellipticCurve.curve.curve import *
from ellipticCurve.mathUtils.quickMod import *
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
        k = 0
        while k == 0:
            k = secrets.randbelow(self.curve.n)
        random_point = self.curve.G * k  # 随机数*基点
        rx = random_point.x % self.curve.n
        signature_proof = quickM(k, self.curve.n - 2, self.curve.n) * (z + rx * priv) % self.curve.n
        return signaTrue(rx, signature_proof)

    def GetK(self):
        k = 0  # 产生一个0到P的随机数，其中randbelow()为secrets包的内置函数
        while k == 0:
            k = secrets.randbelow(self.curve.n)
        return k

    def get_Message(self,message):
        hashed_message = sha256(message.encode('utf-8')).hexdigest()
        hashed_message = sha256(hashed_message.encode('utf-8')).hexdigest()  # 双重哈希对消息进行加密
        return int(hashed_message, 20)




