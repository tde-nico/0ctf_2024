
def test_fun(arr, *args):
	if str(arr) == '0110100110010110100101100110100110010110011010010110100110010110':
		return args[0] ^ args[1] ^ args[2] ^ args[3] ^ args[4] ^ args[5]
	if str(arr) == '01101001100101101001011001101001':
		return args[0] ^ args[1] ^ args[2] ^ args[3] ^ args[4]
	if str(arr) == '0110100110010110':
		return args[0] ^ args[1] ^ args[2] ^ args[3]
	if str(arr) == '01101001':
		return args[0] ^ args[1] ^ args[2]
	if str(arr) == '0110':
		return args[0] ^ args[1]

tests = [64, 32, 16, 8, 4]
s = '0110100110010110100101100110100110010110011010010110100110010110'

for test in tests:
	for i in range(test):
		b0 = ((i >> 0) & 1)
		b1 = ((i >> 1) & 1)
		b2 = ((i >> 2) & 1)
		b3 = ((i >> 3) & 1)
		b4 = ((i >> 4) & 1)
		b5 = ((i >> 5) & 1)
		if int(s[i]) != test_fun(s[:test], b0, b1, b2, b3, b4, b5):
			print('FAIL', i, test)
			exit(1)
