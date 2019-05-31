import os
import requests
from pymongo import MongoClient
import telebot

API_TOKEN = os.environ['BOT_TOKEN']
DB = os.environ['BOT_DB']
bot = telebot.TeleBot(API_TOKEN)
client = MongoClient(DB)
db = client.bot_db


@bot.message_handler(commands=['start'])
def send_welcome_contoller(message):
    chat_id = message.chat.id
    text = 'Hi! You can send voice note to me and I will save it.'
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['get_files'])
def get_list_files_contoller(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if db.files.count_documents({"user_id": user_id}) > 0:
        list_ = db.files.find({"user_id": user_id})
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for file in list_:
            markup.add(
                telebot.types.KeyboardButton(text=f'/get_file {file["id"]}'))
        text = 'Please choose file:'
        bot.send_message(chat_id, text, reply_markup=markup)
    else:
        text = 'Files not found'
        bot.send_message(chat_id, text)


@bot.message_handler(commands=['get_file'])
def get_file_contoller(message):
    id = message.text.split(' ')[1]
    user_id = message.from_user.id
    chat_id = message.chat.id
    file = db.files.find_one({"user_id": user_id, "id": int(id)})
    try:
        file_path = file['path']
        voice = open(file_path, 'rb')
        bot.send_voice(chat_id, voice)
    except:
        text = 'File not found'
        bot.send_message(user_id, text)


@bot.message_handler(content_types=['voice'])
def save_voice_file_contoller(message):
    file_id = message.voice.file_id
    user_id = message.from_user.id
    date = message.date
    id = save_voice_file(file_id, user_id, date)
    bot.reply_to(message, f"ок: {id}")


def save_voice_file(file_id, user_id, date):
    file_info = bot.get_file(file_id)
    response = requests.get(
        f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}')
    path = f'uploads/{file_id}.ogg'
    with open(path, 'wb') as output:
        output.write(response.content)
    count = db.files.count_documents({"user_id": user_id})
    data = {"id": count + 1, "path": path, "user_id": user_id, "date": date}
    result = db.files.insert_one(data)
    return data["id"]


bot.polling()