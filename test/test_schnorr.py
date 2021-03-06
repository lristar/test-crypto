import unittest
from schnorr.interactingSchnorr import *
from schnorr.NoactingSchnorr import *
from schnorr.aggregateSchnorr import *
from schnorr.NoactingSchnorr_better import *

class SchnorrTestCase(unittest.TestCase):
    def test_firstSchnorr(self):
        self.assertTrue(Process())

    def test_noActingSchnorr(self):
        self.assertTrue(noActingProcess())

    def test_noActingSchnorrBetter(self):
        self.assertTrue(noActingProcessBetter())

    def test_aggregateSchnorr(self):
        self.assertTrue(aggregateProcess())
