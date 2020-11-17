import os
import sys

def kill():
	os.system("ps aux | grep ython | grep export.py | awk '{print $2}' | xargs kill -9")

def setup(arg = ''):
	kill()
	if arg == 'kill':
		return
		
	RUN_COMMAND = "nohup python3 -u export.py &" % 

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