import sympy
from sympy import *


##极限 x->0
def limit1():
    x = sympy.Symbol('x')  ## init unknown number
    print(limit(sin(x) / x, x, 0))


def serval():
    x = sympy.Symbol('x')
    return cos(x).series(x, 0, 10)


if __name__ == '__main__':
    limit1()
    print(serval())
