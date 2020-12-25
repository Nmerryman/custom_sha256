import bitarray
import math
# Programmed with sha256 in mind so some settings may break when trying to change
# Sha only works with 32bits pieces (words)
word_size = 32
block_size = 512
sha_name = 256
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311]


def str_to_bits(data: str):
    # Helper to convert ascii to bits
    array = bitarray.bitarray()
    array.frombytes(data.encode())
    return array


def shr(data: bitarray.bitarray, dist: int):
    # shift right
    data = data.copy()
    for a in range(dist):
        data.insert(0, 0)
        data.pop()
    return data


def rotr(data: bitarray.bitarray, dist: int):
    # rotate right
    data = data.copy()
    for a in range(dist):
        data.insert(0, data.pop())
    return data


def xor_vals(*args: int):
    # xor multiple individual values
    thing = False
    for a in args:
        if int(a) == 1:
            thing = not thing
    return thing


def xor(*args: bitarray.bitarray):
    # xor arrays
    base = args[0].copy()
    if len(args) > 1:
        for a in args[1:]:
            base ^= a
    return base


def add(*args: bitarray.bitarray):
    # Add multiple arrays
    base = int(args[0].to01(), 2)
    if len(args) > 1:
        for a in args[1:]:
            base += int(a.to01(), 2)
    out = "{0:b}".format(base)
    out = '0' * (word_size - len(out)) + out
    out = out[-word_size:]
    return bitarray.bitarray(out)


def sigma_0(data: bitarray.bitarray):
    # sha operation
    prep = (rotr(data.copy(), 7), rotr(data.copy(), 18), shr(data.copy(), 3))
    return xor(*prep)


def sigma_1(data: bitarray.bitarray):
    # sha operation
    prep = (rotr(data.copy(), 17), rotr(data.copy(), 19), shr(data.copy(), 10))
    return xor(*prep)


def SIGMA_0(data: bitarray.bitarray):
    # sha operation
    prep = (rotr(data.copy(), 2), rotr(data.copy(), 13), rotr(data.copy(), 22))
    return xor(*prep)


def SIGMA_1(data: bitarray.bitarray):
    # sha operation
    prep = (rotr(data.copy(), 6), rotr(data.copy(), 11), rotr(data.copy(), 25))
    return xor(*prep)


def choice(x: bitarray.bitarray, y: bitarray.bitarray, z: bitarray.bitarray):
    # for each in array x, if 1, choose y value from same index, else z value
    base = bitarray.bitarray('0'*len(x))
    for num_a, a in enumerate(x):
        if int(a) == 1:
            base[num_a] = y[num_a]
        else:
            base[num_a] = z[num_a]
    return base


def majority(x: bitarray.bitarray, y: bitarray.bitarray, z: bitarray.bitarray):
    # majority
    base = bitarray.bitarray('0' * len(x))
    for a in range(len(x)):
        if int(x[a]) + int(y[a]) + int(z[a]) > 1:
            base[a] = 1
    return base


def gen_cube_root_const(root: int):
    # Only does one digit at a time
    root = pow(root, 1/3)
    fractional = root - math.floor(root)
    hexed = ""
    for _ in range(8):
        product = fractional * 16
        hexed += str(hex(int(math.floor(product))))[2:]
        fractional = product - math.floor(product)
    val = "{0:b}".format(int(hexed, base=16))
    val = '0' * (word_size - len(val)) + val
    return bitarray.bitarray(val)


def gen_sqr_root_init(root: int):
    # Only does one digit at a time
    root = pow(root, 1/2)
    fractional = root - math.floor(root)
    preped = int(fractional * 2**32)
    out = "{0:b}".format(preped)
    out = '0' * (word_size - len(out)) + out
    return bitarray.bitarray(out)


def pad(message: bitarray.bitarray):
    # This assumes all fits into only 1 message of 512
    base = message.copy()
    ks = 448 - 1 - len(message)
    while ks < 0:
        ks += block_size
    base.append(1)
    for _ in range(ks):
        base.append(0)
    extra = "{0:b}".format(len(message))
    extra = "0" * (64 - len(extra)) + extra
    return base + bitarray.bitarray(extra)


def to_blocks(message: bitarray.bitarray):
    blocks = len(message) / block_size
    pieces = []
    for a in range(int(blocks)):
        pieces.append(message[a * block_size: (a + 1) * block_size])
    return pieces


def gen_msg_schedule(message: bitarray.bitarray):
    schedule = []
    for a in range(int(len(message) / word_size)):
        schedule.append(message[a * word_size: (a + 1) * word_size])
    for a in range(64 - len(schedule)):
        temp1, temp2, temp3, temp4 = schedule[a], sigma_0(schedule[a + 1]), schedule[a + 9], sigma_1(schedule[a + 14])
        together = add(temp1, temp2, temp3, temp4)
        schedule.append(together)
    return schedule


def gen_constants():
    # Never changes
    const = []
    for a in primes:
        const.append(gen_cube_root_const(a))
    return const


