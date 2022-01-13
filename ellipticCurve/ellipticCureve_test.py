class EllipticCurve:
    def __init__(self, a, b,p):
        self.a = a
        self.b = b
        self.p = p

    def point(self, x, y):
        return Point(x, y, self.a, self.b, self.p)


class Point:
    def __init__(self, x, y, a, b, p):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.p = p

    def __add__(self, other):
        if self.x != other.x or self.y != other.y:
            k = self.modall((self.y - other.y),(self.x - other.x),self.p)
        else:
            k = self.modall((3*(self.x**2)+self.a), 2*self.y, self.p)
        x3 = (k ** 2 - (self.x + other.x)) % self.p
        y3 = (k * (self.x - x3)) % self.p
        return self.__class__(x3, y3, self.a, self.b, self.p)

    def modall(self, x, y, m):
        if x % y != 0:
            i = 1
            while (i * y) % m != x:
                i = i + 1
            return i
        else:
            return (x/y)% m

def main():
     a = EllipticCurve(2, 3, 97)
     p1 = a.point(3, 6)
     p2 = a.point(3, 6)
     for i in range(1,15):
         p1 = p1 + p2
         print("x=", p1.x, "y=", p1.y, "a=", p1.a, "b=", p1.b, "p", p1.p)



if __name__ == '__main__':
    main()
