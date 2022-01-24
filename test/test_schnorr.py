import unittest
from schnorr.interactingSchnorr import *
from schnorr.NoactingSchnorr import *


class SchnorrTestCase(unittest.TestCase):
    def test_firstSchnorr(self):
        self.assertTrue(Process())

    def test_noActingSchnorr(self):
        self.assertTrue(noActingProcess())

    
