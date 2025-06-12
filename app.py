from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import asyncio


BOT_TOKEN = '7691118439:AAH5mGK8VWFxhpItj8GZEp0AwOQoyihwDQg'  # o'zingizning token
ADMIN_ID = 6855997739  # o'zingizning Telegram ID (raqam holatda)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

users = set()
pending_messages = {}

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    users.add(message.from_user.id)
    args = message.get_args()
    if args and args != str(message.from_user.id):
        await message.answer("✉️ Savolingizni yozing:")
        pending_messages[message.from_user.id] = int(args)
    else:
        bot_username = (await bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={message.from_user.id}"
        await message.answer(
            f"🧾 Sizning maxsus havolangiz:\n\n{link}\n\n"
            "Boshqalar shu link orqali sizga anonim savol yuborishi mumkin."
        )

@dp.message_handler(commands=['broadcast'])
async def broadcast_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Siz admin emassiz.")
    await message.answer("📨 Yubormoqchi bo'lgan xabar matnini kiriting:")

    @dp.message_handler(lambda msg: msg.chat.id == ADMIN_ID, content_types=types.ContentType.TEXT)
    async def get_broadcast_text(msg: types.Message):
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Javob berish", url=f"https://t.me/{(await bot.get_me()).username}")
        )
        count = 0
        for user_id in users:
            try:
                await bot.send_message(user_id, f"📢 {msg.text}", reply_markup=markup)
                count += 1
                await asyncio.sleep(0.05)
            except:
                continue
        await msg.answer(f"✅ {count} ta foydalanuvchiga yuborildi.")

@dp.message_handler(lambda message: message.reply_to_message and message.reply_to_message.message_id in pending_messages)
async def handle_reply(message: types.Message):
    target_user_id = pending_messages.get(message.reply_to_message.message_id)
    if not target_user_id:
        return await message.reply("❌ Javob yuborib bo‘lmadi.")
    try:
        await bot.send_message(target_user_id, f"💬 Sizga javob:\n\n{message.text}")
        await message.reply("✅ Javob yuborildi.")
    except:
        await message.reply("❌ Foydalanuvchiga yetib bo‘lmadi.")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_question(message: types.Message):
    if message.from_user.id in pending_messages:
        target_id = pending_messages[message.from_user.id]
        try:
            btn = InlineKeyboardMarkup().add(
                InlineKeyboardButton("✏️ Javob berish", url=f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}")
            )
            sent = await bot.send_message(target_id, f"📩 Yangi anonim savol:\n\n{message.text}", reply_markup=btn)
            pending_messages[sent.message_id] = target_id
            await message.answer("✅ Savolingiz yuborildi.")
        except:
            await message.answer("❌ Savol yuborilmadi.")
        del pending_messages[message.from_user.id]
    else:
        await message.answer("ℹ️ Iltimos, avval havola orqali kirib savol yuboring.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

