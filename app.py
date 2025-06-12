import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# === Sozlamalar ===

BOT_TOKEN = '7691118439:AAEF9ECbHvB1e8Lhi7NlmJxWF284rldzfzY'  # o'zingizning token
ADMIN_ID = '6855997739'  # o'zingizning Telegram ID (raqam holatda)

# === Ishga tushirish ===
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

users = set()
pending_answers = {}

# === Javob yozish holati ===
class AnswerState(StatesGroup):
    waiting = State()

# === Reklama yuborish holati ===
class BroadcastState(StatesGroup):
    waiting_text = State()
    waiting_button_text = State()
    waiting_button_url = State()

# === /start ===
@dp.message_handler(CommandStart(deep_link=False))
async def start_handler(message: types.Message):
    users.add(message.from_user.id)
    bot_user = await bot.get_me()
    link = f"https://t.me/{bot_user.username}?start={message.from_user.id}"
    await message.answer(
        "👋 Salom! Bu bot orqali anonim savollar qabul qilishingiz mumkin.\n"
        f"🔗 Sizning havolangiz:\n{link}"
    )

# === /start <id> bilan savol yuborish ===
@dp.message_handler(CommandStart(deep_link=True))
async def handle_deep_link(message: types.Message, state: FSMContext):
    target_id = message.get_args()
    if not target_id.isdigit():
        return await message.answer("❌ Noto‘g‘ri havola.")
    await state.update_data(owner_id=int(target_id))
    await message.answer("✉️ Iltimos, savolingizni yozing:")

@dp.message_handler(state=None)
async def handle_question(message: types.Message, state: FSMContext):
    await message.answer("ℹ️ Iltimos, havola orqali savol yuboring: /start <id>")

@dp.message_handler(state=AnswerState.waiting)
async def handle_answer(message: types.Message, state: FSMContext):
    from_id = message.from_user.id
    to_id = pending_answers.pop(from_id, None)
    if to_id:
        await bot.send_message(to_id, f"📬 Sizga javob keldi:\n\n{message.text}")
        await message.answer("✅ Javob yuborildi.")
    else:
        await message.answer("❗ Javob yuborishda xatolik.")
    await state.finish()

@dp.message_handler(state=BroadcastState.waiting_button_url)
async def get_button_url(message: types.Message, state: FSMContext):
    data = await state.get_data()
    button_text = data.get("button_text")
    button_url = message.text
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(button_text, url=button_url))

    text = data.get("broadcast_text")
    success = 0
    for user_id in users:
        try:
            await bot.send_message(user_id, text, reply_markup=markup)
            success += 1
        except:
            pass
    await message.answer(f"📢 Reklama yuborildi. Yuborilgan: {success} ta foydalanuvchiga.")
    await state.finish()

@dp.message_handler(state=BroadcastState.waiting_button_text)
async def get_button_text(message: types.Message, state: FSMContext):
    await state.update_data(button_text=message.text)
    await message.answer("🔗 Endi tugma uchun URL manzilini yuboring:")
    await BroadcastState.waiting_button_url.set()

@dp.message_handler(state=BroadcastState.waiting_text)
async def get_broadcast_text(message: types.Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text)
    await message.answer("📝 Tugma matnini yuboring:")
    await BroadcastState.waiting_button_text.set()

@dp.message_handler(commands=['sendall'])
async def send_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Siz admin emassiz.")
    await message.answer("📢 Reklama matnini yuboring:")
    await BroadcastState.waiting_text.set()

# === "javob berish" tugmasi ===
@dp.callback_query_handler(lambda c: c.data.startswith("reply_"))
async def callback_reply(call: types.CallbackQuery):
    questioner_id = int(call.data.split("_")[1])
    pending_answers[call.from_user.id] = questioner_id
    await call.message.answer("✍️ Javobingizni yozing:")
    await AnswerState.waiting.set()
    await call.answer()

# === Foydalanuvchi savol yuboradi ===
@dp.message_handler(state=FSMContext)
async def forward_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    owner_id = data.get("owner_id")
    if owner_id:
        users.add(owner_id)
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📝 Javob berish", callback_data=f"reply_{message.chat.id}")
        )
        await bot.send_message(owner_id, f"📨 Yangi anonim savol:\n\n❓ {message.text}", reply_markup=markup)
        await message.answer("✅ Savolingiz yuborildi.")
        await state.finish()
    else:
        await message.answer("❗ Xatolik yuz berdi.")

# === Botni ishga tushirish ===
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
