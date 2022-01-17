from os import urandom

from ellipticCurve.mathUtils import quickMod,mod_sqrt,mod_inverse, utils


class Point:
    def __init__(self, x, y, curve):
        self.G_x = x
        self.G_y = y
        self.curve = curve

    def __add__(self, other):
        if self.G_x == other.G_x and (self.G_x + other.G_y) % self.curve.p == 0:
            return self.__class__(0, 0, self.curve)
        if self.G_x == 0 and self.G_y == 0:
            return other
        if self.G_x != other.G_x or self.G_y != other.G_y:
            k = self.modAll((self.G_y - other.G_y), (self.G_x - other.G_x), self.curve.p)
        else:
            k = self.modAll((3 * (self.G_x ** 2) + self.curve.a), 2 * self.G_y, self.curve.p)
        x3 = (k ** 2 - (self.G_x + other.G_x)) % self.curve.p
        y3 = ((k * (self.G_x - x3)) - self.G_y) % self.curve.p
        return self.__class__(x3, y3, self.curve)

    def __neg__(self):
        return self.curve.neg_point(self)

    def multi(self,  d: int):
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
        return self.G_x is None and self.G_y is None

    def modAll(self, x, y, m):
        if x % y != 0:
            return x % m * quickMod.quickMod(y, m - 2, m)
        return (x / y) % m





class EllipticCurve:
    def __init__(self, a, b, p, n, G_x, G_y):
        self.a = a
        self.b = b
        self.p = p
        self.n = n
        self.G_x = G_x
        self.G_y = G_y


    def G(self):
        return Point(self.G_x, self.G_y, self)

    def INF(self):
        return Point(None, None, self)


    def include(self, point):
        if (point.G_y ** 2) % self.p == ((point.G_x ** 3) + (self.a * point.G_x) + self.b) % self.p:
            return True
        return False

    def is_on_curve(self, P: Point) -> bool:
        if P.curve != self:
            return False
        return P.is_at_infinity() or self.include(P)

    def neg_point(self, P: Point) -> Point:
        if not self.is_on_curve(P):
            raise ValueError("The point is not on the curve.")
        if P.is_at_infinity():
            return self.INF()
        return self._neg_point(P)

    def encode_point(self, plaintext: bytes):
        plaintext = len(plaintext).to_bytes(1, byteorder="big") + plaintext
        while True:
            x = int.from_bytes(plaintext, "big")
            y = self.compute_y(x)
            if y:
                return Point(x, y, self)
            plaintext += urandom(1)

    def decode_point(self, M: Point) -> bytes:
        byte_len = utils.int_length_in_byte(M.G_x)
        print("byte_len", byte_len)
        plaintext_len = (M.G_x >> ((byte_len - 1) * 8)) & 0xff
        print("plaintext_len", plaintext_len)
        plaintext = ((M.G_x >> ((byte_len - plaintext_len - 1) * 8))
                     & (int.from_bytes(b"\xff" * plaintext_len, "big")))
        return plaintext.to_bytes(plaintext_len, byteorder="big")

    def _neg_point(self, P: Point) -> Point:
        return Point(P.G_x, -P.G_y % self.p, self)

    def compute_y(self, x: int) -> int:
        right = self.a * x * x - 1
        left_scale = (self.b * x * x - 1) % self.p
        inv_scale = mod_inverse.modinv(left_scale, self.p)
        right = (right * inv_scale) % self.p
        y = mod_sqrt.modsqrt(right, self.p)
        return y

    def double_point(self, P: Point):
        if not self.is_on_curve(P):
            raise ValueError("The point is not on the curve.")
        if P.is_at_infinity():
            return self.INF

        return self._double_point(P)

    def _double_point(self, P):
        s = (3 * P.G_x * P.G_x + self.a) * mod_inverse.modinv(2 * P.G_y, self.p)
        res_x = (s * s - 2 * P.G_x) % self.p
        res_y = (P.G_y + s * (res_x - P.G_x)) % self.p
        return - Point(res_x, res_y, self)


secp256k1 = EllipticCurve(
    a=0,
    b=7,
    p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
    n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141,
    G_x=0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    G_y=0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)
