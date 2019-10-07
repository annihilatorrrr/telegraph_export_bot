import os
import sys
from html_telegraph_poster import TelegraphPoster

def setup(token):
	RUN_COMMAND = 'nohup python3 telegraph_bot.py &'

	TOKEN = ''
	try:
		with open('TOKEN') as f:
			TOKEN = f.readline().strip()
	except:
		pass

	if TOKEN != token:
		PIP_COMMAND = 'pip3 install -r requirements.txt'
		os.system(PIP_COMMAND)

		UPGRADE_TELE_BOT = 'pip3 install python-telegram-bot --upgrade'
		os.system(UPGRADE_TELE_BOT) # need to use some experiement feature, e.g. message filtering

		with open('TOKEN', 'w') as f:
			f.write(token)

	TELEGRAPH_TOKEN = ''
	try:
		with open('TELEGRAPH_TOKEN') as f:
			TELEGRAPH_TOKEN = f.readline().strip()
	except:
		pass

	if not TELEGRAPH_TOKEN:
		t = TelegraphPoster()
		r = t.create_api_token('dushufenxiang', 'dushufenxiang', 'https://t.me/dushufenxiang_chat')
		with open('TELEGRAPH_TOKEN', 'w') as f:
			f.write(r['access_token'])
		print(r['auth_url'])

	return os.system(RUN_COMMAND)


if __name__ == "__main__":
    setup(sys.argv[1])