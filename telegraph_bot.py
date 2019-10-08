#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import requests
from bs4 import BeautifulSoup
from html_telegraph_poster import TelegraphPoster

DEBUG_GROUP = -1001198682178 # @bot_debug

with open('TELEGRAPH_TOKEN') as f:
	TELEGRAPH_TOKEN = f.readline().strip()

poster = TelegraphPoster(access_token = TELEGRAPH_TOKEN)
r = poster.get_account_info(fields=['auth_url', 'short_name', 'author_name', 'author_url'])
print("~~~~~ Telegraph account Info ~~~~~")
print(r)

def WeChat_to_Telegraph(URL):
	r = requests.get(URL)
	soup = BeautifulSoup(r.text, 'html.parser')
	title = soup.find("h2").text.strip()
	author = soup.find("a", {"id" : "js_name"}).text.strip()
	g = soup.find("div", {"id" : "js_content"})
	for img in g.find_all("img"):
		b = soup.new_tag("figure")
		b.append(soup.new_tag("img", src = img["data-src"]))
		img.replace_with(b)
	for section in g.find_all("section"):
		b = soup.new_tag("p")
		b.append(BeautifulSoup(str(section)))
		section.replace_with(b)
	print(str(g))
	result = poster.post(title = title, author = author, author_url = URL, text = str(g)[:80000])
	return result["url"]

def stackoverflow2Telegraph(URL):
	r = requests.get(URL)
	soup = BeautifulSoup(r.text, 'html.parser')
	title = soup.find("title").text.strip()
	title = title.replace('- Stack Overflow', '').strip()
	author = 'Stack Overflow'
	g = soup.find("div", class_ = "answercell")
	g = g.find("div", class_ = "post-text")
	for section in g.find_all("section"):
		b = soup.new_tag("p")
		b.append(BeautifulSoup(str(section)))
		section.replace_with(b)
	
	result = poster.post(title = title, author = author, author_url = URL, text = str(g)[:80000])
	return result["url"]

def getAuthor(msg):
	result = ''
	user = msg.from_user
	if user.first_name:
		result += ' ' + user.first_name
	if user.last_name:
		result += ' ' + user.last_name
	if user.username:
		result += '(@' + user.username + ')'
	return result

def getTelegraph(URL):
	if "mp.weixin.qq.com" in URL:
		return WeChat_to_Telegraph(URL)
	if "stackoverflow.com" in URL:
		return stackoverflow2Telegraph(URL)
	return WeChat_to_Telegraph(URL)

def trimURL(URL):
	if not '://' in URL:
		return URL
	loc = URL.find('://')
	return URL[loc + 3:]

def exportImp(update, context):
	msg = update.message
	for item in msg.entities:
		if (item["type"] == "url"):
			URL = msg.text[item["offset"]:][:item["length"]]
			u = trimURL(getTelegraph(URL))
			msg.reply_text(u)
			r = context.bot.send_message(chat_id=DEBUG_GROUP, text=getAuthor(msg) + ': ' + u)

def export(update, context):
	try:
		exportImp(update, context)
	except Exception as e:
		print("exception")
		print(e)

with open('TOKEN') as f:
	TOKEN = f.readline().strip()

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text & Filters.private, export))

updater.start_polling()
updater.idle()