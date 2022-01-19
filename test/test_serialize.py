import unittest

from serialize.key import other_gen_keypair
from ellipticCurve.curve.EllipticCurve import *


class SerializeTestCase(unittest.TestCase):
    def test_Sectool(self):
        pri_key, pub_key = other_gen_keypair(secp256k1, 2018 ** 5)
        print(pub_key.sec().hex())

    def test_SecFormat(self):
        pri_key, pub_key = other_gen_keypair(secp256k1, 2018 ** 5)
        print(pub_key.depSec().hex())

