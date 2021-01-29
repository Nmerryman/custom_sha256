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
    other = my_bits.Array()
    other.from_text("a")

    array = implementation.pad(array)
    other = new.pad(other)

    wblocks = implementation.to_blocks(array)
    tblocks = new.to_blocks(other)

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

    a = 0
    wtemp1, wtemp2, wtemp3, wtemp4 = wschedule[a], implementation.sigma_0(wschedule[a + 1]), wschedule[a + 9], implementation.sigma_1(wschedule[a + 14])
    wtogether = implementation.add(wtemp1, wtemp2, wtemp3, wtemp4)
    ttemp1, ttemp2, ttemp3, ttemp4 = tschedule[a].copy(), new.sigma_0(tschedule[a + 1].copy()), tschedule[a + 9].copy(), new.sigma_1(tschedule[a + 14].copy())
    together = my_bits.add_mod(ttemp1.copy(), ttemp2, ttemp3, ttemp4)

    print(f"")




    for a in range(len(wgen)):
        print(a, is_same(wgen[a], tgen[a]))


if __name__ == '__main__':
    main()
