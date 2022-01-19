from ellipticCurve.curve.curve import *
from ellipticCurve.mathUtils import mod_sqrt,mod_inverse


class EllipticCurve(Curve):
    def _is_on_curve(self, P: Point) -> bool:
        left = P.y * P.y
        right = (P.x * P.x * P.x) + (self.a * P.x) + self.b
        return (right - left) % self.p == 0

    def _add_point(self, P: Point, Q: Point) -> Point:
        x3 = P.x - Q.x
        y3 = P.y - Q.y
        k = y3 * mod_inverse.modinv(x3, self.p)
        res_x = (k * k - P.x - Q.x) % self.p
        res_y = (P.y + k * (res_x - P.x)) % self.p
        return - Point(res_x, res_y, self)

    def _double_point(self, P: Point) -> Point:
        k = (3 * P.x * P.x + self.a) * mod_inverse.modinv(2 * P.y, self.p)
        res_x = (k * k - 2 * P.x) % self.p
        res_y = (P.y + k * (res_x - P.x)) % self.p
        return - Point(res_x, res_y, self)

    def _neg_point(self, P: Point) -> Point:
        return Point(P.x, -P.y % self.p, self)

    def compute_y(self, x) -> int:
        right = (x * x * x + self.a * x + self.b) % self.p
        y = mod_sqrt.modsqrt(right, self.p)
        return y


secp256k1 = EllipticCurve(
    a=0,
    b=7,
    p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
    n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141,
    x=0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    y=0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)