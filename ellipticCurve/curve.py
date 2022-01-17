from os import urandom

from ellipticCurve.mathUtils import quickMod,mod_sqrt ,mod_inverse, utils




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

    def include(self, point):
        if (point.G_y ** 2) % self.p == ((point.G_x ** 3) + (self.a * point.G_x) + self.b) % self.p:
            return True
        return False


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
            d >>= 1
        return data

    def INF(self):
        return Point(None, None, self)

    def modAll(self, x, y, m):
        if x % y != 0:


            return x % m * quickMod.quickMod(y, m - 2, m)
        return (x / y) % m

    def encode_point(self, plaintext: bytes):
        plaintext = len(plaintext).to_bytes(1, byteorder="big") + plaintext
        while True:
            x = int.from_bytes(plaintext, "big")
            y = self.compute_y(x)
            if y:
                return Point(x, y, self)
            plaintext += urandom(1)

    def decode_point(self, M) -> bytes:
        byte_len = utils.int_length_in_byte(M.x)
        plaintext_len = (M.x >> ((byte_len - 1) * 8)) & 0xff
        plaintext = ((M.x >> ((byte_len - plaintext_len - 1) * 8))
                     & (int.from_bytes(b"\xff" * plaintext_len, "big")))
        return plaintext.to_bytes(plaintext_len, byteorder="big")

    def compute_y(self, x: int) -> int:
        right = self.curve.a * x * x - 1
        left_scale = (self.curve.b * x * x - 1) % self.curve.p
        inv_scale = mod_inverse.modinv(left_scale, self.curve.p)
        right = (right * inv_scale) % self.curve.p
        y = mod_sqrt.modsqrt(right, self.curve.p)
        return y

secp256k1 = EllipticCurve(
    a=0,
    b=7,
    p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
    n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141,
    G_x=0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    G_y=0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)
