from ellipticCurve.otherUtils.key import *
from ellipticCurve.curve.EllipticCurve import *
import random
from ellipticCurve.mathUtils.quickMod import *
from hashlib import sha256
import secrets


PLAINTEXT = "I am lzy"

def test_getRS():
    pri, pub = gen_keypair(secp256k1)
    randfunc = urandom
    random.seed(randfunc(1048576))
    k = random.randint(1, secp256k1.n)
    g = secp256k1.G
    p = k * g
    z = hash(PLAINTEXT)
    print('z:', z)
    R = p.x
    nk = quickM(k, secp256k1.p-2, secp256k1.p)
    print("nk:", nk)
    s = (nk * (z + pri * R)) % secp256k1.p
    print("s:", s)
    return s,z,R,pub,secp256k1.G,p

def judge(s,z,R,pub,G):
    return ((z*G)+(R*pub))

def getSign():
    pri, pub = gen_keypair(secp256k1)
    s = sign(pri,PLAINTEXT)
    print(verify(pub,PLAINTEXT,s))


def double_hash(message):
    hashed_message = sha256(message.encode('utf-8')).hexdigest()
    hashed_message = sha256(hashed_message.encode('utf-8')).hexdigest()#双重哈希对消息进行加密
    return int(hashed_message, 16)

def sign(private_key, message):#私钥对消息签名
    hashed_message = double_hash(message)#消息为上个函数计算的双重哈希的消息
    print("sign", hashed_message)
    # A secure random number for the signature
    k = secrets.randbelow(1024)#产生一个0到P的随机数，其中randbelow()为secrets包的内置函数
    random_point = secp256k1.G*k #随机数*基点

    # Only the x-value is needed, as the y can always be generated using the curve equation y^2 = x^3 + 7
    rx = random_point.x % secp256k1.p #随机的点有x，y的坐标，但是只取x：random_point[0]，模为N

    signature_proof = quickM(k, secp256k1.p - 2,secp256k1.p) * (hashed_message + rx*private_key) % secp256k1.p#用私钥进行签名

    return (rx, signature_proof) #以元组形式存在的签名

def verify(public_key, message, signature):
    (rx, s) = signature#为签名的形式

    hashed_message = double_hash(message)#双重签名得到的哈希消息
    print("verify",hashed_message)
    inverse_s = quickM(s, secp256k1.p - 2, secp256k1.p)#对s求逆

    # Solve for the random point
    a = secp256k1.G * (hashed_message * (inverse_s % secp256k1.p)) #elliptic_multiply()为乘法
    b = public_key * (rx * (inverse_s % secp256k1.p))#公钥验证
    recovered_random_point = a+b

    # Check that the recovered random point matches the actual random point
    return recovered_random_point.x == rx#相等则表示验证通过




if __name__ == '__main__':
    # s,z,R,pub,G,p = getRS()
    # print("aaafdafd", judge(s,z,R,pub,G))
    # print("aaafdafd",p )
    # print(2**20)
    getSign()

