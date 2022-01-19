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
    pri, pub = gen_keypair(secp256k1)
    randfunc = urandom
    random.seed(randfunc(1024))
    k = 0  # 产生一个0到P的随机数，其中randbelow()为secrets包的内置函数
    while k == 0:
        k = secrets.randbelow(secp256k1.n)
    p = secp256k1.G * k  # 随机数*基点
    z = double_hash(PLAINTEXT)
    print('z:', z)
    R = p.x
    signature_proof = (quickM(k, secp256k1.n - 2, secp256k1.n) * (z + R*pri)) % secp256k1.n
    return signature_proof,z,R,pub,secp256k1.G,p


def judge(s,z,R,pub):
    a = secp256k1.G * (z * (s % secp256k1.n))
    b = pub * (R * (s % secp256k1.n))
    return (a+b).x == R


def getSign():
    pri, pub = gen_keypair(secp256k1)
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
    while k == 0:
        k =secrets.randbelow(secp256k1.n)
    random_point = secp256k1.G*k  #随机数*基点
    # Only the x-value is needed, as the y can always be generated using the curve equation y^2 = x^3 + 7
    # rx = random_point.x % secp256k1.p #随机的点有x，y的坐标，但是只取x：random_point[0]，模为N
    rx = random_point.x% secp256k1.n
    signature_proof = quickM(k, secp256k1.n - 2, secp256k1.n) * (hashed_message + rx*private_key) % secp256k1.n     #用私钥进行签名
    return (rx, signature_proof) #以元组形式存在的签名


def verify(public_key, message, signature):
    (rx, s) = signature#为签名的形式
    print("verify-s",s)
    hashed_message = double_hash(message)#双重签名得到的哈希消息
    inverse_s = quickM(s, secp256k1.n - 2, secp256k1.n)#对s求逆
    print("verify-inverse_s",inverse_s)
    print("is inverse",(inverse_s*s)%secp256k1.n)
    # Solve for the random point
    a = secp256k1.G * (hashed_message * (inverse_s % secp256k1.n)) #elliptic_multiply()为乘法
    b = public_key * (rx * (inverse_s % secp256k1.n))#公钥验证
    recovered_random_point = a+b

    # Check that the recovered random point matches the actual random point
    return recovered_random_point.x == rx#相等则表示验证通过


def verify_e():
    s_inv = quickM()

if __name__ == '__main__':
    s,z,R,pub,G,p = test_getRS()
    print("aaafdafd", judge(s,z,R,pub))
    getSign()
    # print(2**20)

