import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
TOKEN = os.getenv('BOT_TOKEN', '8444368217:AAHrcAVnvgUKyQ9aEoRtgJNZclqhcwMNZXs')

# Состояния для ConversationHandler
CITY, FIO, CONFIRMATION = range(3)

# Каталог чая
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
        'description': 'Шu Пуэр 2021г. завода «Чашуван» 357гр.',
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

# Корзина в памяти
user_carts = {}
# Временные данные для заказов
user_orders = {}

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
    keyboard = []
    row = []
    
    for i, (product_id, product) in enumerate(CATALOG.items(), 1):
        button = InlineKeyboardButton(product['name'][:20] + "...", callback_data=f"view_{product_id}")
        row.append(button)
        
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🍵 Выберите чай из каталога:", reply_markup=reply_markup)

# Показ корзины
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cart = user_carts.get(user_id, [])
    
    if not cart:
        await update.message.reply_text("🛒 Ваша корзина пуста")
        return
    
    cart_text = "🛒 Ваша корзина:\n\n"
    total = 0
    
    for i, item in enumerate(cart):
        product = CATALOG[item['product_id']]
        cart_text += f"{i+1}. {item['name']}\n"
        cart_text += f"   {item['grams']}г - {item['price']}₽\n\n"
        total += item['price']
    
    cart_text += f"💵 Общая сумма: {total}₽"
    
    # Кнопки для управления корзиной
    keyboard = []
    for i in range(len(cart)):
        keyboard.append([InlineKeyboardButton(f"🗑️ Удалить {i+1}", callback_data=f"remove_{i}")])
    
    keyboard.extend([
        [InlineKeyboardButton("🗑️ Очистить всю корзину", callback_data="clear_cart")],
        [InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("↩️ Назад", callback_data="back_main")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(cart_text, reply_markup=reply_markup)

# Начало оформления заказа
async def start_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        await query.edit_message_text("❌ Корзина пуста")
        return
    
    # Сохраняем данные заказа
    user_orders[user_id] = {'cart': user_carts[user_id].copy()}
    
    await query.edit_message_text("🏙️ Введите город доставки:")
    return CITY

# Обработка города
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    city = update.message.text
    
    if user_id not in user_orders:
        await update.message.reply_text("❌ Ошибка заказа. Начните заново.")
        return ConversationHandler.END
    
    user_orders[user_id]['city'] = city
    await update.message.reply_text("👤 Введите ваше ФИО:")
    return FIO

# Обработка ФИО
async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    fio = update.message.text
    
    if user_id not in user_orders:
        await update.message.reply_text("❌ Ошибка заказа. Начните заново.")
        return ConversationHandler.END
    
    user_orders[user_id]['fio'] = fio
    user_orders[user_id]['username'] = update.effective_user.username or "Не указан"
    user_orders[user_id]['user_id'] = user_id
    
    # Формируем подтверждение
    order = user_orders[user_id]
    confirm_text = "✅ Подтвердите заказ:\n\n"
    confirm_text += f"🏙️ Город: {order['city']}\n"
    confirm_text += f"👤 ФИО: {order['fio']}\n\n"
    confirm_text += "🛒 Состав за订单:\n"
    
    total = 0
    for item in order['cart']:
        confirm_text += f"• {item['name']} - {item['grams']}г - {item['price']}₽\n"
        total += item['price']
    
    confirm_text += f"\n💵 Итого: {total}₽\n\n"
    confirm_text += "Подтверждаете заказ?"
    
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Нет", callback_data="cancel_order")]
    ]
    
    await update.message.reply_text(confirm_text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRMATION

# Подтверждение заказа
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in user_orders:
        await query.edit_message_text("❌ Ошибка заказа.")
        return ConversationHandler.END
    
    order = user_orders[user_id]
    
    # Формируем сообщение для продавца
    order_text = "🛍️ НОВЫЙ ЗАКАЗ!\n\n"
    order_text += f"👤 Покупатель: {order['fio']}\n"
    order_text += f"📞 Username: @{order['username']}\n"
    order_text += f"🆔 ID: {order['user_id']}\n"
    order_text += f"🏙️ Город: {order['city']}\n\n"
    order_text += "📦 Состав заказа:\n"
    
    total = 0
    for item in order['cart']:
        order_text += f"• {item['name']} - {item['grams']}г - {item['price']}₽\n"
        total += item['price']
    
    order_text += f"\n💵 Итого: {total}₽"
    
    # Отправляем продавцу (используем ID пользователя вместо @username)
    try:
        # Пытаемся отправить сообщение продавцу (замените на реальный ID чата продавца)
        # Чтобы получить ID продавца, можно попросить его написать боту @userinfobot
        seller_chat_id = "ваш_chat_id_продавца"  # Замените на реальный chat_id
        await context.bot.send_message(chat_id=seller_chat_id, text=order_text)
        print(f"✅ Уведомление отправлено продавцу: {order_text}")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления продавцу: {e}")
        # Альтернативный вариант - отправить сообщение через username
        try:
            await context.bot.send_message(chat_id="@moychai181", text=order_text)
            print(f"✅ Уведомление отправлено через @moychai181")
        except Exception as e2:
            print(f"❌ Ошибка отправки через @moychai181: {e2}")
            # Сохраняем заказ в лог как запасной вариант
            with open("orders.log", "a", encoding="utf-8") as f:
                f.write(f"\n{order_text}\n{'='*50}\n")
    
    # Очищаем корзину
    if user_id in user_carts:
        user_carts[user_id] = []
    
    # Удаляем временные данные
    del user_orders[user_id]
    
    await query.edit_message_text("✅ Заказ оформлен! Продавец свяжется с вами для уточнения деталей доставки и оплаты.")
    return ConversationHandler.END

# Отмена заказа
async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id in user_orders:
        del user_orders[user_id]
    
    await query.edit_message_text("❌ Заказ отменен.")
    return ConversationHandler.END

# Добавление в корзину с указанным количеством грамм
async def add_to_cart_with_grams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    grams_text = update.message.text
    
    try:
        grams = int(grams_text)
        if grams <= 0:
            await update.message.reply_text("❌ Пожалуйста, введите положительное число грамм:")
            return
            
        product_id = context.user_data.get('selected_product')
        if not product_id:
            await update.message.reply_text("❌ Ошибка: товар не выбран")
            return
            
        product = CATALOG[product_id]
        
        # Рассчитываем цену за указанное количество грамм
        price_for_grams = round(product['price_per_gram'] * grams)
        
        # Инициализируем корзину
        if user_id not in user_carts:
            user_carts[user_id] = []
        
        # Добавляем товар в корзину
        user_carts[user_id].append({
            'product_id': product_id,
            'grams': grams,
            'price': price_for_grams,
            'name': product['name']
        })
        
        # Очищаем выбранный товар
        context.user_data.pop('selected_product', None)
        
        await update.message.reply_text(f"✅ Добавлено в корзину: {product['name']} ({grams}г)")
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число грамм:")

# Обработка нажатий на кнопки
async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "back_main":
        await query.edit_message_text("Главное меню:")
        await query.message.reply_text("Выберите раздел:", reply_markup=reply_markup)
    
    elif data.startswith("view_"):
        product_id = data.split("_")[1]
        product = CATALOG[product_id]
        info_text = (
            f"{product['name']}\n\n"
            f"📝 Описание: {product['description']}\n\n"
            f"💰 Цена: {product['price']}₽/{product['weight']}\n"
            f"📊 Цена за 1гр: {product['price_per_gram']}₽\n\n"
            f"Введите количество грамм:"
        )
        # Сохраняем выбранный товар
        context.user_data['selected_product'] = product_id
        # Редактируем существующее сообщение
        await query.edit_message_text(info_text)
    
    elif data.startswith("remove_"):
        index = int(data.split("_")[1])
        if user_id in user_carts and 0 <= index < len(user_carts[user_id]):
            removed_item = user_carts[user_id].pop(index)
            await query.answer(f"🗑️ Удалено: {removed_item['name']}")
            await show_cart(update, context)
        else:
            await query.answer("❌ Ошибка удаления")
    
    elif data == "clear_cart":
        if user_id in user_carts:
            user_carts[user_id] = []
        await query.edit_message_text("🗑️ Корзина очищена")
    
    elif data == "checkout":
        await start_checkout(update, context)
    
    elif data == "confirm_order":
        await confirm_order(update, context)
    
    elif data == "cancel_order":
        await cancel_order(update, context)

# Обработка текстовых сообщений
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
        # Проверяем, ожидаем ли мы ввод грамм
        if 'selected_product' in context.user_data:
            await add_to_cart_with_grams(update, context)
        else:
            await update.message.reply_text("Пожалуйста, выберите раздел из меню ниже:", reply_markup=reply_markup)

def main():
    application = Application.builder().token(TOKEN).build()
    
    # ConversationHandler для оформления заказа
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_checkout, pattern='^checkout$')],
        states={
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio)],
            CONFIRMATION: [CallbackQueryHandler(confirm_order, pattern='^confirm_order$'),
                          CallbackQueryHandler(cancel_order, pattern='^cancel_order$')]
        },
        fallbacks=[]
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    
    print("Бот запущен и работает...")
    application.run_polling()

if __name__ == '__main__':
    main()