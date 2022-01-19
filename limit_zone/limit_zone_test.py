class FieldElement:
    def __init__(self,num,prime):
        if num >= prime or num<0:
            error = 'Num {} not in field range 0 to {}'.format(num,prime-1)
            raise ValueError(error)
        self.num=num
        self.prime=prime

    def __repr__(self,):
        return 'FieldElement_{}({})'.format(self.prime,self.num)

## init equal
    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

## init no equal
    def __ne__(self, other):
        if other is None:
             return False
        return self.num != other.num or self.prime != other.prime

## init add
    def __add__(self, other):
        if other is None:
            return self
        self.jugdePrime(other)
        return (self.num+other.num) %self.prime

## init multipart
    def __mul__(self, other):
        if other is None:
            return None
        self.jugdePrime(other)
        self.num*other.num%self.prime
        return self.num*other.num%self.prime

## init pow
    def __pow__(self, power, modulo=None):
        p=power
        if p<0:
            p=power-1+self.prime
        return self.__class__(self.num**p%self.prime,self.prime)

## init v
    def __truediv__(self, other):
        return self.num*(other.num**(self.prime-2))%self.prime

    def jugdePrime(self,other):
        if other.prime != self.prime:
            error = 'prime is no equal'
            raise ValueError(error)

def main():
    a = FieldElement(7, 13)
    b = FieldElement(8, 13)
    print(a == b)
    print(a == a)
    print(a+b)
    print(a*b)
    print(a**-3 == b)
    print((29*(12**95)) % 97)


if __name__ == '__main__':
    main()