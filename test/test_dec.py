import unittest
from ellipticCurve.otherUtils.key import *
from ellipticCurve.otherUtils.cipher import *
from ellipticCurve.curve import (
    EllipticCurve
)




CURVES = [EllipticCurve, Point]
PLAINTEXT = b"I am lzy"



class ElGamalTestCase(unittest.TestCase):
    def test_secp256k1(self):
        p = secp256k1.G
        print("px", p.x,"py", p.y)
        p1 = 15 * p
        print("x:", p1.x, "y:", p1.y)
        print(secp256k1.is_on_curve(p1))

    def test_plantext(self):
        pri_key, pub_key = gen_keypair(secp256k1)
        print("priv:", pri_key, "pub_key", pub_key)
        print("is include",secp256k1.is_on_curve(pub_key))
        cipher_elg = ElGamal(secp256k1)
        print("cipher_elg_x",cipher_elg.curve.x,"cipher_elg_y",cipher_elg.curve.y)
        c1, c2 = cipher_elg.encrypt(PLAINTEXT, pub_key)
        plaintext = cipher_elg.decrypt(pri_key, c1, c2)
        self.assertEqual(plaintext, PLAINTEXT)
        print(plaintext)

    def test_pub(self):
        print(10 * secp256k1.G)

