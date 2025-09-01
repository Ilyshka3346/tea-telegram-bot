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
CITY, FIO, PHONE, CONFIRMATION = range(4)

# Каталог чая с фото (обновленные цены и форматирование)
CATALOG = {
    '1': {
        'name': '🍵 Дафо Лунцзин (колодец дракона)',
        'description': 'Нежный, густой, освежающий, сладкий. Оттенки липового меда, орехов, дыни и свежих фруктов.',
        'price': 640,
        'weight': '50гр',
        'price_per_gram': 12.8,
        'photo': 'https://imgur.com/aSnZTQx'
    },
    '2': {
        'name': '🚩 Да Хун Пао (большой красный халат)',
        'description': 'Нежный, густой и насыщенный, табачными, карамельными, медовыми нотами и выраженным вкусом семечек.',
        'price': 400,
        'weight': '50гр',
        'price_per_gram': 8,
        'photo': 'https://imgur.com/czS7nph'
    },
    '3': {
        'name': '🍵 Те гуань инь (железная богиня)',
        'description': 'Свежескошенная трава, цветы, цитрусы, мёд с железным послевкусием и легкими ментоловыми нотками',
        'price': 430,
        'weight': '50гр',
        'price_per_gram': 8.6,
        'photo': 'https://imgur.com/NZayGfs'
    },
    '4': {
        'name': '🍵 Шу Пуэр 2021г. «Юаньфэй»',
        'description': '',
        'price': 1500,
        'weight': '357гр',
        'price_per_gram': 4.2,
        'photo': 'https://imgur.com/DIm3dvb'
    },
    '5': {
        'name': '🍵 Шу Пуэр 2019г. «3 звезды»',
        'description': '',
        'price': 1400,
        'weight': '357гр',
        'price_per_gram': 3.9,
        'photo': 'https://imgur.com/mIthhWy'
    },
    '6': {
        'name': '🍵 Шу Пуэр 2021г. «Бык из Нака»',
        'description': '',
        'price': 2360,
        'weight': '357гр',
        'price_per_gram': 6.6,
        'photo': 'https://imgur.com/8lsc4zp'
    },
    '7': {
        'name': '🍵 Шу Пуэр 2017г. «Гунтин»',
        'description': 'Древесина, земля с нотками бани, грецкого ореха, сухофруктов и лёгкой сливочностью\n❗ЦЕЛОГО БЛИНА НЕТ В НАЛИЧИИ❗',
        'price': 3140,
        'weight': '357гр',
        'price_per_gram': 8,
        'photo': 'https://imgur.com/AgnAVaM'
    },
    '8': {
        'name': '🍵 Шен Пуэр 2020г. «Гора Бада»',
        'description': '',
        'price': 2000,
        'weight': '357гр',
        'price_per_gram': 5.7,
        'photo': 'https://imgur.com/22P5cKD'
    },
    '9': {
        'name': '🍵 Шен Пуэр 2018г. «Золотая нить»',
        'description': '',
        'price': 1000,
        'weight': '100гр',
        'price_per_gram': 10,
        'photo': 'https://imgur.com/JgLhysy'
    },
    '10': {
        'name': '🍵 Шен Пуэр 2013г. «7543»',
        'description': '',
        'price': 3500,
        'weight': '357гр',
        'price_per_gram': 9.8,
        'photo': 'https://imgur.com/bmy5NBB'
    },
    '11': {
        'name': '🍵 Шу Пуэр 2016г. «Наньно»',
        'description': '',
        'price': 1800,
        'weight': '357гр',
        'price_per_gram': 5,
        'photo': 'https://imgur.com/KIzmAb5'
    },
    '12': {
        'name': '🍵 Шу Пуэр 2005г. «Двор чайного короля»',
        'description': '❗ЦЕЛОГО БЛИНА НЕТ В НАЛИЧИИ❗',
        'price': 2220,
        'weight': '357гр',
        'price_per_gram': 5.3,
        'photo': 'https://imgur.com/6OIEJT6'
    },
    '13': {
        'name': '🍵 Шуйсянь (владыка вод)',
        'description': 'Легкий с цветочными, табачными, фруктовыми и семечными нотами.',
        'price': 520,
        'weight': '50гр',
        'price_per_gram': 10.4,
        'photo': 'https://imgur.com/m8F5AK6'
    },
    '14': {
        'name': '🍵 Шоу мэй (брови старца)',
        'description': 'Белый чай Шоумэй очаровывает нежным ароматом сушеных злаков, шиповника и полевых цветов. Промытый лист дарит бархатистый, кисло-сладкий шлейф, напоминающий осеннюю листву и ароматные травы. Вкус чая плотный и гармоничный, сочетающий ноты трав, спелых фруктов и розовых лепестков. С каждым проливом, начиная с четвертого, вкус становится насыщеннее, раскрываясь оттенками вяленого изюма, кураги и освежающего компота из сухофруктов.',
        'price': 310,
        'weight': '50гр',
        'price_per_gram': 6.2,
        'photo': 'https://imgur.com/0JezVc7'
    },
    # Добавляем наборы
    '15': {
        'name': '🆕 Набор новичок 📦',
        'description': 'Белый чай - Шоу Мэй 10гр\nЗеленый чай- Дафо Лунцзин 10гр\nТёмный Улун - Да Хун Пао 10гр\nТёмный Улун - Шуйсянь 10гр\nСветлый Улун - Те Гуань Инь 10гр\nШу Пуэр 2021г «Юаньфэй» 10гр\nШу Пуэр 2019г «3 звезды» 10гр\nШу Пуэр 2021г «бык из Нака меняет мир» 10гр\nШу Пуэр 2016г «Наньно» 10гр\nШу Пуэр 2017г «Гунтин» 10гр\nШу Пуэр 2005г «двор чайного короля» 10гр\nШен Пуэр 2020г «Гора Бада» 10гр\nШен Пуэр 2018г «золотая нить» 10гр\nШен Пуэр 2013г «7543» 10гр',
        'price': 1000,
        'weight': 'набор 140гр',
        'photo': 'https://imgur.com/uCNbGJt',
        'is_set': True
    },
    '16': {
        'name': '🥴 Пьяный набор 📦',
        'description': 'Да Хун Пао 20гр\nШуйсянь 20гр\nТе Гуань Инь 20гр\nШен Пуэр 2020г 20гр\nШен Пуэр 2018г 20гр\nШен Пуэр 2013г 20гр',
        'price': 1000,
        'weight': 'набор 120гр',
        'photo': 'https://imgur.com/AtSrDi3',
        'is_set': True
    },
    '17': {
        'name': '🏋️ Бодрый набор 📦',
        'description': 'Шу Пуэр 2021г «Юаньфэй» 30гр\nШу Пуэр 2019г «3 звезды» 30гр\nШу Пуэр 2021г «бык из Нака меняет мир» 30гр\nШу Пуэр 2017г «Гунтин» 30гр\nДафо Лунцзин 20гр\nШен Пуэр 2020г «Гора Бада» 20гр',
        'price': 1000,
        'weight': 'набор 160гр',
        'photo': 'https://imgur.com/zjZ0yNa',
        'is_set': True
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

# Показ информации о чае с фото
async def show_tea_info(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    product = CATALOG[product_id]
    
    # Формируем текст описания
    caption = f"{product['name']}\n\n"
    
    # Добавляем описание только если оно есть
    if product['description']:
        caption += f"{product['description']}\n\n"
    
    # Для наборов не показываем цену за грамм
    if product.get('is_set'):
        caption += f"💰 Цена: {product['price']}₽/{product['weight']}\n\n"
    else:
        caption += (
            f"💰 Цена: {product['price']}₽/{product['weight']}\n"
            f"📊 Цена за 1гр: {product['price_per_gram']}₽\n\n"
        )
    
    # Для наборов не запрашиваем количество грамм
    if product.get('is_set'):
        caption += "✅ Это готовый набор. Добавить в корзину?"
        keyboard = [
            [InlineKeyboardButton("✅ Да, добавить набор", callback_data=f"add_set_{product_id}")],
            [InlineKeyboardButton("↩️ Назад в каталог", callback_data="back_catalog")]
        ]
    else:
        caption += "Введите количество грамм:"
        keyboard = [
            [InlineKeyboardButton("↩️ Назад в каталог", callback_data="back_catalog")]
        ]
    
    # Сохраняем выбранный товар
    context.user_data['selected_product'] = product_id
    
    # Отправляем фото с описанием (если есть фото)
    try:
        if product['photo'] and product['photo'].startswith('http'):
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=product['photo'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Если фото нет, отправляем текстовое сообщение
            await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        # Если ошибка при отправке фото, отправляем текстовое сообщение
        print(f"Ошибка отправки фото: {e}")
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard))

# Добавление набора в корзину
async def add_set_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    product = CATALOG[product_id]
    
    # Инициализируем корзину
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    # Добавляем набор в корзину
    user_carts[user_id].append({
        'product_id': product_id,
        'grams': product['weight'],
        'price': product['price'],
        'name': product['name']
    })
    
    await query.edit_message_text(f"✅ Добавлено в корзину: {product['name']}")

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
        product = CATALOG.get(item['product_id'], {})
        cart_text += f"{i+1}. {item['name']}\n"
        cart_text += f"   {item['grams']} - {item['price']}₽\n\n"
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
    await update.message.reply_text("📱 Введите ваш номер телефона (например: +79123456789):")
    return PHONE

# Обработка номера телефона
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.text
    
    if user_id not in user_orders:
        await update.message.reply_text("❌ Ошибка заказа. Начните заново.")
        return ConversationHandler.END
    
    # Простая валидация номера телефона
    if not any(char.isdigit() for char in phone) or len(phone) < 5:
        await update.message.reply_text("❌ Пожалуйста, введите корректный номер телефона (например: +79123456789 или 89123456789):")
        return PHONE
    
    user_orders[user_id]['phone'] = phone
    user_orders[user_id]['username'] = update.effective_user.username or "Не указан"
    user_orders[user_id]['user_id'] = user_id
    
    # Формируем подтверждение
    order = user_orders[user_id]
    confirm_text = "✅ Подтвердите заказ:\n\n"
    confirm_text += f"🏙️ Город: {order['city']}\n"
    confirm_text += f"👤 ФИО: {order['fio']}\n"
    confirm_text += f"📱 Телефон: {order['phone']}\n\n"
    confirm_text += "🛒 Состав заказа:\n"
    
    total = 0
    for item in order['cart']:
        confirm_text += f"• {item['name']} - {item['grams']} - {item['price']}₽\n"
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
    order_text += f"📱 Телефон: {order['phone']}\n"
    order_text += f"📞 Username: @{order['username']}\n"
    order_text += f"🆔 ID: {order['user_id']}\n"
    order_text += f"🏙️ Город: {order['city']}\n\n"
    order_text += "📦 Состав заказа:\n"
    
    total = 0
    for item in order['cart']:
        order_text += f"• {item['name']} - {item['grams']} - {item['price']}₽\n"
        total += item['price']
    
    order_text += f"\n💵 Итого: {total}₽"
    
    # Отправляем продавцу
    try:
        seller_chat_id = "1868127211"  # Замените на реальный chat_id
        await context.bot.send_message(chat_id=seller_chat_id, text=order_text)
        print(f"✅ Уведомление отправлено продавцу: {order_text}")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления продавцу: {e}")
        # Альтернативный вариант
        try:
            await context.bot.send_message(chat_id="@moychai181", text=order_text)
            print(f"✅ Уведомление отправлено через @moychai181")
        except Exception as e2:
            print(f"❌ Ошибка отправки через @moychai181: {e2}")
            # Сохраняем заказ в лог
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
        
        # Проверяем, не является ли товар набором
        if product.get('is_set'):
            await update.message.reply_text("❌ Это готовый набор. Используйте кнопку для добавления.")
            return
            
        # Рассчитываем цену за указанное количество грамм
        price_for_grams = round(product['price_per_gram'] * grams)
        
        # Инициализируем корзину
        if user_id not in user_carts:
            user_carts[user_id] = []
        
        # Добавляем товар в корзину
        user_carts[user_id].append({
            'product_id': product_id,
            'grams': f"{grams}г",
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
    
    elif data == "back_catalog":
        await query.delete_message()
        await show_catalog(update, context)
    
    elif data.startswith("view_"):
        product_id = data.split("_")[1]
        # Удаляем сообщение с кнопками каталога
        await query.delete_message()
        # Показываем информацию о чае с фото
        await show_tea_info(update, context, product_id)
    
    elif data.startswith("add_set_"):
        product_id = data.split("_")[2]
        await add_set_to_cart(update, context, product_id)
    
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
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
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