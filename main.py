import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота будет браться из переменных окружения
TOKEN = os.getenv('BOT_TOKEN', '8444368217:AAHrcAVnvgUKyQ9aEoRtgJNZclqhcwMNZXs')

# Главное меню
main_menu_keyboard = [
    ['🍵 Каталог', '🛒 Корзина'],
    ['📢 Наш канал', '👨‍💼 Связаться с нами']
]
reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Добро пожаловать в чайный магазин MOYCHAI🍵.\n"
        f"Выберите интересующий вас раздел:"
    )
    await update.message.reply_html(welcome_text, reply_markup=reply_markup)

# Обработка кнопок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '🍵 Каталог':
        response = "Раздел 'Каталог' в разработке. Скоро здесь будет много вкусного чая! 🍃"
    elif text == '🛒 Корзина':
        response = "Раздел 'Корзина' в разработке. Здесь будут ваши покупки."
    elif text == '📢 Наш канал':
        response = "Подписывайтесь на наш канал, чтобы быть в курсе новинок и акций: https://t.me/moichai181"
    elif text == '👨‍💼 Связаться с нами':
        response = "По всем вопросам обращайтесь к нашему продавцу — @moychai181"
    else:
        response = "Пожалуйста, выберите раздел из меню ниже:"

    await update.message.reply_text(response, reply_markup=reply_markup)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Простой запуск через polling, который отлично работает на Railway
    application.run_polling()

if __name__ == '__main__':
    main()