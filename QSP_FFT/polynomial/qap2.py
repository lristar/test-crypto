import numpy as np
from scipy.interpolate import lagrange

'''
S=[~one, ~out, C5, C4, C3, C2, C1]
C1*C2=C4
(C1+C3)*~one=C5
C4*C5=~out
'''


def main():
    S = [1, 7, 7, 1, 6, 1, 1]
    A = np.array([[0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 1, 0, 0, 0]])
    B = np.array([[0, 0, 0, 0, 0, 1, 0], [1, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0]])
    C = np.array([[0, 0, 0, 1, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0]])
    print("MatrixA:\n", A)
    print("MatrixB:\n", B)
    print("MatrixC:\n", C)
    X = [3, 2, 1]
    print("X:\n", X)
    Axs = []
    Bxs = []
    Cxs = []
    # lagrange 利用拉格朗日插值法查找多个点生成的多项式
    for i in range(0, 7):
        Axs.append(lagrange(X, A[:, i]))
        Bxs.append(lagrange(X, B[:, i]))
        Cxs.append(lagrange(X, C[:, i]))

    Ax = 0
    Bx = 0
    Cx = 0
    print("Axs:", Axs)
    print("Bxs:", Bxs)
    print("Cxs:", Cxs)
    for i in range(0, 7):
        Ax = Ax + S[i] * Axs[i]
        Bx = Bx + S[i] * Bxs[i]
        Cx = Cx + S[i] * Cxs[i]

    print("Matrix A Polynomial \n", Axs)
    print("Ax=\n", Ax)
    print("Matrix B Polynomial \n", Bxs)
    print("Bx=\n", Bx)
    print("Matrix C Polynomial \n", Cxs)
    print("Cx=\n", Cx)
    Px = np.polymul(Ax, Bx) - Cx
    Tx = np.poly1d(np.array([1, -1])) * np.poly1d(np.array([1, -2])) * np.poly1d(np.array([1, -3]))
    Hx, Rx = np.polydiv(Px, Tx)
    print("Px:\n", Px)
    print("Px(1)", np.polyval(Px, 1))
    print("Px(2)", np.polyval(Px, 2))
    print("Px(3)", np.polyval(Px, 3))
    # 得到的除数
    print("Tx:\n", Tx)
    # 得到的数的多项式
    print("Hx:\n", Hx)
    # 余数
    print("Rx:\n", Rx)


if __name__ == '__main__':
    main()
