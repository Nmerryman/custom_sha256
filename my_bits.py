

"""
This was made specifically for working with the sha256 hash to better understand how it works
"""


USE_HISTORY = True


class Bit:

    def __init__(self, val: int):
        self.val: int = val
        if USE_HISTORY:
            self.history: str = f"<const>{self.val}</const>"
        else:
            self.history = ""

    def copy(self):
        new = Bit(self.val)
        new.history = self.history
        return new


class Array:
    # All conversions assume hex was given for leading zeros
    def __init__(self, bits=None):
        self.content = []
        if not bits:
            self.content = []
        elif type(bits) == str:
            self.from_str_num(bits)
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

    def from_str_num(self, text: str):
        # number in string form
        text = text.split("b")[-1].split('x')[-1]
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

    def to_str(self):
        # For converting data to string, good for printing
        vals = ''
        for a in self.content:
            a: Bit
            vals += str(a.val)
        return vals

    def shift_right(self, dist: int):
        todo = self.content
        self.content = []
        important = todo[:-dist]
        self.from_str_num("0" * dist)
        self.content.extend(important)
        return self

    def rotate_right(self, dist: int):
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            self.content.append(todo[(a - dist) % len(todo)])
        return self

    def _is_valid_comp(self, other: "Array"):
        if type(other) != Array or len(self) != len(other):
            print('self', self.to_str(), len(self.to_str()))
            print('other', other.to_str(), len(other.to_str()))
            raise ValueError("Cannot Compare properly (not array or differing lengths)")

    def xor_op(self, other: "Array"):
        self._is_valid_comp(other)
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            val = 0 if todo[a].val == other[a].val else 1
            bit = Bit(val)
            if USE_HISTORY:
                bit.history = f"<xor>{todo[a].history}{other[a].history}</xor>"
            self.content.append(bit)
        return self

    def or_op(self, other: "Array"):
        self._is_valid_comp(other)
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            val = 1 if todo[a].val == 1 or other[a].val == 1 else 0
            bit = Bit(val)
            if USE_HISTORY:
                bit.history = f"<or>{todo[a].history}{other[a].history}</or>"
        return self

    def and_op(self, other: "Array"):
        # fixme self.content never gets reassigned
        self._is_valid_comp(other)
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            val = 1 if todo[a].val == 1 and other[a].val == 1 else 0
            bit = Bit(val)
            if USE_HISTORY:
                bit.history = f"<and>{todo[a].history}{other[a].history}</and>"
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
                print(USE_HISTORY)
                if a == 0:
                    carry_data = f"<add><main>{todo[a].history}{other[a].history}</main><carry><const>0</const></carry></add>"
                else:
                    carry_data = f"<add><main>{todo[a].history}{other[a].history}</main><carry>{carry_data}</carry></add>"
                    # carry_data = ""
                bit.history = carry_data
            self.content.append(bit)
        if carry == 1:
            bit = Bit(1)
            if USE_HISTORY:
                bit.history = f"<add><main><const>0</const><const>0</const></main><carry>{carry_data}</carry></add>"
            self.content.append(bit)
        self.content.reverse()
        return self

    def copy(self):
        new = Array()
        for a in self.content:
            new.content.append(a.copy())
        return new


def xor_multi(*args: Array):
    if len(args) == 1:
        return args[0]
    thing = args[0]
    thing: Array
    for a in args[-1:]:
        thing.xor_op(a)
    return thing


def add_mod(*args: Array):
    # todo make sure this is right, there may be issues with adding them one at a time
    if len(args) == 1:
        return args[0]
    thing = args[0]
    thing: Array
    max_len = len(thing)
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
            new.content[a].history = f"<choice>{x[a].history}{y[a].history}{z[a].history}</choice>"
    return new


def majority(x: Array, y: Array, z: Array):
    new = Array()
    for a in range(len(x)):
        if x[a].val + y[a].val + z[a].val > 1:
            bit = Bit(1)
        else:
            bit = Bit(0)
        if USE_HISTORY:
            bit.history = f"<majority>{x[a].history}{y[a].history}{z[a].history}</majority>"
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
