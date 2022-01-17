import unittest

from ellipticCurve.ellipticCureve_test import (
     EllipticCurve, Point,secp256k1
)
from ellipticCurve.otherUtils.key import *



CURVES = [EllipticCurve, Point]
PLAINTEXT = b"I am plaintext."



class ElGamalTestCase(unittest.TestCase):
    def test_encrypt(self):
        x = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
        y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
        p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
        a = EllipticCurve(0, 7, p)
        p1 = a.G(x, y)
        a.include(p1)
        plaintext = b"I am lzy."
        plaintext = len(plaintext).to_bytes(1, byteorder="big") + plaintext
        print(plaintext)
        gen_()
    def test_createPriv(self):
        pri_key, pub_key = gen_keypair(secp256k1)
        print("priv:",pri_key)
        print("pub:",pub_key)
