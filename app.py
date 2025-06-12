import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 🔐 Sozlamalar
BOT_TOKEN = '7691118439:AAEF9ECbHvB1e8Lhi7NlmJxWF284rldzfzY'  # o'zingizning token
ADMIN_ID = '6855997739'  # o'zingizning Telegram ID (raqam holatda)

# 📦 Ma'lumotlar fayli
data_file = 'data.json'
try:
    with open(data_file, 'r') as f:
        data = json.load(f)
except:
    data = {"users": {}, "questions": {}}

def save_data():
    with open(data_file, 'w') as f:
        json.dump(data, f)

# 🚀 /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in data["users"]:
        token = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))
        data["users"][user_id] = {"token": token}
        save_data()
        await update.message.reply_text(
            f"🤖 Salom! Sizning tokeningiz: `{token}`\n\n"
            "Bu token orqali boshqalar sizga anonim savol yuborishi mumkin.",
            parse_mode='Markdown')
    else:
        token = data["users"][user_id]["token"]
        await update.message.reply_text(f"✅ Siz avval ro‘yxatdan o‘tgansiz.\nTokeningiz: `{token}`", parse_mode='Markdown')

# ✉️ /ask TOKEN Savol
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❗ Format: /ask TOKEN Savol matni")
        return
    token = context.args[0].strip()
    msg = ' '.join(context.args[1:])
    to_user = None
    for uid, info in data["users"].items():
        if info["token"] == token:
            to_user = uid
            break
    if not to_user:
        await update.message.reply_text("❌ Token topilmadi.")
        return

    qid = str(len(data["questions"]) + 1)
    data["questions"][qid] = {
        "to": to_user,
        "from": str(update.effective_user.id),
        "text": msg,
        "answer": None
    }
    save_data()

    # Inline tugma
    keyboard = [[InlineKeyboardButton("📝 Javob berish", switch_inline_query_current_chat=f"/answer {qid} ")]]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=int(to_user),
        text=f"📩 Yangi anonim savol:\n\n❓ {msg}",
        reply_markup=markup
    )
    await update.message.reply_text("✅ Savolingiz yuborildi.")

# ✅ /answer ID Javob
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if len(context.args) < 2:
        await update.message.reply_text("❗ Format: /answer QID Javob matni")
        return
    qid = context.args[0]
    if qid not in data["questions"]:
        await update.message.reply_text("❌ Savol topilmadi.")
        return
    question = data["questions"][qid]
    if question["to"] != user_id:
        await update.message.reply_text("⛔ Siz bu savolga javob bera olmaysiz.")
        return
    if question["answer"]:
        await update.message.reply_text("⚠️ Bu savolga allaqachon javob berilgan.")
        return

    javob = ' '.join(context.args[1:])
    data["questions"][qid]["answer"] = javob
    save_data()

    await update.message.reply_text("✅ Javob saqlandi va yuborildi.")

    # Javobni savol bergan odamga yuboramiz
    from_user = question.get("from")
    if from_user:
        try:
            await context.bot.send_message(
                chat_id=int(from_user),
                text=f"📬 Siz bergan savolga javob:\n\n❓ {question['text']}\n\n💬 {javob}"
            )
        except:
            pass

# 📊 /admin – statistik ma'lumotlar
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    total_users = len(data["users"])
    total_q = len(data["questions"])
    ans_q = len([q for q in data["questions"].values() if q["answer"]])
    await update.message.reply_text(
        f"📊 Statistika:\n👤 Foydalanuvchilar: {total_users}\n"
        f"❓ Savollar: {total_q}\n✅ Javoblar: {ans_q}\n🕳 Javobsiz: {total_q - ans_q}"
    )

# 📢 /broadcast Tugma | URL | Matn
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❗ Format: /broadcast Tugma | URL | Xabar")
        return
    try:
        btn, url, msg = ' '.join(context.args).split('|', maxsplit=2)
        btn, url, msg = btn.strip(), url.strip(), msg.strip()
    except:
        await update.message.reply_text("❗ Format xato. Masalan:\n/broadcast Qo‘shilish | https://t.me/... | E'lon matni")
        return
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(btn, url=url)]])
    count = 0
    for uid in data["users"]:
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 {msg}", reply_markup=markup)
            count += 1
        except:
            pass
    await update.message.reply_text(f"✅ Yuborildi: {count} ta foydalanuvchiga.")

# 🔄 Noma'lum xabarga javob
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot komandalaridan foydalaning: /start, /ask, /answer")

# 🔧 Botni ishga tushirish
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("answer", answer))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    print("✅ Bot ishga tushdi")
    app.run_polling()

if __name__ == '__main__':
    main()
