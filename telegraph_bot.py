#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram import InputMediaPhoto, File
from PIL import Image
import io

import requests
from bs4 import BeautifulSoup
from html_telegraph_poster import upload_to_telegraph

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
    result = upload_to_telegraph(title = title, author = author, text = str(g)[:80000])
    return result["url"]

def preview(bot, update):
    msg = update.message
    if (msg.forward_from_chat):
     if (msg.forward_from_chat.id == -1001333303289): return
    for item in msg.entities:
        if (item["type"] == "url"):
            URL = msg.text[item["offset"]:][:item["length"]]
            if (URL.startswith("https://mp.weixin.qq.com/s")):
                u = WeChat_to_Telegraph(URL)
                msg.reply_text(u)
                r = msg.bot.send_message("@WeChatEssence", u + f"\n原文链接: {URL}")

with open('TOKEN') as f:
    TOKEN = f.readline().strip()

with open('TELEGRAPH_TOKEN') as f:
    TELEGRAPH_TOKEN = f.readline().strip()

updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text, preview))

updater.start_polling()
updater.idle()