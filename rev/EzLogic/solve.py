import subprocess
import string

cmd = "./EzLogic"
compile_cmd = 'iverilog -s EzLogic_tb -o EzLogic ./problem/EzLogic_top_synth.v ./problem/EzLogic_tb.v  ./behavioral\ models/*.v 2>&1'
file = './problem/EzLogic_tb.v'

data_out = bytes.fromhex('30789d5692f2fe23bb2c5d9e16406653b6cb217c952998ce17b7143788d949952680b4bce4c30a96c753')

flag = '0ops{'
for i in range(len(flag), 42):
	for char in string.printable[:-6]:
		line = (flag + char).ljust(42, '.')
		line = f'    parameter FLAG_TO_TEST = "{line}",'

		with open(file, 'r') as f: 
			data = f.readlines() 
		data[3] = line + '\n'
		with open(file, 'w') as f: 
			f.writelines(data) 

		p = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, shell=True)
		p.communicate()
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
		res = p.communicate()[0].strip().decode().split('\n')[1]
		print(flag+char, res)
		
		tmp = bytes.fromhex(res)
		if tmp[i] == data_out[i]:
			flag += char
			break

# 0ops{aadc337c-b5a0-4ff0-ad94-9d1cf41956f4}

