

"""
This was made specifically for working with the sha256 hash to better understand how it works
"""


USE_HISTORY = False
HISTORY_OFFLOADING = True
MAX_HIST_LEN = 1000
HIST_INDEX = 0
# System => (a111)=1 (x001)=1 (m010)=0 (c110)=1 (o10)=1 (b1)=1     (f12)
#           and      xor      Majority Choice   or      const/base file data
# add is assumes it only cares about local bit (A(mainx)(mainy)(carryz)) carry is majority, A is xor.
# add will be written as (x10(M00(...)), ... is prev add func or const. add will always have 3 objects
# If more space needs to be saved, (), [], {}, <>, '", /\ can be used hold data and op type


class Bit:

    def __init__(self, val: int):
        self.val: int = val
        if USE_HISTORY:
            self.history: str = f"(b{self.val})"
        else:
            self.history = ""

    def copy(self):
        new = Bit(self.val)
        new.history = self.history
        return new

    def check_hist(self):
        global HISTORY_OFFLOADING, USE_HISTORY, HIST_INDEX, MAX_HIST_LEN
        if USE_HISTORY and HISTORY_OFFLOADING and len(self.history) > MAX_HIST_LEN:
            with open(f"{HIST_INDEX}", 'w') as f:
                f.write(self.history)
            self.history = f"(f{HIST_INDEX})"
            HIST_INDEX += 1


class Array:
    # All conversions assume hex was given for leading zeros
    def __init__(self, bits=None):
        self.content = []
        if not bits:
            self.content = []
        elif type(bits) == str:
            self.from_str_bin(bits)
        elif type(bits) == int:
            self.from_num(bits)
        elif type(bits) == list:
            for a in bits:
                self.content.append(self._gen_bit(a))
        else:
            raise ValueError("Bad init values")

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        return (b for b in self.content)

    def __getitem__(self, item):
        if type(item) == int:
            return self.content[item]
        part = self.content[item]
        new = Array()
        new.content = part
        return new

    @staticmethod
    def _gen_bit(val):
        # No safety checks in here
        # Might be able to do it all in 1 line rn
        if type(val) == int:
            return Bit(val)
        elif type(val) == str:
            return Bit(int(val))

    def _check_histories(self):
        if USE_HISTORY and HISTORY_OFFLOADING:
            for a in self.content:
                a.check_hist()

    def from_str_bin(self, text: str):
        # number in string form
        text = text.split("b")[-1]
        for a in text:
            self.content.append(self._gen_bit(a))
        return self

    def from_num(self, num):
        # takes any number input
        # ensures everything is byte size via being multiple of 4 long
        val = bin(num).split('b')[-1]
        val = '0' * ((4 - len(val) % 4) % 4) + val
        for a in val:
            self.content.append(self._gen_bit(a))
        return self

    def from_text(self, text):
        # takes an ascii string to convert each letter
        # seems to work well with file bytes as well
        for a in text:
            self.from_num(ord(a))
        return self

    def from_bytes(self, data):
        for a in data:
            piece = "{:08b}".format(a)
            for b in piece:
                self.content.append(self._gen_bit(b))

    def to_str(self):
        # For converting data to string, good for printing
        vals = ''
        for a in self.content:
            a: Bit
            vals += str(a.val)
        return vals

    def to_hex(self):
        if len(self.content) % 4 != 0:
            raise ValueError('Partial bytes in data')
        val = hex(int(self.to_str(), 2))
        return val

    def shift_right(self, dist: int):
        for a in range(dist):
            self.content.insert(0, Bit(0))
            self.content.pop()
        return self

    def rotate_right(self, dist: int):
        for a in range(dist):
            self.content.insert(0, self.content.pop())
        return self

    def _is_valid_comp(self, other: "Array"):
        if type(other) != Array or len(self) != len(other):
            print('self', self.to_str(), len(self.to_str()))
            print('other', other.to_str(), len(other.to_str()))
            raise ValueError("Cannot Compare properly (not array or differing lengths)")

    def xor_op(self, other: "Array", many: bool = False):
        self._is_valid_comp(other)
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            val = 0 if todo[a].val == other[a].val else 1
            bit = Bit(val)
            if USE_HISTORY and not many:
                bit.history = f"(x{todo[a].history}{other[a].history})"
            self.content.append(bit)
        self._check_histories()
        return self

    def or_op(self, other: "Array", many: bool = False):
        self._is_valid_comp(other)
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            val = 1 if todo[a].val == 1 or other[a].val == 1 else 0
            bit = Bit(val)
            if USE_HISTORY and not many:
                bit.history = f"(o{todo[a].history}{other[a].history})"
        self._check_histories()
        return self

    def and_op(self, other: "Array", many: bool = False):
        # fixme self.content never gets reassigned
        self._is_valid_comp(other)
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            val = 1 if todo[a].val == 1 and other[a].val == 1 else 0
            bit = Bit(val)
            if USE_HISTORY and not many:
                bit.history = f"(a{todo[a].history}{other[a].history})"
        self._check_histories()
        return self

    # @profile
    def add_op(self, other: "Array"):
        # This assumes big endian iirc
        # does a complete add. will need to mod after func if desired
        self._is_valid_comp(other)
        todo = list(reversed(self.content))
        # print('todo', todo)
        other = list(reversed(other.content))
        self.content = []
        carry = 0
        carry_data = ""
        for a in range(len(todo)):
            # print("digit")
            val = todo[a].val + other[a].val + carry
            if val >= 2:
                carry = 1
                val -= 2
            else:
                carry = 0
            bit = Bit(val)
            if USE_HISTORY:
                # print(USE_HISTORY)
                if a == 0:
                    # todo not sure how much data I want here
                    carry_data = f"(x{todo[a].history}{other[a].history}0)"
                else:
                    # todo I think I need to clean the carry data to remove the xor from the previous roundn
                    carry_data = f"(x{todo[a].history}{other[a].history}(m{carry_data}))"
                    # carry_data = ""
                bit.history = carry_data
            self.content.append(bit)
        if USE_HISTORY:
            bit = Bit(carry)
            bit.history = f"(m{carry_data})"
            self.content.append(bit)
        elif carry == 1:
            bit = Bit(1)
            self.content.append(bit)
        self.content.reverse()
        self._check_histories()
        return self

    def copy(self):
        new = Array()
        for a in self.content:
            new.content.append(a.copy())
        return new


