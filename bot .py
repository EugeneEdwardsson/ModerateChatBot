import logging
import nltk
import asyncio
import config
import bad_words
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from nltk.tokenize import word_tokenize
import time
from aiogram import types
from aiogram.dispatcher import filters
from aiogram import types
from aiogram.dispatcher.filters import ContentTypeFilter

API_TOKEN = config.TOKEN
bad_words = bad_words.bad_words
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

bot = Bot(token = API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())



user_rating = {}
apology = ['извини', 'простите', 'я больше так не буду', 'извините', "прости",'извени','извените', "сорян"]

def check_for_bad_words(text):
    words = word_tokenize(text.lower())
    for word in words:
        if word in bad_words:
            return True
    return False

def check_for_apology(text):
    words = word_tokenize(text.lower())
    for word in words:
        if word in apology:
            return True
    return False

def calculate_user_rating(user_id):
    if user_id not in user_rating:
        user_rating[user_id] = 0
    return user_rating[user_id]

# def ban_user(user_id, chat_id, message):
#     message.bot.ban_chat_member(chat_id, user_id, until_date=int(time.time()) + 18000) #бан пользователя на 5 часов
#     user_rating[user_id] = 0

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    chat_id = message.chat.id
    await message.answer("Привет! Я телеграм-бот, который поможет тебе избежать использования ненормативной лексики в чате.")
    await message.answer(f"Ваш рейтинг: {calculate_user_rating(message.from_user.id)}")

@dp.message_handler(commands=['help'])
async def handle_help(message: types.Message):
    chat_id = message.chat.id
    await message.answer("Я могу помочь тебе избежать использования ненормативной лексики в чате. Просто отправь мне сообщение, и я проверю его на содержание ненормативных слов. Если они будут обнаружены, я предупрежу тебя и удалю сообщение.")

@dp.message_handler(commands=['rating'])
async def handle_help(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await message.answer(f"Ваш рейтинг: {calculate_user_rating(user_id)}")

@dp.message_handler(content_types=['text'])
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    message_id = message.message_id
    user_id = message.from_user.id
    text = message.text
    if check_for_bad_words(text):
        user_rating[user_id] += 1
        await message.reply(f'Предупреждение: в вашем сообщении была использована ненормативная лексика. Ваш рейтинг: {calculate_user_rating(user_id)}. Если он будет достигнут 3, вы будете удалены из чата на 5 часов!')
        await bot.delete_message(chat_id, message_id)
        if user_rating[user_id] >= 3:
            await message.answer("Вы получили бан, ждем вас через 5 часов, надеемся вы перестаните использовать ненормативную лексику")
            message.bot.ban_chat_member(chat_id, user_id, until_date=int(time.time()) + 18000) #бан пользователя на 5 часов + 18000
            user_rating[user_id] = 0
    elif check_for_apology(text):
        user_rating[user_id] = 0
        await message.reply(f'Ваш рейтинг изменен: {calculate_user_rating(user_id)}. Просим, Вас больше не употреблять ненормативную лексику!')
        

@dp.message_handler(ContentTypeFilter(types.ContentType.NEW_CHAT_MEMBERS))
async def handle_new_member(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    new_members = message.new_chat_members
    for member in new_members:
        await message.answer(f"Добро пожаловать в чат, {member.first_name}! Я помогу тебе избежать использования ненормативной лексики в сообщениях.")
        await message.answer(f"Ваш рейтинг: {calculate_user_rating(user_id)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
