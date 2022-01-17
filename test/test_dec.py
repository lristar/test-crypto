import unittest
from ellipticCurve.otherUtils.key import *
from ellipticCurve.cipher import *
from ellipticCurve.curve import (
     secp256k1,EllipticCurve, Point
)




CURVES = [EllipticCurve, Point]
PLAINTEXT = b"I am lzy"



class ElGamalTestCase(unittest.TestCase):
    def test_secp256k1(self):
        p = secp256k1.G()
        p1 = p + p
        for i in range(0, 5):
            p1 = p1+p
        print(secp256k1.include(p1))

    def test_createPriv(self):
        pri_key, pub_key = gen_keypair(secp256k1)
        print("priv:", pri_key, "pub_key", pub_key)
        cipher_elg = ElGamal(secp256k1)
        c1, c2 = cipher_elg.encrypt(PLAINTEXT, pub_key)
        plaintext = cipher_elg.decrypt(pri_key, c1, c2)
        self.assertEqual(plaintext, PLAINTEXT)

    # def test_pub(self):

