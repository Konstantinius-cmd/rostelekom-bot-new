import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем токен и ID админа из переменных среды
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Состояния для ConversationHandler
GETTING_DATA = range(1)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📡 Подключение новых услуг", callback_data="connect")],
        [
            InlineKeyboardButton("💳 Смена тарифа", callback_data="change"),
            InlineKeyboardButton("🛠 Технические неполадки", callback_data="support"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Здравствуйте! Я бот компании Ростелеком.\nВыберите интересующий вас пункт:",
        reply_markup=reply_markup,
    )


# Обработка нажатия на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "connect":
        await query.message.reply_text(
            "Пожалуйста, введите ваше имя, адрес и номер телефона для подключения услуг:"
        )
        return GETTING_DATA

    elif choice == "change":
        await query.message.reply_text(
            "Для смены тарифа, пожалуйста, позвоните по номеру:\n📞 8-800-100-08-00"
        )

    elif choice == "support":
        await query.message.reply_text(
            "Если у вас возникли технические неполадки:\n"
            "📞 8-800-100-08-00\n"
            "🌐 https://rt.ru/support"
        )

    return ConversationHandler.END


# Получение данных от пользователя
async def get_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = update.message.text
    print(f"[ДАННЫЕ ОТ ПОЛЬЗОВАТЕЛЯ] {user_data}")

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📬 Новая заявка на подключение:\n{user_data}"
        )
        await update.message.reply_text("✅ Спасибо! Ваша заявка передана оператору.")
    except Exception as e:
        print(f"[ОШИБКА ОТПРАВКИ АДМИНУ] {e}")
        await update.message.reply_text("❌ Ошибка при отправке данных. Попробуйте позже.")

    return ConversationHandler.END


# Обработка команды /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Действие отменено.")
    return ConversationHandler.END


# Основная функция запуска бота
async def main():
    print("⚙️ Инициализация бота...")

    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={GETTING_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_data)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("📦 Инициализация завершена, запускаем...")

    await app.initialize()
    print("✅ initialize() пройден")

    await app.start()
    print("✅ start() пройден")

    await app.updater.start_polling()
    print("✅ polling запущен — бот готов!")

    await asyncio.Event().wait()


# Точка входа
if __name__ == "__main__":
    asyncio.run(main())
