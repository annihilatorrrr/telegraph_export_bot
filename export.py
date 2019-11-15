#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import requests
import json
import export_to_telegraph
from html_telegraph_poster import TelegraphPoster
import yaml
from telegram_util import getDisplayUser, matchKey, log_on_fail

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(CREDENTIALS['bot_token'], use_context=True)

r = tele.bot.send_message(-1001198682178, 'test')
r.delete()
debug_group = r.chat

known_users = [420074357]

try:
	with open('TELEGRAPH_TOKENS') as f:
		TELEGRAPH_TOKENS = json.load(f)
except:
	TELEGRAPH_TOKENS = {}

def saveTelegraphTokens():
	with open('TELEGRAPH_TOKENS', 'w') as f:
		f.write(json.dumps(TELEGRAPH_TOKENS, sort_keys=True, indent=2))

def msgTelegraphToken(msg, id):
	if str(id) in TELEGRAPH_TOKENS:
		p = TelegraphPoster(access_token = TELEGRAPH_TOKENS[str(id)])
	else:
		p = TelegraphPoster()
		r = p.create_api_token(msg.from_user.first_name, msg.from_user.username)
		TELEGRAPH_TOKENS[str(id)] = r['access_token']
		saveTelegraphTokens()
	msgAuthUrl(msg, p)

def msgAuthUrl(msg, p):
	r = p.get_account_info(fields=['auth_url'])
	msg.reply_text('Use this url to login in 5 minutes: ' + r['auth_url'])

def getTelegraph(msg, url):
	usr_id = msg.from_user.id
	if str(usr_id) not in TELEGRAPH_TOKENS:
		msgTelegraphToken(msg, usr_id)
	export_to_telegraph.token = TELEGRAPH_TOKENS[str(usr_id)]
	return export_to_telegraph.export(url)

@log_on_fail(debug_group)
def export(update, context):
	msg = update.message
	for item in msg.entities:
		if (item["type"] == "url"):
			url = msg.text[item["offset"]:][:item["length"]]
			if not '://' in url:
				url = "https://" + url
			u = getTelegraph(msg, url)
			msg.reply_text(u)
			if msg.from_user not in known_users:
				r = debug_group.send_message( 
					text=getDisplayUser(msg.from_user) + ': ' + u, 
					parse_mode='Markdown')

@log_on_fail(debug_group)
def command(update, context):
	if matchKey(update.message.text, ['auth', 'token']):
		id = update.message.from_user.id
		return msgTelegraphToken(update.message, id)
	return update.message.reply_text('Feed me link, currently support wechat, bbc, stackoverflow, NYT, and maybe more')

tele.dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, export))
tele.dispatcher.add_handler(MessageHandler(Filters.private & Filters.command, command))

tele.start_polling()
tele.idle()