def quickM(a, b, m):
    a = a % m
    ans = 1
    while b != 0:
        if b & 1:
            ans = (ans * a) % m
        b >>= 1
        a = (a * a) % m
    return ans


