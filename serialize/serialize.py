from ellipticCurve.curve.curve import Point


def sec(self):
    return b'\x04' + self.x.to_bytes(32, 'big') + self.y.to_bytes(32, 'big')


def depSec(point: Point, compressed=True):
    if compressed:
        if point.y % 2 == 0:
            return b'\x02' + point.x.to_bytes(32, 'big')
        else:
            return b'\x03' + point.x.to_bytes(32, 'big')
    return b'\x04' + point.x.to_bytes(32, 'big') + point.y.to_bytes(32, 'big')


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