def xor_multi(*args: Array):
    thing = args[0]
    thing: Array
    new_hist = [a.history for a in thing]
    if len(args) > 1:
        for a in args[1:]:
            new_hist = [new_hist[num_b] + b.history for num_b, b in enumerate(a)]
            thing.xor_op(a)
    for a in range(len(new_hist)):
        thing[a].history = '(x' + new_hist[a] + ')'
    return thing


def and_multi(*args: Array):
    thing = args[0]
    thing: Array
    new_hist = [a.history for a in thing]
    if len(args) > 1:
        for a in args[1:]:
            new_hist = [new_hist[num_b] + b.history for num_b, b in enumerate(a)]
            thing.and_op(a)
    for a in range(len(new_hist)):
        thing[a].history = '(a' + new_hist[a] + ')'
    return thing


def or_multi(*args: Array):
    thing = args[0]
    thing: Array
    new_hist = [a.history for a in thing]
    if len(args) > 1:
        for a in args[1:]:
            new_hist = [new_hist[num_b] + b.history for num_b, b in enumerate(a)]
            thing.or_op(a)
    for a in range(len(new_hist)):
        thing[a].history = '(o' + new_hist[a] + ')'
    return thing


def add_mod(*args: Array):
    # todo make sure this is right, there may be issues with adding them one at a time
    if len(args) == 1:
        return args[0]
    thing = args[0]
    thing: Array
    max_len = len(thing)
    # if max_len == 33:
    #     quit('bad')
    for a in args[1:]:
        thing.add_op(a)
        if len(thing) > max_len:
            thing = thing[-max_len:]
    return thing


def choice(x: Array, y: Array, z: Array):
    new = Array()
    for a in range(len(x)):
        if x[a].val == 1:
            new.content.append(y[a])
        else:
            new.content.append(z[a])
        if USE_HISTORY:
            new.content[a].history = f"(c{x[a].history}{y[a].history}{z[a].history})"
    return new


def majority(x: Array, y: Array, z: Array):
    new = Array()
    for a in range(len(x)):
        if x[a].val + y[a].val + z[a].val > 1:
            bit = Bit(1)
        else:
            bit = Bit(0)
        if USE_HISTORY:
            bit.history = f"(m{x[a].history}{y[a].history}{z[a].history})"
        new.content.append(bit)
    return new


def main():
    # This is for testing purposes
    # print(bin(18))
    data = Array().from_text('abc')
    other_data = Array().from_text('bcd')
    data.content[0] = Bit(1)
    print(data.to_str())
    print(other_data.to_str())
    data.add_op(other_data)
    print(data[-2].history)


if __name__ == '__main__':
    main()
