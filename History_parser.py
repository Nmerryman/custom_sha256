import os
import logging
import time
import datetime


logging.basicConfig()
logger = logging.getLogger(__name__)

val_cache = {}
node_cache = {}
node_count = 0


def goto_dir(name: str):
    if not os.path.isdir(name):
        os.mkdir(name)
    os.chdir(name)


def split_paren(text: str):
    depth = 1
    index = 1
    while depth > 0:
        if text[index] == '(':
            depth += 1
        elif text[index] == ')':
            depth -= 1
        index += 1
    out = []
    sub = []
    in_sub = False
    # print(depth)
    for a in text[1: index]:
        # print(depth)
        if a != '(' and a != ')' and not in_sub:
            out.append(a)
        elif a == '(':
            sub.append(a)
            depth += 1
            in_sub = True
        elif a == ')':
            sub.append(a)
            depth -= 1
            if depth == 0:
                out.append("".join(sub))
                sub = []
                in_sub = False
        else:
            sub.append(a)
    # print(depth)
    return out


def ask_data(name: str):
    # todo cache the lookup system
    if name in val_cache:
        # print('cache used ' + name)
        return val_cache[name]
    # asked = input(f"Data from {name}>")
    asked = '1' if '8' in name else '0'
    val_cache[name] = asked
    return asked


def file_data(name: str):
    with open(name, 'r') as f:
        text = f.read()
    return split_paren(text)


class Node:
    """comp ops are assumed to be bits"""

    def __init__(self, op: str, unparsed: list):
        global node_count
        node_count += 1
        if node_count % 1000000 == 0:
            logger.info(f"{node_count} Nodes at {datetime.datetime.now()}")
        self.op = op
        self.vals = []
        self.result = None
        for a in unparsed:
            if "(" in a:
                temp = split_paren(a)
                self.vals.append(Node(temp[0], temp[1:]))
            else:
                self.vals.append(a)

    def eval(self):
        global node_cache

        if self.result:
            return self.result
        data = []
        for a in self.vals:
            if type(a) == Node:
                data.append(a.eval())
            else:
                data.append(a)
        if type(data[0]) == Node:
            logger.warning(f"{self.vals} to {data}")
        if self.op == 'a':
            if '0' in data:
                self.result = '0'
                return '0'
            self.result = '1'
            return '1'

        elif self.op == 'x':
            self.result = str(sum(map(int, data)) % 2)
            return self.result

        elif self.op == 'o':
            if '1' in data:
                self.result = '1'
                return '1'
            self.result = '0'
            return '0'

        elif self.op == 'm':
            self.result = '1' if sum(map(int, data)) >= 2 else '0'
            return self.result

        elif self.op == 'c':
            if data[0] == '1':
                self.result = data[1]
                return data[1]
            self.result = data[2]
            return data[2]

        elif self.op == 'b':
            self.result = ask_data(self.op + "".join(data))
            return self.result

        elif self.op == 'f':
            if "".join(self.vals) not in node_cache:
                data = file_data("".join(self.vals))
                new = Node(data[0], data[1:])
                node_cache["".join(self.vals)] = new
            else:
                new = node_cache["".join(self.vals)]

            return new.eval()

    def nest(self):
        pass



def tests():
    assert split_paren('(a)') == ['a']
    assert split_paren('((a))') == ['(a)']
    assert split_paren('(a(ba))') == ['a', '(ba)']
    assert split_paren('(ab((c)d))') == ['a', 'b', '((c)d)']
    assert split_paren('(a((b)c)d)') == ['a', '((b)c)', 'd']
    assert split_paren('(a(b)(c))') == ['a', '(b)', '(c)']
    print("Split works")

    assert Node('x', ['1', '0', '(x0011)']).eval() == '1'
    assert Node('a', ['(a(a1)1110)']).eval() == '0'
    assert Node('m', ['(o10)', '(a11111110)', '(m000)']).eval() == '0'
    print('Eval works')

    for a in ('1', '10', "100", "1000", "1000"):
        start = time.time()
        print(a, datetime.datetime.now())
        print(Node('f', a.split()).eval())
        print(f'{time.time() - start}s')

    print('passed tests')
    quit()


def main():
    with open('16092', 'r') as f:
        text = f.read()
    # text = '(ab((c)d))'
    # text = '(m(x(b12)35)1(b2))'
    print(text)
    split = split_paren(text)
    node = Node(split[0], split[1:])
    print(node.vals)
    print(node.eval())
    print('done')


if __name__ == '__main__':
    goto_dir('temp_data')
    logger.setLevel(logging.INFO)
    tests()
    main()
