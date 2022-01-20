import unittest

from serialize.key import other_gen_keypair
from ellipticCurve.curve.EllipticCurve import *
from ellipticCurve.otherUtils.key import *
from ecsda.sign import sign
from serialize.serialize import *

PLAINTEXT = "I am lzy"


class SerializeTestCase(unittest.TestCase):
    def test_Sectool(self):
        pri_key, pub_key = other_gen_keypair(secp256k1, 2018 ** 5)
        print(pub_key.sec().hex())

    def test_SecFormat(self):
        pri_key, pub_key = other_gen_keypair(secp256k1, 2018 ** 5)
        print(pub_key.depSec().hex())

    #  压缩公钥后再解析回来
    def test_compressed(self):
        pri_key, pub_key = other_gen_keypair(secp256k1, 2018 ** 5)
        ya = pub_key.depSec()
        p = pub_key.parse(ya)
        assert pub_key == p

    def test_der(self):
        pri_key, pub_key = gen_keypair(secp256k1)
        s = sign(secp256k1)
        print("pub_key:",pub_key)
        signs = s.create_Sign(PLAINTEXT, pri_key)
        s = signaTrue(signs.r, signs.s)
        # Todo   decode der
        result = s.der()
        s.decParse(result)
