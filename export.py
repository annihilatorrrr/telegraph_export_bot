#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram import MessageEntity

import export_to_telegraph
from html_telegraph_poster import TelegraphPoster
import yaml
from telegram_util import getDisplayUser, matchKey, log_on_fail, getDisplayChat, escapeMarkdown, clearUrl

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(CREDENTIALS['bot_token'], use_context=True)

r = tele.bot.send_message(-1001198682178, 'start')
r.delete()
debug_group = r.chat

known_users = [420074357, 652783030, -1001399998441]
no_auth_link_users = [-1001399998441]
delete_original_msg = [-1001399998441]

with open('TELEGRAPH_TOKENS') as f:
	TELEGRAPH_TOKENS = {}
	for k, v in yaml.load(f, Loader=yaml.FullLoader).items():
		TELEGRAPH_TOKENS[int(k)] = v

def saveTelegraphTokens():
	with open('TELEGRAPH_TOKENS', 'w') as f:
		f.write(yaml.dump(TELEGRAPH_TOKENS, sort_keys=True, indent=2))

def getSource(msg):
	if msg.from_user:
		return msg.from_user.id, msg.from_user.first_name, msg.from_user.username
	return msg.chat_id, msg.chat.title, msg.chat.username

def msgAuthUrl(msg, p):
	r = p.get_account_info(fields=['auth_url'])
	msg.reply_text('Use this url to login in 5 minutes: ' + r['auth_url'])

def msgTelegraphToken(msg):
	source_id, shortname, longname = getSource(msg)
	if source_id in TELEGRAPH_TOKENS:
		p = TelegraphPoster(access_token = TELEGRAPH_TOKENS[source_id])
	else:
		p = TelegraphPoster()
		r = p.create_api_token(shortname, longname)
		TELEGRAPH_TOKENS[source_id] = r['access_token']
		saveTelegraphTokens()
	if source_id not in no_auth_link_users:
		msgAuthUrl(msg, p)

def getTelegraph(msg, url):
	source_id, _, _ = getSource(msg)
	if source_id not in TELEGRAPH_TOKENS:
		msgTelegraphToken(msg)
	export_to_telegraph.token = TELEGRAPH_TOKENS[source_id]
	return export_to_telegraph.export(url, throw_exception = True, force = True, 
		toSimplified = 'bot_simplify' in msg.text)

def exportImp(msg):
	for item in msg.entities:
		if (item["type"] == "url"):
			url = msg.text[item["offset"]:][:item["length"]]
			if not '://' in url:
				url = "https://" + url
			result = getTelegraph(msg, url)
			msg.chat.send_message('%s|[source](%s)' % (result, url), 
				parse_mode='Markdown')

@log_on_fail(debug_group)
def export(update, context):
	msg = update.effective_message
	print(msg.text) # log use
	if '[source]' in msg.text_markdown and msg.chat_id < 0:
		return
	r = msg.reply_text('recieved')
	exportImp(msg)
	r.delete()
	source_id, _, _ = getSource(msg)
	if source_id in delete_original_msg:
		try:
			msg.delete()
		except:
			pass

@log_on_fail(debug_group)
def command(update, context):
	if matchKey(update.message.text, ['auth', 'token']):
		return msgTelegraphToken(update.message)

tele.dispatcher.add_handler(MessageHandler(Filters.text & 
	(Filters.entity('url') | Filters.entity(MessageEntity.TEXT_LINK)), export))
tele.dispatcher.add_handler(MessageHandler(Filters.command, command))

tele.start_polling()
tele.idle()