import os
import sys

def setup(mode = 'normal'):
	RUN_COMMAND = 'nohup python3 export.py &'

	try:
		with open('TOKEN') as f:
			TOKEN = f.readline().strip()
	except:
		print('FAIL. Please save your telebot token in TOKEN file')
		return

	if mode != 'restart' and mode != 'debug':
		os.system('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py')
		os.system('python3 get-pip.py')
		os.system('rm get-pip.py')

		os.system('pip3 install --upgrade pip --user')
		os.system('pip3 install -r requirements.txt')
		os.system('pip3 install python-telegram-bot --upgrade') # need to use some experiement feature, e.g. message filtering
		os.system('pip3 install export_to_telegraph --upgrade')

	# kill the old running bot if any. If you need two same bot running in one machine, use mannual command instead
	os.system("ps aux | grep python | grep export.py | awk '{print $2}' | xargs kill -9")

	if mode == 'debug':
		os.system(RUN_COMMAND[6:-2])
	else:
		os.system(RUN_COMMAND)


if __name__ == '__main__':
	if len(sys.argv) > 1:
		setup(sys.argv[1])
	else:
		setup()