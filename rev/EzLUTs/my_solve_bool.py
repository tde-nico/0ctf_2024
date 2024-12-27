from Crypto.Util.number import long_to_bytes
from z3 import *


DEBUG = 0
OPTIMIZE = 1
BITS = 1


with open('EzLUTs_top_synth.v', 'r') as f:
	lines = f.readlines()

LEN = 42
BITLEN = LEN * 8

s = Solver()
# data = [BitVec(f'data[{i}]', BITS) for i in range(BITLEN)]
# data_enc = [BitVec(f'data_enc[{i}][{j}]', BITS) for i in range(BITLEN) for j in range(8)]
# successes = [BitVec(f'success_{i}', BITS) for i in range(1474)]
data = [Bool(f'data[{i}]') for i in range(BITLEN)]
data_enc = [Bool(f'data_enc[{i}][{j}]') for i in range(BITLEN) for j in range(8)]
successes = [Bool(f'success_{i}') for i in range(1474)]
inits = {}

# for i in range(BITLEN):
# 	s.add(data[i] >= 0)
# 	s.add(data[i] <= 1)
# for i in range(BITLEN):
# 	for j in range(8):
# 		s.add(data_enc[i * 8 + j] >= 0)
# 		s.add(data_enc[i * 8 + j] <= 1)
# for i in range(1474):
# 	s.add(successes[i] >= 0)
# 	s.add(successes[i] <= 1)


def translate_var(in_var):
	if 'success_OBUF_inst_i_' in in_var:
		return in_var.replace('success_OBUF_inst_i_', 'success_').replace('_n_0', '')
	elif 'data_IBUF' in in_var:
		return in_var.replace('data_IBUF', 'data')
	elif 'success_OBUF' in in_var:
		return in_var.replace('success_OBUF', 'success')
	elif '\data_enc' in in_var:
		tmp = in_var.split('[')
		return f'data_enc[{int(tmp[1][:-2]) * 8 + int(tmp[2][:-1])}]'
	else:
		print('Error: Unkown variable')
		print(in_var)
		exit(1)


def parse_var(line, out=False):
	if out:
		var = line[11:-4]
	else:
		var = line[12:-3]
	var = translate_var(var)

	if var == 'success':
		# return 1
		return True
	elif var.startswith('success_'):
		return successes[int(var[8:])]
	elif var.startswith('data_enc'):
		return data_enc[int(var[9:-1])]
	elif var.startswith('data'):
		return data[int(var[5:-1])]

	print('Error: Unkown variable')
	print(var)
	exit(1)


