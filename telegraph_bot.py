#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import requests
import json
from bs4 import BeautifulSoup
from html_telegraph_poster import TelegraphPoster

DEBUG_GROUP = -1001198682178 # @bot_debug

class Article(object):
	def __init__(self, title, author, text):
		self.title = title
		self.author = author
		self.text = text

with open('TELEGRAPH_TOKENS') as f:
	TELEGRAPH_TOKENS = json.load(f)

with open('TELEGRAPH_TOKENS', 'w') as f:
	f.write(json.dumps(TELEGRAPH_TOKENS, sort_keys=True, indent=2))

def getPoster(msg, id, forceMessageAuthUrl=False):
	if str(id) in TELEGRAPH_TOKENS:
		p = TelegraphPoster(access_token = TELEGRAPH_TOKENS[str(id)])
		if forceMessageAuthUrl:
			msgAuthUrl(msg, p)
		return p
	p = TelegraphPoster()
	r = p.create_api_token(msg.from_user.first_name, msg.from_user.username)
	TELEGRAPH_TOKENS[str(id)] = r['access_token']
	saveTelegraphTokens()
	msgAuthUrl(msg, p)
	return p

def msgAuthUrl(msg, p):
	r = p.get_account_info(fields=['auth_url'])
	msg.reply_text('Use this URL to login in 5 minutes: ' + r['auth_url'])

def wechat2Article(URL):
	r = requests.get(URL)
	soup = BeautifulSoup(r.text, 'html.parser')
	title = soup.find("h2").text.strip()
	author = soup.find("a", {"id" : "js_name"}).text.strip()
	g = soup.find("div", {"id" : "js_content"})
	for img in g.find_all("img"):
		b = soup.new_tag("figure")
		b.append(soup.new_tag("img", src = img["data-src"]))
		img.append(b)
	for section in g.find_all("section"):
		b = soup.new_tag("p")
		b.append(BeautifulSoup(str(section)))
		section.replace_with(b)
	return Article(title, author,str(g)[:80000])
	

def stackoverflow2Article(URL):
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
	
	return Article(title, author,str(g)[:80000])

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

def bbc2Article(URL):
	r = requests.get(URL)
	soup = BeautifulSoup(r.text, 'html.parser')
	title = soup.find("h1").text.strip()
	author = 'BBC'
	g = soup.find("div", class_ = "story-body__inner")
	for elm in g.find_all('span', class_="off-screen"):
		elm.decompose()
	for elm in g.find_all('ul', class_="story-body__unordered-list"):
		elm.decompose()
	for elm in g.find_all('span', class_="story-image-copyright"):
		elm.decompose()
	for img in g.find_all("div", class_="js-delayed-image-load"):
		b = soup.new_tag("figure", width=img['data-width'], height=img['data-height'])
		b.append(soup.new_tag("img", src = img["data-src"], width=img['data-width'], height=img['data-height']))
		img.replace_with(b)
	for section in g.find_all("section"):
		b = soup.new_tag("p")
		b.append(BeautifulSoup(str(section)))
		section.replace_with(b)
	return Article(title, author,str(g)[:80000])

def getArticle(URL):
	if "mp.weixin.qq.com" in URL:
		article =  wechat2Article(URL)
	if "stackoverflow.com" in URL:
		article = stackoverflow2Article(URL)
	if "bbc.com" in URL:
		article = bbc2Article(URL)
	return bbc2Article(URL)

def getTelegraph(msg, URL):
	usr_id = msg.from_user.id
	p = getPoster(msg, usr_id)
	article = getArticle(URL)
	r = p.post(title = article.title, author = article.author, author_url = URL, text = article.text)
	return r["url"]

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
			u = trimURL(getTelegraph(msg, URL))
			msg.reply_text(u)
			r = context.bot.send_message(chat_id=DEBUG_GROUP, text=getAuthor(msg) + ': ' + u)

def export(update, context):
	try:
		exportImp(update, context)
	except Exception as e:
		print("exception")
		print(e)

def command(update, context):
	try:
		if update.message.text and 'token' in update.message.text.lower():
			id = update.message.from_user.id
			return getPoster(update.message, id, forceMessageAuthUrl=True)
		return update.message.reply_text('Feed me link, currently support wechat, bbc, and stackoverflow')
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