def gen_registers():
    # Never changes
    reg = []
    for a in primes[:8]:
        reg.append(gen_sqr_root_init(a))
    return reg


def update_registers(word: bitarray.bitarray, constant: bitarray.bitarray, registers: list):
    # print(word, constant, registers)
    T1 = add(word, constant, SIGMA_1(registers[4]), choice(*registers[4: 7]), registers[7])
    T2 = add(majority(*registers[0:3]), SIGMA_0(registers[0]))
    # print(word, constant, registers)
    # print('t', T1, T2)
    base_reg = registers.copy()
    base_reg.insert(0, add(T1, T2))
    base_reg.pop()
    # print(registers[4], T1)
    base_reg[4] = add(base_reg[4], T1)
    # print(registers[4], T1)
    return base_reg


def compress(schedule: list, constants: list, registers: list):
    # print(registers)
    new_reg = registers.copy()
    for a in range(64):
        registers = update_registers(schedule[a], constants[a], registers)
        # print(a, registers)

    for a in range(8):
        registers[a] = add(new_reg[a], registers[a])

    return registers


def reg_to_hash(registers: list):
    out = ""
    for a in registers:
        val = hex(int(a.to01(), 2))[2:]
        val = "0" * (8 - len(val)) + val  # some registers start with 0 which needs to be added back on
        out += val
    return out


def hash_bits(data: bitarray.bitarray):
    # This starts from the very start with only input bits
    array = pad(data)
    blocks = to_blocks(array)
    # print(blocks[1])
    constants = gen_constants()
    registers = gen_registers()

    for a in blocks:
        schedule = gen_msg_schedule(a)
        # print(registers, '\n')
        registers = compress(schedule.copy(), constants.copy(), registers.copy())

    return reg_to_hash(registers)


def hash_str(string: str):
    # I could make this into one line but this looks nicer to me.
    bits = str_to_bits(string)
    hash_val = hash_bits(bits)
    return hash_val


def hash_bytes(data: bytes):
    bits = bitarray.bitarray()
    bits.frombytes(data)
    hash_val = hash_bits(bits)
    return hash_val


def test():
    # These hashes are compared with results from https://emn178.github.io/online-tools/sha256.html
    # testing various sizes
    start = 'abc'
    array = str_to_bits(start)
    hash_val = hash_bits(array)
    print(len(array), start, '=>', hash_val)
    assert hash_val == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    print('WORKED')
    
    start = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz'
    array = str_to_bits(start)
    hash_val = hash_bits(array)
    print(len(array), start, '=>', hash_val)
    assert str(hash_val) == '941ac378682e3dc66275dd49d5fb09978754ecf4231d18d30326fa51962648ec'
    print('WORKED')

    start = '''abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz'''
    bits = str_to_bits(start)
    hash_val = hash_bits(bits)
    assert hash_val == "064eae61978ddb8c86764defd787420950d2e4b126e8306cdb565e3d082d55dd"
    print("WORKED")

    # testing from text file
    with open('test_file.txt', 'r') as f:
        hash_val = hash_str(f.read())
    assert hash_val == 'd9d38162f61210a97161fc66fe8fe266566c96547aab3ad2b34bb170dce4a7cb'
    print("plain text worked")

    # testing reading bytes form file
    with open('test_file.txt', 'rb') as f:
        bits = bitarray.bitarray()  # init
        bits.frombytes(f.read())  # load
    hash_val = hash_bits(bits)
    assert hash_val == 'a64c58af41981c80629ddeef8234a5485469787659d59c88ddff68c819100d3d'
    print("file bytes worked")

    # test for simplified func
    with open('test_file.txt', 'rb') as f:
        hash_val = hash_bytes(f.read())
    assert hash_val == 'a64c58af41981c80629ddeef8234a5485469787659d59c88ddff68c819100d3d'


def main():
    test()
    quit()
    array = str_to_bits('abc')
    # print(array)
    # test = bitarray.bitarray('11111111000000001111111100000000')
    # test_2 = bitarray.bitarray('11111111000000000000111000011111')
    # test_5 = bitarray.bitarray('00000000000000001111111111111111')
    # test_3 = bitarray.bitarray('1010')
    # test_4 = bitarray.bitarray('0111')
    # print(majority(shr(test, 8), test_5, rotr(test_5, 16)))
    # print('Base input', array)
    # print('Padded', pad(array))
    array = pad(array)
    # print("Split blocks", to_blocks(array))
    # Only takes first block for testing
    block = to_blocks(array)[0]
    # print('Gen schedule (W16)', gen_msg_schedule(block)[-1])
    msg_schedule = gen_msg_schedule(block)
    # print('Gen constants', gen_constants())
    constants = gen_constants()
    # print('Gen registers', gen_registers())
    registers = gen_registers()
    # print("Update register (test)", update_registers(msg_schedule[0], constants[0], registers))
    compressed = compress(msg_schedule, constants, registers)
    print("Compressed", compressed)
    print("Registers merged", reg_to_hash(compressed))

    print(hash_bits(array))
    print(array)


if __name__ == '__main__':
    main()
