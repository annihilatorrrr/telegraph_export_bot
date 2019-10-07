import os
import sys

def setup(token):
	RUN_COMMAND = 'nohup python3 telegraph_bot.py &'

	TOKEN = ''
	try:
		with open('TOKEN') as f:
			TOKEN = f.readline().strip()
	except:
		pass

	if not TOKEN and not token:
		print('ERROR: please run as `python setup.py YOUR_TOKEN`.')
		return

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
		from html_telegraph_poster import TelegraphPoster
		t = TelegraphPoster()
		r = t.create_api_token('dushufenxiang', 'dushufenxiang', 'https://t.me/dushufenxiang_chat')
		with open('TELEGRAPH_TOKEN', 'w') as f:
			f.write(r['access_token'])
		print('Please use this url to login to your telegraph account on your browser. Link will expire in a few minutes.' + r['auth_url'])

	return os.system(RUN_COMMAND)


if __name__ == "__main__":
	if len(sys.argv) > 1:
    	setup(sys.argv[1])
    else:
    	setup('')