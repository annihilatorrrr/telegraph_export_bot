#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram import InputMediaPhoto, File
from PIL import Image
import io

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
	result = poster.post(title = title, author = author, author_url = URL, text = str(g)[:80000])
	return result["url"]

def exportImp(update, context):
	msg = update.message
	for item in msg.entities:
		if (item["type"] == "url"):
			URL = msg.text[item["offset"]:][:item["length"]]
			if (URL.startswith("https://mp.weixin.qq.com/s")):
				u = WeChat_to_Telegraph(URL)
				msg.reply_text(u)
				r = context.bot.send_message(DEBUG_GROUP, u)

def export(update, context):
	try:
		exportImp(update, context)
	except Exception as e:
		print(e)

with open('TOKEN') as f:
	TOKEN = f.readline().strip()

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text & Filters.private, export))

updater.start_polling()
updater.idle()