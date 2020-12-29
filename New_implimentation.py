from my_bits import *
import math


def sigma_0(data: Array):
    # sha operation
    prep = (data.copy().rotate_right(7), data.copy().rotate_right(13), data.copy().shift_right(3))
    return xor(*prep)


def sigma_1(data: Array):
    # sha operation
    prep = (data.copy().rotate_right(17, data.copy().rotate_right(19), data.copy().shift_right(10)))
    return xor(*prep)


def SIGMA_0(data: Array):
    # sha operation
    prep = (data.copy().rotate_right(2), data.copy().rotate_right(13), data.copy().rotate_right(22))
    return xor(*prep)


def SIGMA_1(data: Array):
    # sha operation
    prep = (data.copy().rotate_right(6), data.copy().rotate_right(11), data.copy().rotate_right(25))
    return xor(*prep)


def gen_square(root: int):
    # Only does one digit at a time
    root = pow(root, 1/2)
    fractional = root - math.floor(root)
    preped = int(fractional * 2**32)
    out = "{0:b}".format(preped)
    out = '0' * (32 - len(out)) + out
    return out


def gen_cube(root: int):
    # Only does one digit at a time
    root = pow(root, 1/3)
    fractional = root - math.floor(root)
    preped = int(fractional * 2**32)
    out = "{0:b}".format(preped)
    out = '0' * (32 - len(out)) + out
    return out


def pad(message: Array):
    # This assumes all fits into only 1 message of 512
    # todo label the important bits here
    base = message.copy()
    ks = 448 - 1 - len(message)
    while ks < 0:
        ks += 512
    base.content.append()
    for _ in range(ks):
        base.append(0)
    extra = "{0:b}".format(len(message))
    extra = "0" * (64 - len(extra)) + extra
    return base.content.append(Array(extra).content)


def main():
    print(gen_cube(7))
    print(gen_square(7))


if __name__ == '__main__':
    main()
