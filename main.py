import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
TOKEN = os.getenv('BOT_TOKEN', '8444368217:AAHrcAVnvgUKyQ9aEoRtgJNZclqhcwMNZXs')

# Каталог чая (данные из вашего сообщения)
CATALOG = {
    '1': {
        'name': '🍵 Дафо Лунцзин (колодец дракона)',
        'description': 'Вкус: нежный, густой, освежающий, сладкий. Оттенки липового меда, орехов, дыни и свежих фруктов.',
        'price': 640,
        'weight': '50гр',
        'price_per_gram': 13
    },
    '2': {
        'name': '🚩 Да Хун Пао (большой красный халат)',
        'description': 'Вкус: нежный, густой и насыщенный, табачными, карамельными, медовыми нотами и выраженным вкусом семечек.',
        'price': 400,
        'weight': '50гр',
        'price_per_gram': 8
    },
    '3': {
        'name': '🍵 Те гуань инь (железная богиня)',
        'description': 'Во вкусе: свежескошенная трава, цветы, цитрусы, мёд с железным послевкусием и легкими ментоловыми нотками',
        'price': 430,
        'weight': '50гр',
        'price_per_gram': 8.6
    },
    '4': {
        'name': '🍵 Шу Пуэр 2021г. «Юаньфэй»',
        'description': 'Шу Пуэр 2021г. завода «Чашуван» 357гр.',
        'price': 1600,
        'weight': '357гр',
        'price_per_gram': 4.5
    },
    '5': {
        'name': '🍵 Шу Пуэр 2019г. «3 звезды»',
        'description': 'Шу Пуэр 2019г. завода «Чашуван» 357гр.',
        'price': 1600,
        'weight': '357гр',
        'price_per_gram': 4.5
    },
    '6': {
        'name': '🍵 Шу Пуэр 2021г. «Бык из Нака»',
        'description': 'Шу Пуэр 2021г. завода «Чашуван» 357гр.',
        'price': 2360,
        'weight': '357гр',
        'price_per_gram': 7
    },
    '7': {
        'name': '🍵 Шу Пуэр 2017г. «Гунтин»',
        'description': 'Шу Пуэр 2017г. завода «Юньфусян» 357гр. Вкус: древесина, земля с нотками бани, грецкого ореха, сухофруктов и лёгкой сливочностью',
        'price': 3140,
        'weight': '357гр',
        'price_per_gram': 8.8
    },
    '8': {
        'name': '🍵 Шен Пуэр 2020г. «Гора Бада»',
        'description': 'Шен Пуэр 2020г. завода «Юньфусян» 357гр.',
        'price': 2000,
        'weight': '357гр',
        'price_per_gram': 5.7
    },
    '9': {
        'name': '🍵 Шен Пуэр 2018г. «Золотая нить»',
        'description': 'Шен Пуэр 2018г. завода «Сягуань» гнездо 100гр.',
        'price': 1000,
        'weight': '100гр',
        'price_per_gram': 10
    },
    '10': {
        'name': '🍵 Шен Пуэр 2013г. «7543»',
        'description': 'Шен Пуэр 2013г. завода «Сягуань» 357гр.',
        'price': 3750,
        'weight': '357гр',
        'price_per_gram': 10.6
    },
    '11': {
        'name': '🍵 Шу Пуэр 2016г. «Наньно»',
        'description': 'Шу Пуэр 2016г. завода «Чжоуши» 357гр.',
        'price': 2040,
        'weight': '357гр',
        'price_per_gram': 5.7
    },
    '12': {
        'name': '🍵 Шу Пуэр 2005г. «Двор чайного короля»',
        'description': 'Шу Пуэр 2005г. завода «Чжоуши» 357гр.',
        'price': 2220,
        'weight': '357гр',
        'price_per_gram': 6.2
    },
    '13': {
        'name': '🍵 Шуйсянь (владыка вод)',
        'description': 'Темный улун сильной прожарки. Вкус: легкий с цветочными, табачными, фруктовыми и семечными нотами.',
        'price': 520,
        'weight': '50гр',
        'price_per_gram': 10.4
    }
}

# Корзина в памяти (словарь, где ключ - user_id, значение - список товаров)
user_carts = {}

