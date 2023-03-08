import config
import logging
import filters

from aiogram import Bot, Dispatcher, executor, types

from filters import IsAdminFilter

# log level
logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# activate filters
dp.filters_factory.bind(IsAdminFilter)

# ban command(admins only!)
@dp.message_handler(is_admin=True, commands=["ban"], commands_prefix="!/")
async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть ответом на сообщение!")
        return

    await message.bot.delete_message(chat_id=config.GROUP_ID, user_id=message.message_id)
    await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.reply_to_message.from_user.id)

    await message.reply_to_message.reply("Пользователь забанен!")

# remove new user joined message
@dp.message_handler(content_types=["new_chat_members"])
async def on_user_joined(message: types.Message):
    await message.delete()


# simple profanity check
@dp.message_handler()
async def filter_messages(message: types.Message):
    if "плохое слово" in message.text:
        # profanity detected, remove
        await message.delete()

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)