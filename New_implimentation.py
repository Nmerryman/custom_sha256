from my_bits import *
import math

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311]


def sigma_0(data: Array):
    # sha operation
    prep = (data.copy().rotate_right(7), data.copy().rotate_right(13), data.copy().shift_right(3))
    return xor_multi(*prep)


def sigma_1(data: Array):
    # sha operation
    prep = (data.copy().rotate_right(17), data.copy().rotate_right(19), data.copy().shift_right(10))
    return xor_multi(*prep)


def SIGMA_0(data: Array):
    # sha operation
    prep = (data.copy().rotate_right(2), data.copy().rotate_right(13), data.copy().rotate_right(22))
    return xor_multi(*prep)


def SIGMA_1(data: Array):
    # sha operation
    prep = (data.copy().rotate_right(6), data.copy().rotate_right(11), data.copy().rotate_right(25))
    return xor_multi(*prep)


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
    base.content.append(Bit(1))
    for _ in range(ks):
        base.content.append(Bit(0))
    extra = "{0:b}".format(len(message))
    extra = "0" * (64 - len(extra)) + extra
    base.content.extend(Array(extra).content)
    return base


def to_blocks(message: Array):
    # must a working size
    blocks = len(message) / 512
    print('blocks', blocks)
    pieces = []
    for a in range(int(blocks)):
        print('cut')
        pieces.append(message[a * 512: (a + 1) * 512])
    return pieces


def gen_msg_schedule(message: Array):
    schedule = []
    for a in range(int(len(message) / 32)):
        schedule.append(message[a * 32: (a + 1) * 32])
    for a in range(64 - len(schedule)):
        input(f'gen msg {a}')
        temp1, temp2, temp3, temp4 = schedule[a], sigma_0(schedule[a + 1]), schedule[a + 9], sigma_1(schedule[a + 14])
        together = add(temp1, temp2, temp3, temp4)
        schedule.append(together)
    return schedule


def gen_constants():
    # Never changes
    const = []
    for a in primes:
        const.append(gen_cube(a))
    return const


def gen_registers():
    # Never changes
    reg = []
    for a in primes[:8]:
        reg.append(gen_square(a))
    return reg


def update_registers(word: Array, constant: Array, registers: list):
    # print(word, constant, registers)
    T1 = add(word, constant, SIGMA_1(registers[4]), choice(*registers[4: 7]), registers[7])[-32:]
    T2 = add(majority(*registers[0:3]), SIGMA_0(registers[0]))[-32:]
    # print(word, constant, registers)
    # print('t', T1, T2)
    base_reg = registers.copy()
    base_reg.insert(0, add(T1, T2)[-32:])
    base_reg.pop()
    # print(registers[4], T1)
    base_reg[4] = add(base_reg[4], T1)[-32]
    # print(registers[4], T1)
    return base_reg


def compress(schedule: list, constants: list, registers: list):
    # print(registers)
    new_reg = registers.copy()
    for a in range(64):
        input('update reg')
        registers = update_registers(schedule[a], constants[a], registers)
        # print(a, registers)

    for a in range(8):
        registers[a] = add(new_reg[a], registers[a])[-32:]

    return registers


def reg_to_hash(registers: list):
    out = ""
    for a in registers:
        val = hex(int(a.to01(), 2))[2:]
        val = "0" * (8 - len(val)) + val  # some registers start with 0 which needs to be added back on
        out += val
    return out


def hash_bits(data: Array):
    # This starts from the very start with only input bits
    array = pad(data)
    # print(array.to_str())
    blocks = to_blocks(array)
    print(blocks)
    constants = gen_constants()
    registers = gen_registers()

    for a in blocks:
        schedule = gen_msg_schedule(a)
        # print(registers, '\n')
        registers = compress(schedule.copy(), constants.copy(), registers.copy())

    return reg_to_hash(registers)


def hash_str(string: str):
    # I could make this into one line but this looks nicer to me.
    bits = Array()
    bits.from_text(string)
    # print(bits.to_str())
    hash_val = hash_bits(bits)
    return hash_val


def hash_bytes(data: bytes):
    bits = Array()
    bits.from_text(data)
    hash_val = hash_bits(bits)
    return hash_val


def main():
    # print(gen_cube(7))
    # print(gen_square(7))
    print(hash_str("abc"))


if __name__ == '__main__':
    main()
