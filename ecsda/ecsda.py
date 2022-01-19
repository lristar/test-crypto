import sys

sys.path.append("..")
from ellipticCurve.otherUtils.key import *
from ellipticCurve.curve.EllipticCurve import *
import random
from ellipticCurve.mathUtils.quickMod import *
from hashlib import sha256
import secrets

PLAINTEXT = "I am lzy"


def test_getRS():
    pri, pub = gen_keypair(easy)
    randfunc = urandom
    random.seed(randfunc(1024))
    k = random.randint(1, easy.n)
    g = easy.G
    p = k * g
    z = hash(PLAINTEXT).to_bytes(20)
    print('z:', z)
    R = p.x
    nk = quickM(k, easy.p-2, easy.p)
    print("nk:", nk)
    s = (nk * (z + pri * R)) % easy.p
    print("s:", s)
    return s,z,R,pub,easy.G,p


def judge(s,z,R,pub,G):
    return ((z*G)+(R*pub))


def getSign():
    pri, pub = gen_keypair(easy)
    s = sign(pri, PLAINTEXT)
    print(verify(pub, PLAINTEXT, s))


def double_hash(message):
    hashed_message = sha256(message.encode('utf-8')).hexdigest()
    hashed_message = sha256(hashed_message.encode('utf-8')).hexdigest()#双重哈希对消息进行加密
    return int(hashed_message, 20)


def sign(private_key, message):#私钥对消息签名
    hashed_message = double_hash(message)#消息为上个函数计算的双重哈希的消息
    # A secure random number for the signature
    k = 0 #产生一个0到P的随机数，其中randbelow()为secrets包的内置函数
    while k ==0:
        k =secrets.randbelow(5)
    random_point = easy.G*k  #随机数*基点
    print("sign-random_point", random_point)
    # Only the x-value is needed, as the y can always be generated using the curve equation y^2 = x^3 + 7
    # rx = random_point.x % easy.p #随机的点有x，y的坐标，但是只取x：random_point[0]，模为N
    rx = random_point.x
    print("sign-rx", rx)
    signature_proof = quickM(k, easy.p - 2, easy.p) * (hashed_message + rx*private_key) % easy.p     #用私钥进行签名
    print("sign-signature_proof",signature_proof)
    return (rx, signature_proof) #以元组形式存在的签名


def verify(public_key, message, signature):
    (rx, s) = signature#为签名的形式
    print("verify-s",s)
    hashed_message = double_hash(message)#双重签名得到的哈希消息
    inverse_s = quickM(s, easy.p - 2, easy.p)#对s求逆
    print("verify-inverse_s",inverse_s)
    print("is inverse",(inverse_s*s)%easy.p)
    # Solve for the random point
    a = easy.G * (hashed_message * (inverse_s % easy.p)) #elliptic_multiply()为乘法
    b = public_key * (rx * (inverse_s % easy.p))#公钥验证
    recovered_random_point = a+b

    # Check that the recovered random point matches the actual random point
    return recovered_random_point.x == rx#相等则表示验证通过


def verify_e():
    s_inv = quickM()

if __name__ == '__main__':
    # getSign()
    z = 0xbc62d4b80d9e36da29c16c5d4d9f11731f36052c72401a76c23c0fb5a9b74423
    r = 0x37206a0610995C58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c6
    s = 0x8ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec
    px = 0x04519fac3d910ca7e7138f7013706f619fa8f033e6ec6e09370ea38cee6a7574
    py = 0x82b51eab8c27c66e26c858a079bcdf4f1ada34cec420cafc7eac1a42216fb6c4
    point = secp256k1.getP(px,py)
    s_inv = quickM(s,secp256k1.n-2,secp256k1.n)
    u = z * s_inv % secp256k1.n
    v = r *s_inv %secp256k1.n
    print((u *secp256k1.G + v *point).x ==r)

