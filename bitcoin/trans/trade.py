# Version 版本
# Input 输入
# OutPut 输出
# Locktime 时间锁
from dataclasses import dataclass
from exchange import *
import hashlib
from bitcoin.scripts.transaction_scripts import *


class TxIn:
    def __init__(self, prev_tx, prev_index, script_sig: Script = None, sequence=0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence

    def __repr__(self):
        return '{}:{}'.format(self.prev_tx.hex(), self.prev_index)

    # 类方法（不需要实例化类就可以被类本身调用）
    @classmethod
    def parse(cls, s):
        prev_tx = s.read(32)[::-1]
        prev_index = little_endian_to_int(s.read(4))
        script_sig = Script.parse(s)
        sequence = little_endian_to_int(s.read(4))
        return cls(prev_tx, prev_index, script_sig, sequence)

    def serialize(self):
        result = self.prev_tx[::-1]
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result


class TxOut:
    def __init__(self, amount, script_pubkey: Script):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)

    @classmethod
    def parse(cls, s):
        amount = little_endian_to_int(s.read(8))
        script_pubkey = Script.parse(s)
        return cls(amount, script_pubkey)

    def serialize(self):
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result



@dataclass
class Tx:
    def __init__(self, version, tx_ins: [], tx_outs: [], lockTime, testnet=False):
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
        result = int_to_little_endian(self.version, 4)
        result += encode_varInt(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_varInt(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        result += int_to_little_endian(self.lockTime, 4)
        return result

    @classmethod
    def parse(cls, stream):
        serialized_version = cls.little_endian_to_int(stream.read(4))
        num_inputs = read_varInt(stream)

        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(num_inputs))
        # serialized_version = stream.read(4)
        num_outs = read_varInt(stream)

        outs = []
        for _ in range(num_outs):
            outs.append(TxOut.parse(num_outs))

        time_lock = little_endian_to_int(stream.read(4))
        return Tx(serialized_version, inputs, outs, time_lock, testnet=True)

    @staticmethod
    def little_endian_to_int(b):
        return int.from_bytes(b, 'little')

    @staticmethod
    def int_to_little_endian(n: int, length: int):
        return n.to_bytes(length, 'little')
