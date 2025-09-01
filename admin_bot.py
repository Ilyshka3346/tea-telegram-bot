import os
import json
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters, ConversationHandler
)

# Вместо dotenv используем os.environ для простоты
ADMIN_BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '8254583426:AAG--jMQKwkpo-ExLZDcaGiA1NcYiIc0-uY')
ADMIN_CHAT_ID = int(os.environ.get('ADMIN_CHAT_ID', '6236736863'))

# Состояния для ConversationHandler
(
    SELECT_ACTION, SELECT_TYPE, GET_PHOTO, GET_DESCRIPTION, 
    GET_PRICE, GET_WEIGHT, CONFIRM_ADD
) = range(7)

# Временное хранилище для данных товара
temp_products = {}

# Главное меню админа
admin_keyboard = [
    ['➕ Добавить товар', '📋 Посмотреть каталог'],
    ['❌ Удалить товар', '🔄 Обновить товар']
]

# Загрузка каталога
def load_catalog():
    try:
        with open('catalog.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Сохранение каталога
def save_catalog(catalog):
    with open('catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

# Проверка прав администратора
def is_admin(chat_id):
    return chat_id == ADMIN_CHAT_ID

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_chat.id):
        await update.message.reply_text("❌ У вас нет прав доступа к этому боту.")
        return
    
    reply_markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Добро пожаловать в панель администратора!\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

# Начало добавления товара
async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_chat.id):
        return
    
    keyboard = [
        [InlineKeyboardButton("🍵 Чай", callback_data="type_tea")],
        [InlineKeyboardButton("📦 Набор", callback_data="type_set")],
        [InlineKeyboardButton("↩️ Назад", callback_data="back_admin")]
    ]
    
    await update.message.reply_text(
        "Выберите тип товара:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_TYPE

# Обработка выбора типа
async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_admin":
        await query.edit_message_text("Возврат в главное меню...")
        reply_markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
        await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        return ConversationHandler.END
    
    product_type = query.data.split("_")[1]
    user_id = query.from_user.id
    
    # Инициализируем временные данные
    temp_products[user_id] = {
        'type': product_type,
        'photo': None,
        'description': '',
        'price': None,
        'weight': None
    }
    
    await query.edit_message_text(
        "📸 Отправьте фото товара (можно отправить как файл или ссылку на Imgur):"
    )
    return GET_PHOTO

# Обработка фото
async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if update.message.photo:
        # Получаем самое большое фото
        photo = update.message.photo[-1]
        temp_products[user_id]['photo'] = photo.file_id
    elif update.message.text and update.message.text.startswith(('http://', 'https://')):
        temp_products[user_id]['photo'] = update.message.text
    else:
        await update.message.reply_text("❌ Пожалуйста, отправьте валидное фото или ссылку:")
        return GET_PHOTO
    
    if temp_products[user_id]['type'] == 'tea':
        await update.message.reply_text("📝 Введите описание чая (можно пропустить, отправив '-'):")
    else:
        await update.message.reply_text("📝 Введите описание набора (можно пропустить, отправив '-'):")
    
    return GET_DESCRIPTION

# Обработка описания
async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    description = update.message.text
    
    if description != '-':
        temp_products[user_id]['description'] = description
    
    if temp_products[user_id]['type'] == 'tea':
        await update.message.reply_text("💰 Введите цену за грамм (например: 12.8):")
    else:
        await update.message.reply_text("💰 Введите цену за набор (например: 1000):")
    
    return GET_PRICE

# Обработка цены
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    try:
        price = float(update.message.text)
        temp_products[user_id]['price'] = price
        
        if temp_products[user_id]['type'] == 'tea':
            await update.message.reply_text("⚖️ Введите вес в граммах (например: 50):")
            return GET_WEIGHT
        else:
            await update.message.reply_text("⚖️ Введите общий вес набора (например: 'набор 150гр'):")
            return GET_WEIGHT
            
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите корректную цену (число):")
        return GET_PRICE

# Обработка веса
async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    weight = update.message.text
    temp_products[user_id]['weight'] = weight
    
    # Формируем предпросмотр
    product = temp_products[user_id]
    
    caption = f"📋 Предпросмотр товара:\n\n"
    caption += f"Тип: {'🍵 Чай' if product['type'] == 'tea' else '📦 Набор'}\n"
    
    if product['description']:
        caption += f"Описание: {product['description']}\n\n"
    
    if product['type'] == 'tea':
        caption += f"💰 Цена за грамм: {product['price']}₽\n"
        caption += f"⚖️ Вес: {product['weight']}гр\n"
        caption += f"💵 Итого: {product['price'] * float(product['weight'])}₽"
    else:
        caption += f"💰 Цена за набор: {product['price']}₽\n"
        caption += f"⚖️ Вес: {product['weight']}"
    
    # Отправляем предпросмотр
    keyboard = [
        [InlineKeyboardButton("✅ Добавить в каталог", callback_data="confirm_add")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_add")]
    ]
    
    try:
        if isinstance(product['photo'], str) and product['photo'].startswith(('http://', 'https://')):
            await update.message.reply_photo(
                photo=product['photo'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_photo(
                photo=product['photo'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        await update.message.reply_text(
            f"{caption}\n\n❌ Не удалось отправить фото. Ошибка: {e}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    return CONFIRM_ADD

# Подтверждение добавления
async def confirm_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "confirm_add":
        # Загружаем текущий каталог
        catalog = load_catalog()
        
        # Генерируем новый ID
        existing_ids = [int(k) for k in catalog.keys() if k.isdigit()]
        new_id = str(max(existing_ids + [0]) + 1) if existing_ids else "1"
        
        # Создаем запись товара
        product_data = temp_products[user_id]
        
        catalog[new_id] = {
            'name': '',
            'description': product_data['description'],
            'price': product_data['price'],
            'weight': product_data['weight'],
            'photo': product_data['photo'],
            'is_set': product_data['type'] == 'set'
        }
        
        if product_data['type'] == 'tea':
            catalog[new_id]['price_per_gram'] = product_data['price']
            catalog[new_id]['price'] = product_data['price'] * float(product_data['weight'])
        
        # Сохраняем каталог
        save_catalog(catalog)
        
        # Очищаем временные данные
        del temp_products[user_id]
        
        await query.edit_message_text("✅ Товар успешно добавлен в каталог!")
        
    else:
        # Отмена добавления
        del temp_products[user_id]
        await query.edit_message_text("❌ Добавление товара отменено.")
    
    # Возвращаем в главное меню
    reply_markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
    await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    
    return ConversationHandler.END

# Просмотр каталога
async def view_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_chat.id):
        return
    
    catalog = load_catalog()
    
    if not catalog:
        await update.message.reply_text("📋 Каталог пуст.")
        return
    
    catalog_text = "📋 Текущий каталог:\n\n"
    
    for product_id, product in catalog.items():
        catalog_text += f"ID: {product_id}\n"
        catalog_text += f"Тип: {'📦 Набор' if product.get('is_set') else '🍵 Чай'}\n"
        
        if product.get('is_set'):
            catalog_text += f"Цена: {product['price']}₽/{product['weight']}\n"
        else:
            catalog_text += f"Цена: {product['price']}₽ ({product.get('price_per_gram', 'N/A')}₽/г)\n"
        
        catalog_text += "─" * 20 + "\n"
    
    await update.message.reply_text(catalog_text)

# Отмена ConversationHandler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in temp_products:
        del temp_products[user_id]
    
    await update.message.reply_text("❌ Операция отменена.")
    return ConversationHandler.END

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_chat.id):
        return
    
    text = update.message.text
    
    if text == '📋 Посмотреть каталог':
        await view_catalog(update, context)
    elif text in ['❌ Удалить товар', '🔄 Обновить товар']:
        await update.message.reply_text("⚠️ Эта функция еще в разработке")

# Основная функция
def main():
    application = Application.builder().token(ADMIN_BOT_TOKEN).build()
    
    # ConversationHandler для добавления товара
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^➕ Добавить товар$'), start_add_product)],
        states={
            SELECT_TYPE: [CallbackQueryHandler(select_type)],
            GET_PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, get_photo)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            GET_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            GET_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
            CONFIRM_ADD: [CallbackQueryHandler(confirm_add)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Админ-бот запущен и работает...")
    application.run_polling()

if __name__ == '__main__':
    main()