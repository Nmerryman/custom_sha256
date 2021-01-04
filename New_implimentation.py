import my_bits as mb
import math
import gc

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311]


def sigma_0(data: mb.Array):
    # sha operation
    prep = (data.copy().rotate_right(7), data.copy().rotate_right(13), data.copy().shift_right(3))
    return mb.xor_multi(*prep)


def sigma_1(data: mb.Array):
    # sha operation
    prep = (data.copy().rotate_right(17), data.copy().rotate_right(19), data.copy().shift_right(10))
    return mb.xor_multi(*prep)


def SIGMA_0(data: mb.Array):
    # sha operation
    prep = (data.copy().rotate_right(2), data.copy().rotate_right(13), data.copy().rotate_right(22))
    return mb.xor_multi(*prep)


def SIGMA_1(data: mb.Array):
    # sha operation
    prep = (data.copy().rotate_right(6), data.copy().rotate_right(11), data.copy().rotate_right(25))
    return mb.xor_multi(*prep)


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


def pad(message: mb.Array):
    # This assumes all fits into only 1 message of 512
    # todo label the important bits here
    base = message.copy()
    ks = 448 - 1 - len(message)
    while ks < 0:
        ks += 512
    base.content.append(mb.Bit(1))
    for _ in range(ks):
        base.content.append(mb.Bit(0))
    extra = "{0:b}".format(len(message))
    extra = "0" * (64 - len(extra)) + extra
    base.content.extend(mb.Array(extra).content)
    return base


def to_blocks(message: mb.Array):
    # must a working size
    blocks = len(message) / 512
    print('blocks', blocks)
    pieces = []
    for a in range(int(blocks)):
        print('cut')
        pieces.append(message[a * 512: (a + 1) * 512])
    return pieces


# @profile
def gen_msg_schedule(message: mb.Array):
    schedule = []
    for a in range(int(len(message) / 32)):
        schedule.append(message[a * 32: (a + 1) * 32])
        # print(len(message[a * 32: (a + 1) * 32].to_str()))
    for a in range(64 - len(schedule)):
        # print(f'gen msg {a}')
        # if a > 3:
        #     quit()
        temp1, temp2, temp3, temp4 = schedule[a].copy(), sigma_0(schedule[a + 1].copy()), schedule[a + 9].copy(), sigma_1(schedule[a + 14].copy())
        together = mb.add_mod(temp1, temp2, temp3, temp4)
        # print(together.to_str())
        schedule.append(together)
    # for num_a, a in enumerate(schedule):
    #     print(num_a, a.to_str())
    return schedule


def gen_constants():
    # Never changes
    const = []
    for a in primes:
        const.append(mb.Array(gen_cube(a)))
    return const


def gen_registers():
    # Never changes
    reg = []
    for a in primes[:8]:
        reg.append(mb.Array(gen_square(a)))
    return reg


def update_registers(word: mb.Array, constant: mb.Array, registers: list):
    # print(len(word), constant, registers)
    T1 = mb.add_mod(word.copy(), constant, SIGMA_1(registers[4]), mb.choice(*registers[4: 7]), registers[7])
    T2 = mb.add_mod(mb.majority(*registers[0:3]), SIGMA_0(registers[0]))
    # print(word, constant, registers)
    # print('t', T1, T2)
    base_reg = registers.copy()
    base_reg.insert(0, mb.add_mod(T1.copy(), T2))
    base_reg.pop()
    # print(registers[4], T1)
    base_reg[4] = mb.add_mod(base_reg[4], T1)
    # print(registers[4], T1)
    for a in base_reg:
        if len(a) > 32:
            a = a[-32:]
    return base_reg


def compress(schedule: list, constants: list, registers: list):
    # print(registers)
    new_reg = []
    for a in registers:
        new_reg.append(a.copy())
    for a in range(64):
        print('update reg')
        registers = update_registers(schedule[a], constants[a], registers)
        # print(a, registers)

    for a in range(8):
        registers[a] = mb.add_mod(new_reg[a], registers[a])

    return registers


def reg_to_hash(registers: list):
    out = ""
    for a in registers:
        a: mb.Array
        val = hex(int(a.to_str(), 2))[2:]
        val = "0" * (8 - len(val)) + val  # some registers start with 0 which needs to be added back on
        out += val
    return out


def hash_bits(data: mb.Array):
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
    bits = mb.Array()
    bits.from_text(string)
    # print(bits.to_str())
    hash_val = hash_bits(bits)
    return hash_val


def hash_bytes(data: bytes):
    bits = mb.Array()
    bits.from_text(data)
    hash_val = hash_bits(bits)
    return hash_val


def test():
    data = mb.Array('0' * 500000)
    # print(data.to_str())
    input('>')


def main():
    # print(gen_cube(7))
    # print(gen_square(7))
    # test()
    # quit()
    print(hash_str("abc"))


if __name__ == '__main__':
    mb.USE_HISTORY = False
    main()
