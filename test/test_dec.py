import unittest
from ellipticCurve.otherUtils.key import *

from ellipticCurve.curve import (
     secp256k1,EllipticCurve, Point
)




CURVES = [EllipticCurve, Point]
PLAINTEXT = b"I am plaintext."



class ElGamalTestCase(unittest.TestCase):
    def test_secp256k1(self):
        p = secp256k1.G()
        p1 = p + p
        for i in range(0, 5):
            p1 = p1+p
        print(secp256k1.include(p1))

    def test_createPriv(self):
        plaintext = b"I am lzy."
        plaintext = len(plaintext).to_bytes(1, byteorder="big") + plaintext
        print(plaintext)
        pri_key, pub_key = gen_keypair(secp256k1)
        print("priv:", pri_key)
        print(secp256k1.include(pub_key))

    # def test_pub(self):

