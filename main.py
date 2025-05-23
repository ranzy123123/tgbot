from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

BOT_TOKEN = "7006467443:AAFNVxqnP4mKsnGkdehqH7jecPXWwkctbtI"
SUPPORT_GROUP_ID = -1002288022061

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Введіть своє питання — ми надішлемо його в техпідтримку.")

# Повідомлення від користувача
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text
    info = (
        f"📩 Повідомлення від @{user.username or 'немає_нікнейму'}\n"
        f"ID: {user.id}\n\n"
        f"{message}"
    )
    await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=info)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔚 Завершити чат", callback_data="end_chat")]
    ])
    await update.message.reply_text("✅ Ваше повідомлення надіслано. Очікуйте відповідь.", reply_markup=keyboard)

# Відповідь саппорту
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != SUPPORT_GROUP_ID:
        await update.message.reply_text("❌ Ця команда працює тільки в групі підтримки.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Формат: /reply <user_id> <повідомлення>")
        return

    user_id = int(args[0])
    reply_text = " ".join(args[1:])
    try:
        await context.bot.send_message(chat_id=user_id, text=f"💬 Відповідь від підтримки:\n{reply_text}")
        await update.message.reply_text("✅ Відповідь надіслана.")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {e}")

# Обробка callback кнопок
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "end_chat":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{i} ⭐", callback_data=f"rate_{i}")] for i in range(1, 6)
        ])
        await query.message.reply_text("📝 Оцініть нашу підтримку:", reply_markup=keyboard)

    elif query.data.startswith("rate_"):
        rating = query.data.split("_")[1]
        user = update.effective_user
        await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=f"⭐ Користувач @{user.username or user.id} залишив оцінку: {rating} з 5"
        )
        await query.message.reply_text("🙏 Дякуємо за вашу оцінку!")

# Запуск бота
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reply", reply_command))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_message))
app.add_handler(CallbackQueryHandler(handle_callback))

print("✅ Бот запущено")
app.run_polling()
