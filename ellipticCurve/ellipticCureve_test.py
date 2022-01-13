import time


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
        if self.x == other.x and (self.y+other.y) % self.p==0:
            return self.__class__(0, 0, self.a, self.b, self.p)
        if self.x == 0 and self.y == 0:
            return other
        if self.x != other.x or self.y != other.y:
            k = self.modAll((self.y - other.y),(self.x - other.x),self.p)
        else:
            k = self.modAll((3*(self.x**2)+self.a), 2*self.y, self.p)
        x3 = (k ** 2 - (self.x + other.x)) % self.p
        y3 = ((k * (self.x - x3)) - self.y) % self.p
        return self.__class__(x3, y3, self.a, self.b, self.p)

    def modAll(self, x, y, m):
        if y == 0:
            return 0
        if x % y != 0:
            return (x*(y**(m-2))) % m
        else:
            return (x/y) % m

def main():
     a = EllipticCurve(8, 7, 73)
     p1 = a.point(32, 53)
     p2 = a.point(32, 53)
     for i in range(1, 15):
         p1 = p1 + p2
         print("x=", p1.x, "y=", p1.y, "a=", p1.a, "b=", p1.b, "p", p1.p)



if __name__ == '__main__':
    main()
