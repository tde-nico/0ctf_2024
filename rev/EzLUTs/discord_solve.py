import lark
import z3

parser = lark.Lark(
r'''
start: (call | comment)*
comment: "(*" /(.|\n)/* "*)"

call: ident params CNAME args ";"

params: "#(" ".INIT(" INT "'h" HEXINT ")" ")"
args: "(" (arg ("," arg)*) ")"

arg: "." CNAME "(" var ")"
var: ident ("[" INT "]")?

ident: CNAME | ESCAPED_IDENTIFIER

HEXINT: HEXDIGIT+

ESCAPED_IDENTIFIER: /\\([^\s]+)/
%import common.CNAME
%import common.INT
%import common.HEXDIGIT
%import common.WS
%ignore WS
''', parser="lalr")

with open('ext.v', 'rt') as f:
    tree = parser.parse(f.read())

def get_ident(tree):
    assert tree.data == 'ident'
    return tree.children[0].value

def extract_var(tree):
    assert tree.data == 'var'
    ident = get_ident(tree.children[0])
    if len(tree.children) == 1:
        return ident, None
    assert tree.children[1].type == 'INT'
    return ident, int(tree.children[1].value)

def extract_args(tree):
    assert tree.data == 'args'
    output = tree.children.pop()
    assert output.children[0].value == 'O'
    output = extract_var(output.children[1])
    args = []
    for i, child in enumerate(tree.children):
        assert child.children[0].value == f'I{i}'
        args.append(extract_var(child.children[1]))
    return tuple(args), output

SYMBOL = {}
def get_symbol(arg):
    if arg not in SYMBOL:
        name, ind = arg
        if ind is None:
            SYMBOL[arg] = z3.Bool(name)
        else:
            SYMBOL[arg] = z3.Bool(f'{name}[{ind}]')
    return SYMBOL[arg]

def xor(bits1, bits2):
    assert len(bits1) == len(bits2)
    return [a ^ b for a, b in zip(bits1, bits2)]

def mirrored(bits):
    assert len(bits) % 2 == 0
    half = len(bits) // 2
    for i in range(half):
        if bits[i] == bits[half + i]:
            return False
    return True

def all_zero(bits):
    return all(b == 0 for b in bits)

def pattern_gen(bits, args):
    if len(bits) == 1:
        return z3.BoolVal(bits[0]),

    half = len(bits) // 2

    if all_zero(bits[:half]):
        return args[0], *pattern_gen(bits[half:], args[1:])

    if all_zero(bits[half:]):
        return z3.Not(args[0]), *pattern_gen(bits[:half], args[1:])
    
    if mirrored(bits):
        return z3.Xor(args[0], z3.And(*pattern_gen(bits[:half], args[1:]))),
    
    assert half >= 2

    a1, *a2 = pattern_gen(bits[:half], args[1:])
    b1, *b2 = pattern_gen(bits[half:], args[1:])

    assert len(a2) == len(b2)
    assert all(z3.eq(a, b) for a, b in zip(a2, b2))

    if z3.eq(a1, z3.Not(b1)):
        return args[0] == b1, *a2
    elif z3.eq(z3.Not(a1), b1):
        return z3.Not(args[0] == a1), *a2
    
    raise NotImplementedError(f'init={hex(init)}, bits={bits}')

assigned = {}

for rule in tree.children:
    if rule.data != 'call':
        continue
    assert len(rule.children) == 4 # (ident, params, CNAME, args)
    lut_name = get_ident(rule.children[0])
    assert lut_name.startswith('LUT')
    lut_size = int(lut_name[3:])
    assert len(rule.children[3].children) == lut_size + 1
    bytes_size = 1 << lut_size
    assert int(rule.children[1].children[0].value) == bytes_size

    init = int(rule.children[1].children[1].value, 16)
    args, out = extract_args(rule.children[3])
    assert out not in assigned
    try:
        pat = pattern_gen([(init >> i) & 1 for i in range(bytes_size)], tuple(map(get_symbol, reversed(args))))
    except:
        print('Failed to generate pattern for', rule.children[2].value)
        raise
    pat = z3.And(*pat)
    # print(hex(init), args)
    # print(z3.simplify(pat))
    assigned[out] = pat

flag_bits = []

for i in range(336):
    name = get_symbol(('data_IBUF', i))
    assert name not in assigned
    flag_bits.append(name)

solver = z3.Solver()

# 0ops{aadc337c-b5a0-4ff0-ad94-9d1cf41956f4}
for i in range(0, 336, 8):
    solver.add(z3.Not(flag_bits[i]))
    solver.add(flag_bits[i + 2])

def add_known(i, c):
    for j in range(8):
        if (c >> (7 - j)) & 1:
            solver.add(flag_bits[i * 8 + j])
        else:
            solver.add(z3.Not(flag_bits[i * 8 + j]))

for i, c in enumerate(b'0ops{'):
    add_known(i, c)

add_known(41, ord('}'))
for i in (13, 18, 23, 28):
    add_known(i, ord('-'))

for name, pat in assigned.items():
    solver.add(get_symbol(name) == pat)

solver.add(get_symbol(('success_OBUF', None)))

assert solver.check() == z3.sat
model = solver.model()

for v in flag_bits:
    print('1' if bool(model[v]) else '0', end='')