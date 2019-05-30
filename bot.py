import os

import telebot

TOKEN = os.environ['BOT_TOKEN']

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['test'])
def send_welcome(message):
    bot.reply_to(message, "Hello World!")


@bot.message_handler(content_types=['voice'])
def save_voice_message(message):
    bot.reply_to(message, "This is voice!")
