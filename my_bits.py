

"""
This was made specifically for working with the sha256 hash to better understand how it works
"""


class Bit:

    def __init__(self, val: int):
        self.val: int = val
        self.history: str = f"<const>{self.val}</const>"


class Array:
    # All conversions assume hex was given for leading zeros
    def __init__(self, bits=None):
        self.content = []
        if not bits:
            self.content = []
        elif type(bits) == str:
            self.from_str(bits)
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
        return self.content[item]

    @staticmethod
    def _gen_bit(val):
        # No safety checks in here
        # Might be able to do it all in 1 line rn
        if type(val) == int:
            return Bit(val)
        elif type(val) == str:
            return Bit(int(val))

    def from_str(self, text: str):
        text = text.split("b")[-1].split('x')[-1]
        for a in text:
            self.content.append(self._gen_bit(a))
        return self

    def from_num(self, num):
        val = bin(num).split('b')[-1]
        val = '0' * ((4 - len(val) % 4) % 4) + val
        for a in val:
            self.content.append(self._gen_bit(a))
        return self

    def from_text(self, text):
        for a in text:
            self.from_num(ord(a))
        return self

    def to_str(self):
        vals = ''
        for a in self.content:
            a: Bit
            vals += str(a.val)
        return vals

    def shift_right(self, dist: int):
        todo = self.content
        self.content = []
        important = todo[:-dist]
        self.from_str("0" * dist)
        for a in important:
            self.content.append(a)
        return self

    def rotate_right(self, dist: int):
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            self.content.append(todo[(a - dist) % len(todo)])
        return self

    def _is_valid_comp(self, other: "Array"):
        if type(other) != Array or len(self) != len(other):
            raise ValueError("Cannot Compare properly (not array or differing lengths)")

    def xor_op(self, other: "Array"):
        self._is_valid_comp(other)
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            val = 0 if todo[a].val == other[a].val else 1
            bit = Bit(val)
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
            bit.history = f"<or>{todo[a].history}{other[a].history}</or>"
        return self

    def and_op(self, other: "Array"):
        self._is_valid_comp(other)
        todo = self.content
        self.content = []
        for a in range(len(todo)):
            val = 1 if todo[a].val == 1 and other[a].val == 1 else 0
            bit = Bit(val)
            bit.history = f"<and>{todo[a].history}{other[a].history}</and>"
        return self

    def add_op(self, other: "Array"):
        self._is_valid_comp(other)
        todo = list(reversed(self.content))
        other = list(reversed(other.content))
        self.content = []
        carry = 0
        carry_data = ""
        for a in range(len(todo)):
            val = todo[a].val + other[a].val + carry
            if val >= 2:
                carry = 1
                val -= 2
            else:
                carry = 0
            bit = Bit(val)
            if a == 0:
                carry_data = f"<add><main>{todo[a].history}{other[a].history}</main><carry><const>0</const></carry></add>"
            else:
                carry_data = f"<add><main>{todo[a].history}{other[a].history}</main><carry>{carry_data}</carry></add>"
            bit.history = carry_data
            self.content.append(bit)
        if carry == 1:
            bit = Bit(1)
            bit.history = carry_data
            self.content.append(bit)
        self.content.reverse()
        return self


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
