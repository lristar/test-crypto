import functools

import numpy as np
from sklearn.preprocessing import PolynomialFeatures  # 这哥用于生成多项式


class Verifier:
    def __init__(self, func):
        self.rangV = np.poly1d(func)
        self.func = func

    def initProver(self, w):
        p = self.rangV(w)
        proverFunc = self.func
        proverFunc[len(self.func) - 1] = self.func[len(self.func) - 1] - p
        return Prover(proverFunc)

    def Door(self, x, y):
        w = x & y
        return ~w


class Prover:
    def __init__(self, func):
        self.rangP = np.poly1d(func)

    def proveValue(self, t):
        return self.rangP(t)


## use bin
def change(x, n):
    a = bin(x)
    num = a[2:]
    if len(num) > n:
        num = num[len(num) - n:]
    l = len(num)
    t = 0
    for i in num:
        t = t + (2 ** (l - 1)) * int(i)
        l = l - 1
    return t - x


if __name__ == '__main__':
    v = Verifier([1, -4, 3])
    p = v.initProver(10)
    print(p.proveValue(100))
    print(v.Door(10, 15))
