import bitarray
import my_bits
import implementation
import New_implimentation as new


def is_same(array: bitarray.bitarray, mine: my_bits.Array):
    if len(array) != len(mine):
        return False
    for a in range(len(array)):
        if array[a] != mine[a].val:
            return False
    return True


def main():
    array = implementation.str_to_bits("a")
    other = my_bits.Array().from_text('a')

    wpadded = implementation.pad(array)
    tpadded = new.pad(other)

    wblocks = implementation.to_blocks(wpadded)
    tblocks = new.to_blocks(tpadded)

    wconts = implementation.gen_constants()
    tconts = new.gen_constants()

    wreg = implementation.gen_registers()
    treg = new.gen_registers()

    wgen = implementation.gen_msg_schedule(wblocks[0])
    tgen = new.gen_msg_schedule(tblocks[0])  # dies on gening new schedule parts 17


    wschedule = []
    for a in range(16):
        wschedule.append(wblocks[0][a * 32: (a + 1) * 32])
    tschedule = []
    for a in range(int(len(wblocks[0]) / 32)):
        tschedule.append(tblocks[0][a * 32: (a + 1) * 32])
    # Both are the exact same implimentationn

    for a in range(48):
        print(a)
        wtemp1, wtemp2, wtemp3, wtemp4 = wschedule[a], implementation.sigma_0(wschedule[a + 1]), wschedule[a + 9], implementation.sigma_1(wschedule[a + 14].copy())
        wtogether = implementation.add(wtemp1, wtemp2, wtemp3, wtemp4)
        ttemp1, ttemp2, ttemp3, ttemp4 = tschedule[a].copy(), new.sigma_0(tschedule[a + 1].copy()), tschedule[a + 9].copy(), new.sigma_1(tschedule[a + 14].copy())
        ttogether = my_bits.add_mod(ttemp1.copy(), ttemp2, ttemp3, ttemp4)

        print(f"1:{is_same(wtemp1, ttemp1)}, 2: {is_same(wtemp2, ttemp2)}, 3: {is_same(wtemp3, ttemp3)}, 4: {is_same(wtemp4, ttemp4)}")
        print(is_same(wtogether, ttogether))
        print(implementation.sigma_1(wschedule[a+14]), new.sigma_1(tschedule[a+14]).to_str())

        wschedule.append(wtogether)
        tschedule.append(ttogether)
        if a >= 12:
            print(implementation.sigma_0(wschedule[a+1]))
            print(new.sigma_0(tschedule[a+1]).to_str())
            print(wschedule[a+1])
            print('         ', tschedule[a+1].to_str())
            input('next>')
    # Issue is in new.sigma_1

    wdata = wschedule[16]
    wprep = (implementation.rotr(wdata.copy(), 17), implementation.rotr(wdata.copy(), 19), implementation.shr(wdata.copy(), 10))
    # print(prep)
    wdata = implementation.xor(*wprep)
    tdata = tschedule[16]
    tprep = (tdata.copy().rotate_right(17), tdata.copy().rotate_right(19), tdata.copy().shift_right(10))
    # print([a.to_str() for a in prep], mb.xor_multi(*prep).to_str())
    tdata = my_bits.xor_multi(*tprep)

    # print(is_same(implementation.shr(wdata.copy(), 10, tdata.shift_right(10)), wdata, tdata.to_str())
    # print([a for a in wprep])
    # print([a.to_str() for a in tprep])
    print(is_same(wdata, tdata))

    array = implementation.str_to_bits("a")
    other = my_bits.Array().from_text('a')
    # print(implementation.xor(array.copy(), implementation.shr(array.copy(), 5)))
    # print(other.xor_op(other.copy().shift_right(5)).to_str())

    # for a in range(len(wgen)):
    #     print(a, is_same(wgen[a], tgen[a]))


if __name__ == '__main__':
    main()
