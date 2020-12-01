import bitarray
import math
# this assumes it fits in 1 sha block
# Sha only works with 32bits pieces (words)
small_chunk_size = 32
sha_size = 256
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311]


def to_bits(data: str):
    array = bitarray.bitarray()
    array.frombytes(data.encode())
    return array


def shr(data: bitarray.bitarray, dist: int):
    data = data.copy()
    for a in range(dist):
        data.insert(0, 0)
        data.pop()
    return data


def rotr(data: bitarray.bitarray, dist: int):
    data = data.copy()
    for a in range(dist):
        data.insert(0, data.pop())
    return data


def xor_vals(*args: int):
    thing = False
    for a in args:
        if int(a) == 1:
            thing = not thing
    return thing


def xor(*args: bitarray.bitarray):
    base = args[0].copy()
    if len(args) > 1:
        for a in args[1:]:
            base ^= a
    return base


def add(*args: bitarray.bitarray):
    base = int(args[0].to01(), 2)
    if len(args) > 1:
        for a in args[1:]:
            base += int(a.to01(), 2)
    return bitarray.bitarray(bin(base)[-small_chunk_size:])


def sigma_0(data: bitarray.bitarray):
    prep = (rotr(data.copy(), 7), rotr(data.copy(), 18), shr(data.copy(), 3))
    return xor(*prep)


def sigma_1(data: bitarray.bitarray):
    prep = (rotr(data.copy(), 17), rotr(data.copy(), 19), shr(data.copy(), 10))
    return xor(*prep)


def SIGMA_0(data: bitarray.bitarray):
    prep = (rotr(data.copy(), 2), rotr(data.copy(), 13), rotr(data.copy(), 22))
    return xor(*prep)


def SIGMA_1(data: bitarray.bitarray):
    prep = (rotr(data.copy(), 6), rotr(data.copy(), 11), rotr(data.copy(), 25))
    return xor(*prep)


def choice(x: bitarray.bitarray, y: bitarray.bitarray, z: bitarray.bitarray):
    base = bitarray.bitarray('0'*len(x))
    for num_a, a in enumerate(x):
        if int(a) == 1:
            base[num_a] = y[num_a]
        else:
            base[num_a] = z[num_a]
    return base


def majority(x: bitarray.bitarray, y: bitarray.bitarray, z: bitarray.bitarray):
    base = bitarray.bitarray('0' * len(x))
    for a in range(len(x)):
        if int(x[a]) + int(y[a]) + int(z[a]) > 1:
            base[a] = 1
    return base


def gen_cube_root_const(root: int):
    root = pow(root, 1/3)
    fractional = root - math.floor(root)
    hexed = ""
    for _ in range(8):
        product = fractional * 16
        hexed += str(hex(int(math.floor(product))))[2:]
        fractional = product - math.floor(product)
    val = "{0:b}".format(int(hexed, base=16))
    val = '0' * (small_chunk_size - len(val)) + val
    return val


def pad(message: bitarray.bitarray):
    # This assumes all fits into only 1 message of 512
    message.extend((1))



def main():
    # array = to_bits('abc')
    # print(array)
    test = bitarray.bitarray('11111111000000001111111100000000')
    test_2 = bitarray.bitarray('11111111000000000000111000011111')
    test_5 = bitarray.bitarray('00000000000000001111111111111111')
    # test_3 = bitarray.bitarray('1010')
    # test_4 = bitarray.bitarray('0111')
    print(majority(shr(test, 8), test_5, rotr(test_5, 16)))
    print(pad(test))


if __name__ == '__main__':
    main()
