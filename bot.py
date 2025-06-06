import os
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Получаем токен и ID оператора из переменных окружения (для Render)
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

GETTING_DATA = range(1)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📡 Подключение новых услуг", callback_data="connect")],
        [
            InlineKeyboardButton("🔄 Смена тарифа", callback_data="change"),
            InlineKeyboardButton("⚠️ Технические неполадки", callback_data="support"),
        ],
    ]
    await update.message.reply_text(
        "Здравствуйте! Я бот компании Ростелеком.\nЧем могу помочь?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "connect":
        await query.message.reply_text("Пожалуйста, введите ваше имя, адрес и номер телефона:")
        return GETTING_DATA

    elif action == "change":
        await query.message.reply_text("📞 Для смены тарифа позвоните: 8-800-100-08-00")
    elif action == "support":
        await query.message.reply_text(
            "⚙️ Для решения технических проблем обратитесь:\n"
            "📞 8-800-100-08-00\n🌐 https://rt.ru/support"
        )

    return ConversationHandler.END

# Получение данных от пользователя
async def get_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = update.message.text
    await update.message.reply_text("✅ Спасибо! Ваша заявка передана оператору.")
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📬 Новая заявка:\n{user_data}"
        )
    except Exception as e:
        print(f"Ошибка при отправке админу: {e}")
    return ConversationHandler.END

# Команда /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

# Основной запуск
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GETTING_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Новый бот запущен.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
