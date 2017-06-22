#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import random
import time
import sys

import requests
import flask
import telebot
from telebot import types
from bs4 import BeautifulSoup


BOT_TOKEN = sys.argv[1]

WEBHOOK_HOST = '89.223.27.217'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'


WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (BOT_TOKEN)

random.seed()

app = flask.Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)


def get_random_quote():
	"""
	Get random quote and parse text from bash.im
	"""
	rand_id = random.randint(440000, 445000)
	url = "http://bash.im/quote/{}".format(str(rand_id))
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	text = str(soup.find("div", class_="text"))
	text = re.sub('<br>', '\n', text)
	text = re.sub('<.*?>', '', text)
	return url + "\n\n" + text


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
	if flask.request.headers.get('content-type') == 'application/json':
		json_string = flask.request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_updates([update])
		return ''
	else:
		flask.abort(403)


@bot.message_handler(commands=['start'])
def cmd_start(message):
	text = "Привет!\nЯ умею выдавать рандомные цитати с сайта bash.im\n"
	text += "Отправьте мне команду /quote, что бы получить цитату."
	return bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["quote"])
def quote_commdnd(message):
	keyboard = types.InlineKeyboardMarkup()
	btn = types.InlineKeyboardButton(text="Ещё цитата", callback_data="quote")
	keyboard.add(btn)
	text = get_random_quote()
	bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	if call.message:
		if call.data == "quote":
			keyboard = types.InlineKeyboardMarkup()
			btn = types.InlineKeyboardButton(text="Ещё цитата", callback_data="quote")
			keyboard.add(btn)
			text = get_random_quote()
			while text == call.message.text:
				text = get_random_quote()
			bot.edit_message_text(
				chat_id=call.message.chat.id, 
				message_id=call.message.message_id, 
				text=text, reply_markup=keyboard, parse_mode="html")


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(query):
	random_quote = types.InlineQueryResultArticle(
		id="1", title="Рандомная цитата",
		description="Нажмите, что бы получить цитату",
		input_message_content=types.InputTextMessageContent(get_random_quote())
	)
	return bot.answer_inline_query(query.id, [random_quote])


if __name__ == '__main__':
	print("[Bot started]")
	bot.remove_webhook()
	time.sleep(1)
	bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
					certificate=open(WEBHOOK_SSL_CERT, 'r'))
	app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT,
			ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV))
