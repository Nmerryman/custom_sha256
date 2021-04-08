import my_bits as mb
import math
import os
import json

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
          109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
          233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311]


def goto_dir(name: str):
    if not os.path.isdir(name):
        os.mkdir(name)
    os.chdir(name)


def sigma_0(data: mb.Array):
    # sha operation
    prep = (data.copy().rotate_right(7), data.copy().rotate_right(18), data.copy().shift_right(3))
    return mb.xor_multi(*prep)


def sigma_1(data: mb.Array):
    # sha operation
    prep = (data.copy().rotate_right(17), data.copy().rotate_right(19), data.copy().shift_right(10))
    # print([a.to_str() for a in prep], mb.xor_multi(*prep).to_str())
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
    root = pow(root, 1 / 2)
    fractional = root - math.floor(root)
    preped = int(fractional * 2 ** 32)
    out = "{0:b}".format(preped)
    out = '0' * (32 - len(out)) + out
    return out


def gen_cube(root: int):
    # Only does one digit at a time
    root = pow(root, 1 / 3)
    fractional = root - math.floor(root)
    preped = int(fractional * 2 ** 32)
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
        pieces.append(message[a * 512: (a + 1) * 512])
    return pieces


# @profile
def gen_msg_schedule(message: mb.Array):
    schedule = []
    for a in range(int(len(message) / 32)):
        schedule.append(message[a * 32: (a + 1) * 32])
    for a in range(64 - len(schedule)):
        # print(f'gen msg {a}')
        # if a > 3:
        #     quit()
        temp1, temp2, temp3, temp4 = schedule[a].copy(), sigma_0(schedule[a + 1].copy()), schedule[
            a + 9].copy(), sigma_1(schedule[a + 14].copy())
        together = mb.add_mod(temp1.copy(), temp2, temp3, temp4)
        schedule.append(together)
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
    T1 = mb.add_mod(word.copy(), constant, SIGMA_1(registers[4]), mb.choice(*registers[4: 7]), registers[7])
    T2 = mb.add_mod(mb.majority(*registers[0:3]), SIGMA_0(registers[0]))

    base_reg = registers.copy()
    base_reg.insert(0, mb.add_mod(T1.copy(), T2))
    base_reg.pop()
    base_reg[4] = mb.add_mod(base_reg[4], T1)

    for a in base_reg:
        if len(a) > 32:
            a = a[-32:]

    return base_reg


def compress(schedule: list, constants: list, registers: list):
    new_reg = []
    for a in registers:
        new_reg.append(a.copy())
    for a in range(64):
        registers = update_registers(schedule[a], constants[a], registers)

    for a in range(8):
        registers[a] = mb.add_mod(new_reg[a], registers[a])

    return registers


def reg_to_hash(registers: list):
    """Obsolete"""
    out = ""
    for a in registers:
        a: mb.Array
        val = hex(int(a.to_str(), 2))[2:]
        val = "0" * (8 - len(val)) + val  # some registers start with 0 which needs to be added back on
        out += val
    return out


def merge_reg(registers: list) -> mb.Array:
    final = mb.Array()
    for a in registers:
        for b in a:
            final.content.append(b)
    return final


def hash_bits(data: mb.Array) -> mb.Array:
    # This starts from the very start with only input bits
    array = pad(data)
    for num_a, a in enumerate(array):
        a.history = f"(b{num_a})"

    blocks = to_blocks(array)

    constants = gen_constants()
    registers = gen_registers()

    for a in blocks:
        schedule = gen_msg_schedule(a)
        registers = compress(schedule.copy(), constants.copy(), registers.copy())

    return merge_reg(registers)


def hash_str(string: str):
    # I could make this into one line but this looks nicer to me.
    bits = mb.Array()
    bits.from_text(string)
    hash_val = hash_bits(bits)
    return hash_val


def hash_bytes(data: bytes):
    bits = mb.Array()
    bits.from_bytes(data)
    hash_val = hash_bits(bits)
    return hash_val


def test():
    # Generic hash
    assert hash_str('abc').to_hex()[2:] == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'

    # Hash file bytes
    with open('test_file.txt', 'rb') as f:
        assert hash_bytes(f.read()).to_hex()[2:] == 'a64c58af41981c80629ddeef8234a5485469787659d59c88ddff68c819100d3d'
    print("Hashing string and file bytes worked")


def main():
    # test = mb.Array(255)
    # print(test.to_hex())
    # test()
    # quit()
    val = hash_str('abc')
    print(val.to_hex())
    json.dump(mb.HIST_DICT, open("_HIST_1.json", 'w'), indent=4)
    # json.dump

    # for num_a, a in enumerate(val):
    #     print(num_a, a.history)


if __name__ == '__main__':
    goto_dir("temp_data")
    mb.USE_HISTORY = True
    mb.MAX_HIST_LEN = 1
    main()
