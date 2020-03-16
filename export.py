#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import export_to_telegraph
from html_telegraph_poster import TelegraphPoster
import yaml
from telegram_util import getDisplayUser, matchKey, log_on_fail, getDisplayChat

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(CREDENTIALS['bot_token'], use_context=True)

r = tele.bot.send_message(-1001198682178, 'start')
r.delete()
debug_group = r.chat

known_users = [420074357, 652783030, -1001399998441]

with open('TELEGRAPH_TOKENS') as f:
	TELEGRAPH_TOKENS = {}
	for k, v in yaml.load(f, Loader=yaml.FullLoader).items():
		TELEGRAPH_TOKENS[int(k)] = v

def saveTelegraphTokens():
	with open('TELEGRAPH_TOKENS', 'w') as f:
		f.write(yaml.dump(TELEGRAPH_TOKENS, sort_keys=True, indent=2))

def getSource(msg):
	if msg.from_user:
		return msg.from_user.id, getDisplayUser(msg.from_user) 
	return msg.chat_id, getDisplayChat(msg.chat)

def msgTelegraphToken(msg):
	source_id, _ = getSource(msg)
	if user_id in TELEGRAPH_TOKENS:
		p = TelegraphPoster(access_token = TELEGRAPH_TOKENS[user_id])
	else:
		p = TelegraphPoster()
		r = p.create_api_token(msg.from_user.first_name, msg.from_user.username)
		TELEGRAPH_TOKENS[user_id] = r['access_token']
		saveTelegraphTokens()
	msgAuthUrl(msg, p)

def msgAuthUrl(msg, p):
	r = p.get_account_info(fields=['auth_url'])
	msg.reply_text('Use this url to login in 5 minutes: ' + r['auth_url'])

def getTelegraph(msg, url):
	source_id, _ = getSource(msg)
	if source_id not in TELEGRAPH_TOKENS:
		msgTelegraphToken(msg)
	export_to_telegraph.token = TELEGRAPH_TOKENS[user_id]
	return export_to_telegraph.export(url, True, force = True)

def exportImp(msg):
	new_text = msg.text
	links = []
	for item in msg.entities:
		if (item["type"] == "url"):
			url = msg.text[item["offset"]:][:item["length"]]
			markdown_url = '(%s)' % url
			if markdown_url in new_text:
				new_text = new_text.replace('(%s)' % url, '(link)')
			else:
				new_text = new_text.replace(url, '[link](%s)' % url)
			if not '://' in url:
				url = "https://" + url
			u = getTelegraph(msg, url)
			links.append('[%s](%s)' % (u, u))
	if not links:
		return
	new_text = '|'.join(links) + '|' + new_text
	new_text = new_text.replace('_', '\_')
	msg.chat.send_message(new_text, parse_mode='Markdown')
	return new_text

@log_on_fail(debug_group)
def export(update, context):
	msg = update.effective_message
	r = exportImp(msg)
	source_id, display_source = getSource(msg)
	if source_id not in known_users:
		debug_group.send_message(text=display_source + ': ' + r, parse_mode='Markdown')

@log_on_fail(debug_group)
def command(update, context):
	if matchKey(update.message.text, ['auth', 'token']):
		return msgTelegraphToken(update.message)
	return update.message.reply_text('Feed me link, currently support wechat, bbc, stackoverflow, NYT, and maybe more')

tele.dispatcher.add_handler(MessageHandler(Filters.text & Filters.entity('url'), export))
tele.dispatcher.add_handler(MessageHandler(Filters.private & Filters.command, command))

tele.start_polling()
tele.idle()