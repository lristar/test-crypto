# Version 版本
# Input 输入
# OutPut 输出
# Locktime 时间锁
from dataclasses import dataclass
from script import Script
from exchange import *
import hashlib


@dataclass
class Tx:
    def __init__(self, version, tx_ins, tx_outs, lockTime, testnet=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.lockTime = lockTime

    def __repr__(self):
        tx_ins = ''
        tx_outs = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {} \nversion: {}\,tx_ins: {}\n tx_outs:{}\nlocktime:{}'.format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.lockTime
        )

    def id(self):
        return self.hash().hex()

    def hash(self):
        return hashlib.sha256(self.serialize())[::-1]

    def serialize(self):
        pass

    @classmethod
    def parse(cls, stream):
        serialized_version = cls.int_to_little_endian(stream.read(4))
        # serialized_version = stream.read(4)
        return Tx(serialized_version, None, None, None, testnet=True)

    @staticmethod
    def little_endian_to_int(b):
        return int.from_bytes(b, 'little')

    @staticmethod
    def int_to_little_endian(n: int , length: int):
        return n.to_bytes(length, 'little')


class TxIn:
    def __init__(self,prev_tx,prev_index,script_sig=None,sequence=0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence

    def __repr__(self):
        return '{}:{}'.format(self.prev_tx.hex(), self.prev_index)

