# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# import logging
# import asyncio


# BOT_TOKEN = '7691118439:AAH5mGK8VWFxhpItj8GZEp0AwOQoyihwDQg'  # o'zingizning token
# ADMIN_ID = 6855997739  # o'zingizning Telegram ID (raqam holatda)

# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher(bot)

# users = set()
# pending_messages = {}

# logging.basicConfig(level=logging.INFO)

# @dp.message_handler(commands=['start'])
# async def handle_start(message: types.Message):
#     users.add(message.from_user.id)
#     args = message.get_args()
#     if args and args != str(message.from_user.id):
#         await message.answer("✉️ Savolingizni yozing:")
#         pending_messages[message.from_user.id] = int(args)
#     else:
#         bot_username = (await bot.get_me()).username
#         link = f"https://t.me/{bot_username}?start={message.from_user.id}"
#         await message.answer(
#             f"🧾 Sizning maxsus havolangiz:\n\n{link}\n\n"
#             "Boshqalar shu link orqali sizga anonim savol yuborishi mumkin."
#         )

# @dp.message_handler(commands=['broadcast'])
# async def broadcast_start(message: types.Message):
#     if message.from_user.id != ADMIN_ID:
#         return await message.reply("⛔ Siz admin emassiz.")
#     await message.answer("📨 Yuboriladigan xabar matnini yuboring:")
#     await BroadcastState.text.set()

# # Xabar matni
# @dp.message_handler(state=BroadcastState.text)
# async def get_text(message: types.Message, state: FSMContext):
#     await state.update_data(text=message.text)
#     await message.answer("🔘 Tugma matnini yozing:")
#     await BroadcastState.btn_text.set()

# # Tugma matni
# @dp.message_handler(state=BroadcastState.btn_text)
# async def get_btn_text(message: types.Message, state: FSMContext):
#     await state.update_data(btn_text=message.text)
#     await message.answer("🔗 Tugma uchun havolani yuboring (http bilan):")
#     await BroadcastState.btn_url.set()

# # Tugma havolasi va yuborish
# @dp.message_handler(state=BroadcastState.btn_url)
# async def get_btn_url(message: types.Message, state: FSMContext):
#     url = message.text
#     if not url.startswith("http"):
#         return await message.answer("⚠ Iltimos, havola http bilan boshlansin.")
    
#     data = await state.get_data()
#     text = data['text']
#     btn_text = data['btn_text']

#     # Inline tugma
#     markup = InlineKeyboardMarkup().add(
#         InlineKeyboardButton(btn_text, url=url)
#     )

#     # Foydalanuvchilar ro‘yxati
#     users = [6855997739, 123456789]  # Bu yerga haqiqiy user ID’larni yozing

#     count = 0
#     for user_id in users:
#         try:
#             await bot.send_message(user_id, text, reply_markup=markup)
#             count += 1
#         except Exception as e:
#             print(f"Xatolik: {user_id} -> {e}")

#     await message.answer(f"✅ {count} foydalanuvchiga yuborildi.")
#     await state.finish()

# @dp.message_handler(lambda message: message.reply_to_message and message.reply_to_message.message_id in pending_messages)
# async def handle_reply(message: types.Message):
#     target_user_id = pending_messages.get(message.reply_to_message.message_id)
#     if not target_user_id:
#         return await message.reply("❌ Javob yuborib bo‘lmadi.")
#     try:
#         await bot.send_message(target_user_id, f"💬 Sizga javob:\n\n{message.text}")
#         await message.reply("✅ Javob yuborildi.")
#     except:
#         await message.reply("❌ Foydalanuvchiga yetib bo‘lmadi.")

# @dp.message_handler(content_types=types.ContentType.TEXT)
# async def handle_question(message: types.Message):
#     if message.from_user.id in pending_messages:
#         target_id = pending_messages[message.from_user.id]
#         try:
#             btn = InlineKeyboardMarkup().add(
#                 InlineKeyboardButton("✏️ Javob berish", url=f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}")
#             )
#             sent = await bot.send_message(target_id, f"📩 Yangi anonim savol:\n\n{message.text}", reply_markup=btn)
#             pending_messages[sent.message_id] = target_id
#             await message.answer("✅ Savolingiz yuborildi.")
#         except:
#             await message.answer("❌ Savol yuborilmadi.")
#         del pending_messages[message.from_user.id]
#     else:
#         await message.answer("ℹ️ Iltimos, avval havola orqali kirib savol yuboring.")

# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
import logging

BOT_TOKEN = '7691118439:AAH5mGK8VWFxhpItj8GZEp0AwOQoyihwDQg'  # o'zingizning token
ADMIN_ID = 6855997739  # admin telegram ID

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)

users = set()
pending_messages = {}

# === FSM holatlari ===
class BroadcastState(StatesGroup):
    text = State()
    btn_text = State()
    btn_url = State()

# === /start buyrug‘i ===
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

# === Admin uchun broadcast ===
@dp.message_handler(commands=['broadcast'])
async def broadcast_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ Siz admin emassiz.")
    await message.answer("📨 Yuboriladigan xabar matnini yuboring:")
    await BroadcastState.text.set()

@dp.message_handler(state=BroadcastState.text)
async def get_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("🔘 Tugma matnini yozing:")
    await BroadcastState.btn_text.set()

@dp.message_handler(state=BroadcastState.btn_text)
async def get_btn_text(message: types.Message, state: FSMContext):
    await state.update_data(btn_text=message.text)
    await message.answer("🔗 Tugma uchun havolani yuboring (http bilan):")
    await BroadcastState.btn_url.set()

@dp.message_handler(state=BroadcastState.btn_url)
async def get_btn_url(message: types.Message, state: FSMContext):
    url = message.text
    if not url.startswith("http"):
        return await message.answer("⚠ Iltimos, havola http bilan boshlansin.")
    
    data = await state.get_data()
    text = data['text']
    btn_text = data['btn_text']

    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(btn_text, url=url))
    count = 0
    for user_id in users:
        try:
            await bot.send_message(user_id, text, reply_markup=markup)
            count += 1
        except Exception as e:
            print(f"Xatolik: {user_id} -> {e}")

    await message.answer(f"✅ {count} foydalanuvchiga yuborildi.")
    await state.finish()

# === Javob berish (inline tugma orqali) ===
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_question(message: types.Message):
    if message.from_user.id in pending_messages:
        target_id = pending_messages[message.from_user.id]
        try:
            btn = InlineKeyboardMarkup().add(
                InlineKeyboardButton("✏️ Javob berish", url=f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}")
            )
            sent = await bot.send_message(target_id, f"📩 Yangi anonim savol:\n\n{message.text}", reply_markup=btn)
            pending_messages[sent.message_id] = message.from_user.id
            await message.answer("✅ Savolingiz yuborildi.")
        except:
            await message.answer("❌ Savol yuborilmadi.")
        del pending_messages[message.from_user.id]
    else:
        await message.answer("ℹ️ Iltimos, avval havola orqali kirib savol yuboring.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
