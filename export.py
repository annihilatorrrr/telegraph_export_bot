#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import requests
import json
import export_to_telegraph
from html_telegraph_poster import TelegraphPoster

DEBUG_GROUP = -1001198682178 # @bot_debug

class Article(object):
	def __init__(self, title, author, text):
		self.title = title
		self.author = author
		self.text = text

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

def getAuthor(msg):
	result = ''
	user = msg.from_user
	if user.first_name:
		result += ' ' + user.first_name
	if user.last_name:
		result += ' ' + user.last_name
	if user.username:
		result += ' (' + user.username + ')'
	return '[' + result + '](tg://user?id=' + str(user.id) + ')'

def getTelegraph(msg, url):
	usr_id = msg.from_user.id
	if str(usr_id) not in TELEGRAPH_TOKENS:
		msgTelegraphToken(msg, usr_id)
	export_to_telegraph.token = TELEGRAPH_TOKENS[str(usr_id)]
	return export_to_telegraph.export(url)

def exportImp(update, context):
	msg = update.message
	for item in msg.entities:
		if (item["type"] == "url"):
			url = msg.text[item["offset"]:][:item["length"]]
			if not '://' in url:
				url = "https://" + url
			u = trimUrl(getTelegraph(msg, url))
			msg.reply_text(u)
			r = context.bot.send_message(
				chat_id=DEBUG_GROUP, 
				text=getAuthor(msg) + ': ' + u, 
				parse_mode='Markdown')

def export(update, context):
	try:
		exportImp(update, context)
	except Exception as e:
		print(e)
		tb.print_exc()

def command(update, context):
	try:
		if update.message.text and \
			('token' in update.message.text.lower() or 'auth' in update.message.text.lower()):
			id = update.message.from_user.id
			return msgTelegraphToken(update.message, id)
		return update.message.reply_text('Feed me link, currently support wechat, bbc, stackoverflow, NYT')
	except Exception as e:
		print(e)
		tb.print_exc()

with open('TOKEN') as f:
	TOKEN = f.readline().strip()

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text & Filters.private, export))
dp.add_handler(MessageHandler(Filters.private & Filters.command, command))

updater.start_polling()
updater.idle()