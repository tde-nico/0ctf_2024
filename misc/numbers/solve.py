import string

data = [
	200264, 17360, 200266, 3575, 553, 261, 10297, 29186, 200265,
	200264, 1428, 200266, 8256, 5485, 668, 290, 9641, 13, 200265,
	200264, 173781, 200266, 62915, 0, 7306, 382, 290, 9641, 25, 220, 15, 4645, 90, 67, 15, 22477, 15, 84, 62, 7316, 91, 15, 37313, 62, 10, 72, 42, 10, 525, 18, 77, 16, 57, 18, 81, 30, 92, 200265,
	200264, 1428, 200266, 13659, 481, 0, 200265,
	200264, 173781, 200266, 15334, 261, 1899, 1058, 540, 220, 15, 308, 69, 1323, 19, 0, 200265,
]

known = {
	200264: '<|im_start|>',
	200265: '<|im_end|>',
	200266: '<|im_sep|>',
	17360: 'system',
	173781: 'assistant',
	1428: 'user',
	3575: 'You',
	553: ' are',
	261: ' a',
	10297: ' helpful',
	29186: ' assistant',
}

'''
15, 4645, 90, 67, 15, 22477, 15, 84, 62, 7316, 91, 15, 37313, 62, 10, 72, 42, 10, 525, 18, 77, 16, 57, 18, 81, 30, 92
'''

for i, c in enumerate(string.ascii_lowercase, start=64):
	known[i] = c

for i, c in enumerate(string.ascii_uppercase, start=32):
	known[i] = c

for i, c in enumerate(string.digits, start=15):
	known[i] = c

known[4645] = 'ops'
known[90] = '{'
known[92] = '}'
known[62] = '_'
known[22477] = '_Y'
known[30] = '?'
known[10] = '+'
known[91] = '|'
known[525] = 'ok'
known[7316] = 'kr'
known[37313] = 'vv'


for d in data:
	print(known.get(d, ' '), end='')
print()

# 0ops{d0_Y0u_kr|0vv_+iK+ok3n1Z3r?}
