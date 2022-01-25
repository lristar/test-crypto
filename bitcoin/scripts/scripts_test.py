import hashlib


# OP_DUP
def op_dup(stack):
    if len(stack) < 1:
        return False
    stack.append(stack[-1])
    return True


# OP_HASH256
def op_hash256(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hashlib.sha256(element))
    return True


# OP_CHECKSIG


OP_CODE_FUNCTIONS = {
    118: op_dup,
    170: op_hash256,
}


def main():
    list = [1, 2, 3, 4, 5, 6]
    # -1是指list中的最后
    list.append(list[-1])
    print(list)


if __name__ == '__main__':
    main()
