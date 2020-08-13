import os
import sys

EXE_FILE = 'export'

def kill():
	os.system("ps aux | grep ython | grep %s | awk '{print $2}' | xargs kill -9" % EXE_FILE)

def setup(arg = ''):
	if arg == 'kill':
		kill()
		return
		
	RUN_COMMAND = "nohup python3 -u %s.py &" % EXE_FILE

	try:
		import yaml
		with open('TELEGRAPH_TOKENS') as f:
			TELEGRAPH_TOKENS = yaml.load(f, Loader=yaml.FullLoader)
	except:
		with open('TELEGRAPH_TOKENS', 'w') as f:
			f.write(yaml.dump({}, sort_keys=True, indent=2))

	kill()

	if arg.startswith('debug'):
		os.system(RUN_COMMAND[6:-2])
	else:
		os.system(RUN_COMMAND)
		if 'notail' not in sys.argv:
			os.system('touch nohup.out && tail -F nohup.out')


if __name__ == '__main__':
	if len(sys.argv) > 1:
		setup(sys.argv[1])
	else:
		setup('')