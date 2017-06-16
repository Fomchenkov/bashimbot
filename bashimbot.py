#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import re
import random
import requests
from bs4 import BeautifulSoup


# BOT_TOKEN = '381586800:AAHlB90JpJlvnp_pVYNvbgnfuE5l-OGHf_Y' # Your bot token
BOT_TOKEN = '387480715:AAGE4QwIkF6OaTaCln8vB4eAWPwD8Nes_fM'

bot = telebot.TeleBot(BOT_TOKEN)
random.seed()


def get_random_quote():
	"""
	Get random quote and parse text from bash.im
	"""
	rand_id = random.randint(440000, 445000)
	url = "http://bash.im/quote/{}".format(str(rand_id))
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	text = str(soup.find("div", class_="text"))
	text = re.sub(re.compile('<br>'), '\n', text)
	text = re.sub(re.compile('<.*?>'), '', text)
	return url + "\n\n" + text


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
	bot.polling(none_stop=True)
