from ellipticCurve.mathUtils import utils
from typing import Optional
from os import urandom
from abc import ABC, abstractmethod
from dataclasses import dataclass


# 装饰器可以帮你生成 __repr__ __init__ 等等方法
@dataclass
class Point:
    x: Optional[int]
    y: Optional[int]
    curve: "Curve"
    # def __add__(self, other):
    #     if self.x == other.x and (self.x + other.y) % self.curve.p == 0:
    #         return self.__class__(0, 0, self.curve)
    #     if self.x == 0 and self.y == 0:
    #         return other
    #     if self.x != other.x or self.y != other.y:
    #         k = self.modAll((self.y - other.y), (self.x - other.x), self.curve.p)
    #     else:
    #         k = self.modAll((3 * (self.x ** 2) + self.curve.a), 2 * self.y, self.curve.p)
    #     x3 = (k ** 2 - (self.x + other.x)) % self.curve.p
    #     y3 = ((k * (self.x - x3)) - self.y) % self.curve.p
    #     return self.__class__(x3, y3, self.curve)

    def __neg__(self):
        return self.curve.neg_point(self)

    def __eq__(self, other):
        return self.curve == other.curve and self.x == other.x and self.y == other.y

    def __add__(self, other):
        return self.curve.add_point(self, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        negative = - other
        return self.__add__(negative)

    def __mul__(self, scalar: int):
        return self.curve.mul_point(scalar, self)

    def __rmul__(self, scalar: int):
        return self.__mul__(scalar)

    def multi(self, d: int):
        """
        https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication
        """
        if d == 1:
            return self
        res = None
        is_negative_scalar = d < 0
        d = -d if is_negative_scalar else d
        data = self
        while d:
            if d & 0x1 == 1:
                if res:
                    res = data + self
                else:
                    res = data
            data = self.curve.double_point(self)
            d >>= 1
        return res

    def is_at_infinity(self) -> bool:
        return self.x is None and self.y is None

    def sec(self):
        return b'\x04' + self.x.to_bytes(32, 'big') + self.y.to_bytes(32, 'big')

    def depSec(self, compressed=True):
        if compressed:
            if self.y % 2 == 0:
                return b'\x02' + self.x.to_bytes(32, 'big')
            else:
                return b'\x03' + self.x.to_bytes(32, 'big')
        return b'\x04' + self.x.to_bytes(32, 'big') + self.y.to_bytes(32, 'big')

    def parse(self, sec_bin):
        if sec_bin[0] == 4:
            x = int.from_bytes(sec_bin[1:33], 'big')
            y = int.from_bytes(sec_bin[33:65], 'big')
            return Point(x, y, self.curve)
        is_even = sec_bin[0] == 2
        x = int.from_bytes(sec_bin[1:], 'big')
        beta = self.curve.sqrt(x)
        if beta % 2 == 0:
            even_beta = beta
            odd_beta = self.curve.p - beta
        else:
            even_beta = self.curve.p - beta
            odd_beta = beta
        if is_even:
            return Point(x, even_beta, self.curve)
        else:
            return Point(x, odd_beta, self.curve)

    def decParse(self, b: bytes):
        pass


@dataclass
class Curve(ABC):
    a: int
    b: int
    p: int
    n: int
    x: int
    y: int

    # def __str__(self):
    #     return

    # def __repr__(self):
    #     return self.__str__()

    def __eq__(self, other):
        return (
                self.a == other.a and self.b == other.b and self.p == other.p and
                self.n == other.n and self.x == other.x and self.y == other.y
        )

    # 修饰方法，是方法可以像属性一样访问
    @property
    def G(self):
        return Point(self.x, self.y, self)

    def getP(self, x, y):
        return Point(x, y, self)

    @property
    def INF(self) -> Point:
        return Point(None, None, self)

    def is_on_curve(self, P: Point) -> bool:
        if P.curve != self:
            return False
        return P.is_at_infinity() or self._is_on_curve(P)

    @abstractmethod
    def _is_on_curve(self, P: Point) -> bool:
        pass

    def add_point(self, P: Point, Q: Point) -> Point:
        if (not self.is_on_curve(P)) or (not self.is_on_curve(Q)):
            raise ValueError("The points are not on the curve.")
        if P.is_at_infinity():
            return Q
        elif Q.is_at_infinity():
            return P

        if P == Q:
            return self._double_point(P)
        if P == -Q:
            return self.INF

        return self._add_point(P, Q)

    @abstractmethod
    def _add_point(self, P: Point, Q: Point) -> Point:
        pass

    def double_point(self, P: Point) -> Point:
        if not self.is_on_curve(P):
            raise ValueError("The point is not on the curve.")
        if P.is_at_infinity():
            return self.INF

        return self._double_point(P)

    @abstractmethod
    def _double_point(self, P: Point) -> Point:
        pass

    def mul_point(self, d: int, P: Point) -> Point:
        if not self.is_on_curve(P):
            raise ValueError("The point is not on the curve.")
        if P.is_at_infinity():
            return self.INF
        if d == 0:
            return self.INF

        res = None
        is_negative_scalar = d < 0
        d = -d if is_negative_scalar else d
        tmp = P
        while d:
            if d & 0x1 == 1:
                if res:
                    res = self.add_point(res, tmp)
                else:
                    res = tmp
            tmp = self.double_point(tmp)
            d >>= 1
        if is_negative_scalar:
            return -res
        else:
            return res

    def neg_point(self, P: Point) -> Point:
        if not self.is_on_curve(P):
            raise ValueError("The point is not on the curve.")
        if P.is_at_infinity():
            return self.INF
        return self._neg_point(P)

    @abstractmethod
    def _neg_point(self, P: Point) -> Point:
        pass

    @abstractmethod
    def compute_y(self, x: int) -> int:
        pass

    def encode_point(self, plaintext: bytes) -> Point:
        plaintext = len(plaintext).to_bytes(1, byteorder="big") + plaintext
        while True:
            x = int.from_bytes(plaintext, "big")
            y = self.compute_y(x)
            if y:
                print("compute_y", y)
                return Point(x, y, self)
            plaintext += urandom(1)

    @staticmethod
    def decode_point(M: Point) -> bytes:
        byte_len = utils.int_length_in_byte(M.x)
        print("byte_len:", byte_len)
        plaintext_len = (M.x >> ((byte_len - 1) * 8)) & 0xff
        print("plaintext_len:", plaintext_len)
        plaintext = ((M.x >> ((byte_len - plaintext_len - 1) * 8))
                     & (int.from_bytes(b"\xff" * plaintext_len, "big")))
        return plaintext.to_bytes(plaintext_len, byteorder="big")

    def sqrt(self, x: int):
        return self.compute_y(x)