def parse_init(line, bits):
	if bits < 10:
		init = line[13:(13+bits//4)]
	else:
		init = line[14:(14+bits//4)]
	init = int(init, 16)
	init = bin(init)[2:].rjust(bits, '0')
	init = init[::-1]

	if init in inits:
		return inits[init]

	# sym_arr = Array(init, BitVecSort(6), BitVecSort(BITS))
	sym_arr = Array(init, IntSort(), BoolSort())
	for i, elem in enumerate(init):
		# print(sym_arr[i] == int(elem))
		# s.add(sym_arr[i] == int(elem))
		el = True if int(elem) else False
		s.add(sym_arr[i] == el)
		
	inits[init] = sym_arr
	return sym_arr


def index(arr, *args):
	if OPTIMIZE > 0:
		s_arr = str(arr)
		if s_arr == '0110100110010110100101100110100110010110011010010110100110010110':
			return args[0] ^ args[1] ^ args[2] ^ args[3] ^ args[4] ^ args[5]
		if s_arr == '01101001100101101001011001101001':
			return args[0] ^ args[1] ^ args[2] ^ args[3] ^ args[4]
		if s_arr == '0110100110010110':
			return args[0] ^ args[1] ^ args[2] ^ args[3]
		if s_arr == '01101001':
			return args[0] ^ args[1] ^ args[2]
		if s_arr == '0110':
			return args[0] ^ args[1]

	# if str(arr) == '0000000000000000000000000000000000000000000000000000000000000001':
	# 	return args[0] & args[1] & args[2] & args[3] & args[4] & args[5]
	# if str(arr) == '0000000000000000000000000000000000000000000000000001000000000000':
	# 	return args[0] & args[1] & ~args[2] & ~args[3] & args[4] & args[5]
	# if str(arr) == '0000000000000000000000000000000000001000000000000000000000000000':
	# 	return ~args[0] & ~args[1] & args[2] & ~args[3] & ~args[4] & args[5]
	# if str(arr) == '0000000000000000000000000000000000000001000000000000000000000000':
	# 	return args[0] & args[1] & args[2] & ~args[3] & ~args[4] & args[5]
	# if str(arr) == '0000000000000000000000000000000010000000000000000000000000000000':
	# 	return ~args[0] & ~args[1] & ~args[2] & ~args[3] & ~args[4] & args[5]
	# if str(arr) == '0100000000000000000000000000000000000000000000000000000000000000':
	# 	return args[0] & ~args[1] & ~args[2] & ~args[3] & ~args[4] & ~args[5]
	
	if OPTIMIZE > 1:
		if s_arr.count('1') == 1:
			l = len(s_arr)
			i = s_arr.find('1')
			b5 = ((i >> 5) & 1)
			b4 = ((i >> 4) & 1)
			b3 = ((i >> 3) & 1)
			b2 = ((i >> 2) & 1)
			b1 = ((i >> 1) & 1)
			b0 = ((i >> 0) & 1)
			if l > 32: a5 = args[5] if b5 else ~args[5]
			if l > 16: a4 = args[4] if b4 else ~args[4]
			if l > 8: a3 = args[3] if b3 else ~args[3]
			if l > 4: a2 = args[2] if b2 else ~args[2]
			a1 = args[1] if b1 else ~args[1]
			a0 = args[0] if b0 else ~args[0]
			if l > 32: return a0 & a1 & a2 & a3 & a4 & a5
			if l > 16: return a0 & a1 & a2 & a3 & a4
			if l > 8: return a0 & a1 & a2 & a3
			if l > 4: return a0 & a1 & a2
			return a0 & a1

	# print(arr)

	# idx = ZeroExt(6-BITS, args[0])
	idx = args[0]
	# print(idx.sort())
	for i in range(1, len(args)):
		# tmp = ZeroExt(6-BITS, args[i])
		tmp = args[i]
		# print(tmp.sort())
		idx += tmp * (2 ** i)
	# print(idx)
	# print(arr[idx])
	return arr[idx]


cycles = 0
i = 22
while i < len(lines):
	cycles += 1
	# if cycles > 1682:
	# 	break
	# if cycles > 1690:
	# 	break
	if cycles > 2980:
		break

	curr = lines[i].strip()
	if curr == '':
		i += 1
		continue

	keyword = curr.split()[0]
	if keyword == 'wire':
		i += 1
		continue

	elif keyword == 'IBUF':
		i += 3
		continue

	elif keyword == 'OBUF':
		i += 3
		continue

	elif keyword == '(*':
		i += 1
		continue

	elif keyword == 'LUT6':
		init = parse_init(lines[i+1], 64)
		i0 = parse_var(lines[i+3])
		i1 = parse_var(lines[i+4])
		i2 = parse_var(lines[i+5])
		i3 = parse_var(lines[i+6])
		i4 = parse_var(lines[i+7])
		i5 = parse_var(lines[i+8])
		o = parse_var(lines[i+9], True)
		idx = index(init, i0, i1, i2, i3, i4, i5)
		if DEBUG:
			print(init, i0, i1, i2, i3, i4, i5, o)
			print(idx)
		s.add(idx == o)
		i += 10
		continue

	elif keyword == 'LUT5':
		init = parse_init(lines[i+1], 32)
		i0 = parse_var(lines[i+3])
		i1 = parse_var(lines[i+4])
		i2 = parse_var(lines[i+5])
		i3 = parse_var(lines[i+6])
		i4 = parse_var(lines[i+7])
		o = parse_var(lines[i+8], True)
		idx = index(init, i0, i1, i2, i3, i4)
		if DEBUG:
			print(init, i0, i1, i2, i3, i4, o)
			print(idx)
		s.add(idx == o)
		i += 9
		continue

	elif keyword == 'LUT4':
		init = parse_init(lines[i+1], 16)
		i0 = parse_var(lines[i+3])
		i1 = parse_var(lines[i+4])
		i2 = parse_var(lines[i+5])
		i3 = parse_var(lines[i+6])
		o = parse_var(lines[i+7], True)
		idx = index(init, i0, i1, i2, i3)
		if DEBUG:
			print(init, i0, i1, i2, i3, o)
			print(idx)
		s.add(idx == o)
		i += 8
		continue

	elif keyword == 'LUT3':
		init = parse_init(lines[i+1], 8)
		i0 = parse_var(lines[i+3])
		i1 = parse_var(lines[i+4])
		i2 = parse_var(lines[i+5])
		o = parse_var(lines[i+6], True)
		idx = index(init, i0, i1, i2)
		if DEBUG:
			print(init, i0, i1, i2, o)
			print(idx)
		s.add(idx == o)
		i += 7
		continue

	elif keyword == 'LUT2':
		init = parse_init(lines[i+1], 4)
		i0 = parse_var(lines[i+3])
		i1 = parse_var(lines[i+4])
		o = parse_var(lines[i+5], True)
		idx = index(init, i0, i1)
		if DEBUG:
			print(init, i0, i1, o)
			print(idx)
		s.add(idx == o)
		i += 6
		continue

	elif keyword == 'endmodule':
		break


	print('Error: Unkown keyword')
	print(curr)
	print(keyword)
	exit(1)


FLAG_FORMAT = '0ops{'
for i, c in enumerate(FLAG_FORMAT):
	byte = bin(ord(c))[2:].rjust(8, '0')
	# print(byte)
	byte = byte[::-1]
	for j, b in enumerate(byte):
		tmp = True if int(b) else False
		# print(BITLEN - 1 - (i * 8 + j), b)
		# s.add(data[BITLEN - 1 - (i * 8 + j)] == int(b))
		s.add(data[BITLEN - 1 - (i * 8 + j)] == tmp)

END_FORMAT = '}'
for i, c in enumerate(END_FORMAT, start=LEN-len(END_FORMAT)):
	byte = bin(ord(c))[2:].rjust(8, '0')
	byte = byte[::-1]
	for j, b in enumerate(byte):
		tmp = True if int(b) else False
		# print(BITLEN - 1 - (i * 8 + j), b)
		# s.add(data[BITLEN - 1 - (i * 8 + j)] == int(b))
		s.add(data[BITLEN - 1 - (i * 8 + j)] == tmp)

for i in range(LEN):
	# s.add(data[i * 8] == 0)
	s.add(data[i * 8] == False)
	s.add(data[i * 8 + 2] == True)





hex_bin = []
for i in '0123456789abcdef-':
	hex_bin.append(bin(ord(i))[2:].rjust(8, '0')[::-1])

def make_hex(byte):
	hex_bin_eqs = []
	for h in hex_bin:
		tmp = []
		for j, b in enumerate(h):
			if j in [5, 7]:
				continue

			bool_var = True if int(b) else False
			tmp.append(data[BITLEN - 1 - (byte * 8 + j)] == bool_var)
		hex_bin_eqs.append(And(tmp))
	s.append(Or(hex_bin_eqs))

# def make_dash(byte):
# 	tmp = []
# 	for j, b in enumerate(hex_bin[-1][::-1]):
# 		bool_var = True if int(b) else False
# 		tmp.append(data[BITLEN - 1 - (byte * 8 + j)] == bool_var)
# 	s.check(And(tmp))

for i in range(5, LEN-1):
	make_hex(i)

# s.add(data[142] == False)
# s.add(data[143] == True)

# s.add(data[257] == False)
# s.add(data[316] == False)



# # UNSAT
# s.add(data[297] == True)


print('Checking...')
if s.check() == sat:
	print('SAT')
	m = s.model()

	try:
		bits = [str(m[data[i]]) for i in range(BITLEN)]
		# bits = [str(m[data[i]].as_long()) for i in range(BITLEN)]
		#bits = bits[::-1]
		bits = [bits[i:i+8] for i in range(0, len(bits), 8)]
		bits = [''.join(byte) for byte in bits]
		bits = [byte.replace('True', '1').replace('False', '0') for byte in bits]
		bits = bits[::-1]
		for byte in bits:
			try:
				print(str(long_to_bytes(int(byte, 2)))[2:-1], end='')
			except Exception as e:
				# print(e)
				print('?', end='')
		print()
		for byte in bits:
			print(byte, end=' ')
		print()
		# joined = ''.join(bits)
		# print(joined)
		# print(int(joined, 2).to_bytes(42, 'big'))
		# print(long_to_bytes(int(joined, 2)))
		# print(long_to_bytes(int(joined, 2))[::-1])
	except Exception as e:
		print(e)
	
	# while True:
	# 	try:
	# 		print(exec(input('> ')))
	# 	except KeyboardInterrupt:
	# 		break
	# 	except Exception as e:
	# 		print(e)

else:
	print('UNSAT')