# Главное меню
main_menu_keyboard = [
    ['🍵 Каталог', '🛒 Корзина'],
    ['📢 Наш канал', '👨‍💼 Связаться с нами']
]
reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"Добро пожаловать в чайный магазин MOYCHAI🍵.\n"
        f"Выберите интересующий вас раздел:"
    )
    await update.message.reply_html(welcome_text, reply_markup=reply_markup)

# Показ каталога
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем кнопки для каждого чая
    keyboard = []
    row = []
    
    for i, (product_id, product) in enumerate(CATALOG.items(), 1):
        # Создаем кнопку с названием чая
        button = InlineKeyboardButton(product['name'][:20] + "...", callback_data=f"view_{product_id}")
        row.append(button)
        
        # Размещаем по 2 кнопки в ряду
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    
    # Добавляем последний ряд, если он не пустой
    if row:
        keyboard.append(row)
    
    # Кнопка назад
    keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🍵 Выберите чай из каталога:", reply_markup=reply_markup)

# Показ информации о чае
async def show_tea_info(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    product = CATALOG[product_id]
    
    # Формируем текст с информацией
    info_text = (
        f"{product['name']}\n\n"
        f"📝 Описание: {product['description']}\n\n"
        f"💰 Цена: {product['price']}₽/{product['weight']}\n"
        f"📊 Цена за 1гр: {product['price_per_gram']}₽\n\n"
        f"Выберите действие:"
    )
    
    # Кнопки для добавления в корзину и возврата
    keyboard = [
        [InlineKeyboardButton("➕ Добавить в корзину", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton("↩️ Назад в каталог", callback_data="back_catalog")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(info_text, reply_markup=reply_markup)

# Показ корзины
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Получаем корзину пользователя или создаем пустую
    cart = user_carts.get(user_id, [])
    
    if not cart:
        await update.message.reply_text("🛒 Ваша корзина пуста")
        return
    
    # Формируем текст корзины
    cart_text = "🛒 Ваша корзина:\n\n"
    total = 0
    
    for item in cart:
        product = CATALOG[item['product_id']]
        item_total = product['price']
        total += item_total
        cart_text += f"• {product['name']}\n"
        cart_text += f"  {product['weight']} - {product['price']}₽\n\n"
    
    cart_text += f"💵 Общая сумма: {total}₽"
    
    # Кнопки для корзины
    keyboard = [
        [InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton("↩️ Назад", callback_data="back_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(cart_text, reply_markup=reply_markup)

# Обработка нажатий на кнопки
async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "back_main":
        # Возврат в главное меню
        await query.edit_message_text("Главное меню:")
        await query.message.reply_text("Выберите раздел:", reply_markup=reply_markup)
    
    elif data == "back_catalog":
        # Возврат в каталог
        await show_catalog(update, context)
    
    elif data.startswith("view_"):
        # Просмотр информации о чае
        product_id = data.split("_")[1]
        await query.edit_message_text("Информация о чае:")
        await show_tea_info(update, context, product_id)
    
    elif data.startswith("add_"):
        # Добавление в корзину
        product_id = data.split("_")[1]
        
        # Инициализируем корзину, если ее нет
        if user_id not in user_carts:
            user_carts[user_id] = []
        
        # Добавляем товар в корзину
        user_carts[user_id].append({
            'product_id': product_id,
            'added_at': 'now'  # Можно добавить временную метку
        })
        
        await query.answer("✅ Чай добавлен в корзину!")
    
    elif data == "clear_cart":
        # Очистка корзины
        if user_id in user_carts:
            user_carts[user_id] = []
        await query.edit_message_text("🗑️ Корзина очищена")
    
    elif data == "checkout":
        # Оформление заказа
        await query.edit_message_text("Для оформления заказа свяжитесь с @moychai181")

# Обработка текстовых сообщений (главное меню)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '🍵 Каталог':
        await show_catalog(update, context)
    elif text == '🛒 Корзина':
        await show_cart(update, context)
    elif text == '📢 Наш канал':
        await update.message.reply_text("Подписывайтесь на наш канал: https://t.me/moichai181")
    elif text == '👨‍💼 Связаться с нами':
        await update.message.reply_text("По всем вопросам обращайтесь к @moychai181")
    else:
        await update.message.reply_text("Пожалуйста, выберите раздел из меню ниже:", reply_markup=reply_markup)

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    
    print("Бот запущен и работает...")
    application.run_polling()

if __name__ == '__main__':
    main()