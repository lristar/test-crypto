from cryptos import *


def shex(s, st, t):
    temp = int(s, st)
    if t == 16:
        return hex(temp)
    elif t == 8:
        return bin(temp)
    return temp


def main():
    c = Bitcoin(testnet=True)
    priv = sha256('a big big big hello world')
    print("priv:", priv)
    print("priv len:", len(priv))
    pub = c.privtopub(priv)
    print("create publish:", pub)
    print("publish len:", len(pub))
    x = pub[2:66]
    y = pub[66:130]
    print("len x:", len(x), " len y:", len(y))
    print("x:", x)
    print("y:", y)
    pubx = shex(x, 16, 16)
    print("pubx:", pubx)
    puby = shex(y, 16, 16)
    print("puby:", puby)
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    addr = c.pubtoaddr(pub)
    print("addr:", addr)
    print("addr len ", len(addr))


if __name__ == '__main__':
    main()
