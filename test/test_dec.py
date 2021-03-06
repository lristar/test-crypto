import unittest
from ellipticCurve.otherUtils.key import *
from ellipticCurve.otherUtils.cipher import *
from ecsda.sign import *
from ecsda.verify import *
from ellipticCurve.curve import (
    EllipticCurve
)

CURVES = [EllipticCurve, Point]
PLAINTEXT = "message"
PLAINTEXT1 = b'message'


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
        c1, c2 = cipher_elg.encrypt(PLAINTEXT1, pub_key)
        plaintext = cipher_elg.decrypt(pri_key, c1, c2)
        self.assertEqual(plaintext, PLAINTEXT1)
        print(plaintext)
        
    def test_myecdsa(self):
        pri_key, pub_key = gen_keypair(secp256k1)
        s = sign(secp256k1)
        signs = s.create_Sign(PLAINTEXT,pri_key)
        z = s.get_Message(PLAINTEXT)
        assert vertify(pub_key, z, signs)
