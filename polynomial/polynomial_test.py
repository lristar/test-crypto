import numpy as np
from sklearn.preprocessing import PolynomialFeatures  # 这哥用于生成多项式


class Multi:
    def __init__(self, rag, func):
        self.range = rag
        self.func = func

    def isrange(self,x):
        if x < 2**10:
            return True


## use bin
def change(x, n):
    a = bin(x)
    num = a[2:]
    if len(num) > n:
        num = num[len(num)-n:]
    l = len(num)
    t =0
    for i in num:
        t = t + (2**(l-1))*int(i)
        l = l-1
    return t-x


if __name__ == '__main__':
    # p = np.poly1d([1, -4, 3])  # 系数数组，没有出现的系数项用0补齐
    # f = np.poly1d(p)
    print(2**15)  # 输出多项式f的数学表达式
    print("x:", change(1023, 10))
