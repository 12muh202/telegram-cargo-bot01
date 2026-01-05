#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот для массовой рассылки грузов
С приветствием и командой /routes
"""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import firebase_admin
from firebase_admin import credentials, firestore
import re

# ============================================
# НАСТРОЙКИ
# ============================================

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8295664698:AAELQC6gVYapki9lqWstmJ9dtDMonNMOX_E"

# Firebase конфигурация
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "muhammadamin-efb47",
    "private_key_id": "34bb6539bf7116b30add63475d032b3ec96be261",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCleVXeJ+TdLnp9\n6TvGa/GvwX6y2OF5NUps8KUrMNR/1pS+ODSV3I6ftCRA98gN+YnvgMelc3q3yucX\nYb1WoGBJ6EzbpzmqcUdtGv56w/+kDpL9+xfJaxw4DMmGmB6ZzBUthZQiCU7xzuF0\njLbrCL6+fyLnRuJ/9/LCn+fUYhz1o7VKR6nsSitVbJrqzDQRcvQm6kUGr9hR3SM0\n0u7FmG1bBSsnmre6wQ9Whbg2mjtifQBjgAbx4Cd5icQAPwWloVj/cj46Tnp3gWIb\nZl10Nvri0LAfa7Y8uhzpQQZNDDRJQGlJZq1Ge1VIYbDeIFZ+7snqS1Y2CoV+FGNd\nbYkUBVDnAgMBAAECggEAS1zvlrZkrbe1YhMPflc7Q+jEY4ATcLispOEU2I7suSxp\nohjHGlnROzs4J76yBmtYPxRP2TK2+W4XwbZqHUH9mKuMFZ4bzVy6Qx7AN/l8PKPG\nnpX1R27Y804fmoU9qp4gJxNnW/kRU1/9nq9Xv8PD287bfqnyDoZGsg1R8JCez+B6\nzaprxrkTZ5dx+d7DPBnqg26Ax6hZkCwr4rejyz1zo6tnWUT4zwQzI1JmoOt9vVCl\nlQcWQ/8FxjFvZSUbR0D9uU7pzElUKrA3voZaXQNKVE/mWxLsxJm0AB/SWH0gKXVB\nRYUzgp1k2mBDZODP+IWCNU/D0RwnmNqeddhqByhxwQKBgQDmW9ycboquwDcJSNOi\n0NyhrBXAhgkKy3qjfr+JDkzhojyP0Ha1X1CzDIeTHpINf/3UVVVuQ9aA2cTCfVFc\nBFCq4a87Ccx/KsCocbUC+qp2i5ySD7O6DzyH912c6cXLWJTfGIH4GvhetdBim853\n65HapwO4qYgSAKt1+cyieAQ0+wKBgQC35I+/vcrKLg64QFOTJiBi1S+9Dne5EsoA\nyMb5R9rSdBvg8Z9/RQcWcZq0vmdKSL71Y8HLSm7XgFnZ3VLL5l+G2WHT9JSkDntn\nZ7O/TxjFL0A9QWJspAAmUqubZ6u/aAM0mupk0v3JkEJrGgHS1MYqYlhY/uPPDAo+\n1JPL7A5YBQKBgQCyx9Kk+cnaLEXKh+Hwt+az9ul+3MfBwAAzSZh/V0Dl0NLtzp2C\n0DHCdFP4Iz65CX/HPl8qT633nItvYnE1WAf/R16HFGjIvTZ+xJj2cfLAREREu7kC\nCvcwkxPtRyWCVwJbTxr3on7minbrQP7x5TrylrJ1q+V2C10HF9LwuPKS5wKBgCvE\nXGo4U8GXAK3dsYZ+NosPTlNi1B/aVvWk06aU8YHRXKlHGL0DwtIWq8mE37SQZ9Kj\nsYYe6w6jX784q/IXnHjN2DjIJ3B8eeZ8ig1oV+7mdhWeMDzHM7nrRyivnfLqYIju\nrgbdKMYGbahsAi8ZsSh5S6my0KmApheaJKsOPcO5AoGBAMRby48m0T8xg2RL4SSf\n76mLJXR7/31rp+Jy/3RwfhUQU3/BJ6Z2IRWeedGveIdZxP/W4hRM5Lj5/KODA/xB\n4Jii5k0aVhQEh/n/IOXuHrhEY1ELwZhIeg+KLiET3I+Izm6Csy5rTB7MQYkQoMwt\nXo0ITaaXfWeBxe2lNGyYoX/x\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@muhammadamin-efb47.iam.gserviceaccount.com",
    "client_id": "106980942018291704595",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40muhammadamin-efb47.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Разрешенные Chat ID
ALLOWED_CHAT_IDS = [
    712426967,      # Гайрат
    6539699693,     # Админ
    7377972948,     # Нуриддин
]

# Курс сом
KGZ_RATE = 88.5

# ============================================
# ИНИЦИАЛИЗАЦИЯ FIREBASE
# ============================================

try:
    cred = credentials.Certificate(FIREBASE_CONFIG)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase подключен!")
except Exception as e:
    print(f"❌ Ошибка Firebase: {e}")
    db = None

# ============================================
# ФУНКЦИИ
# ============================================

def calculate_som(sum_dollar, yul_kira):
    """Расчет сомов"""
    try:
        total = float(sum_dollar or 0) + float(yul_kira or 0)
        return round(total * KGZ_RATE)
    except:
        return 0

def format_flight_name(file_name):
    """Форматирование названия рейса"""
    if not file_name:
        return ""
    name = file_name.replace('.xlsx', '').replace('.xls', '')
    name = name.replace('F-', '').replace('f-', '').replace('F', '')
    return name.strip()

def extract_flight_number(file_name):
    """Извлечь номер рейса"""
    match = re.search(r'(\d+)', file_name)
    return match.group(1) if match else None

async def get_orders_from_firebase():
    """Загрузить рейсы из Firebase"""
    if not db:
        return []
    
    try:
        orders_ref = db.collection('orders')
        docs = orders_ref.stream()
        
        orders = []
        for doc in docs:
            data = doc.to_dict()
            orders.append({
                'id': doc.id,
                'fileName': data.get('fileName', ''),
                'data': data.get('data', []),
                'userEmail': data.get('userEmail', '')
            })
        
        print(f"✅ Загружено {len(orders)} рейсов")
        return orders
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return []

async def get_users_from_firebase():
    """Получить список пользователей (аккаунтов)"""
    orders = await get_orders_from_firebase()
    users = set()
    
    for order in orders:
        email = order.get('userEmail', '')
        if email:
            users.add(email)
    
    return sorted(list(users))

def is_valid_cargo(row_data):
    """Проверка что груз не пустой"""
    if not row_data or len(row_data) < 6:
        return False
    
    fio = str(row_data[1] or '').strip()
    phone = str(row_data[4] or '').strip()
    name = str(row_data[5] or '').strip()
    
    filled_fields = sum([bool(fio), bool(phone), bool(name)])
    return filled_fields >= 2

def safe_float(value):
    """Безопасное преобразование в число"""
    if value is None or value == '':
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = ''.join(c for c in str(value) if c.isdigit() or c in '.-')
    try:
        return float(cleaned) if cleaned and cleaned not in '.-' else 0.0
    except:
        return 0.0

def create_cargo_message(flight_name, row_data, employee, status, payment_date):
    """Создать сообщение о грузе"""
    try:
        sum_dollar = safe_float(row_data[11]) if len(row_data) > 11 else 0.0
        yul_kira = safe_float(row_data[12]) if len(row_data) > 12 else 0.0
        som = calculate_som(sum_dollar, yul_kira)
        
        message = f"""📦 <b>Информация о грузе</b>

🏷️ <b>Рейс:</b> {flight_name}
👤 <b>ФИО:</b> {row_data[1] if len(row_data) > 1 else '-'}
📞 <b>Телефон:</b> {row_data[4] if len(row_data) > 4 else '-'}
📍 <b>Город:</b> {row_data[2] if len(row_data) > 2 else '-'}
📦 <b>Наименование:</b> {row_data[5] if len(row_data) > 5 else '-'}
📊 <b>Место:</b> {row_data[6] if len(row_data) > 6 else '-'}
⚖️ <b>КГ:</b> {row_data[9] if len(row_data) > 9 else '-'}
💰 <b>Цена:</b> {row_data[10] if len(row_data) > 10 else '-'} $
💵 <b>Сумма:</b> {sum_dollar:.2f} $
🚛 <b>Йул кира:</b> {yul_kira:.2f} $
🇰🇬 <b>Сом:</b> {som:,} с

👷 <b>Сотрудник:</b> {employee or 'Не назначен'}
✅ <b>Статус:</b> {'Оплачено ✅' if status == 'оплачено' else 'Не оплачено ❌'}"""
        
        if payment_date:
            message += f"\n📅 <b>Дата:</b> {payment_date}"
        
        return message
    except Exception as e:
        return f"❌ Ошибка: {e}"

# ============================================
# КОМАНДЫ БОТА
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие"""
    chat_id = update.effective_chat.id
    
    if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
        await update.message.reply_text(
            f"❌ Нет доступа\n\nВаш Chat ID: <code>{chat_id}</code>",
            parse_mode='HTML'
        )
        return
    
    # ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ
    welcome_text = """🚚 <b>Kargo_Express</b>

Добро пожаловать!
Мы занимаемся карго-доставкой из Узбекистана 🇺🇿 в Кыргызстан 🇰🇬

📦 Быстро
💰 Выгодно
🤝 Надёжно

Напишите, что хотите отправить — наш оператор ответит вам.

<b>Команды:</b>
/routes - Посмотреть рейсы и грузы
/help - Помощь"""
    
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def routes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /routes - показать выбор аккаунта"""
    chat_id = update.effective_chat.id
    
    if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
        await update.message.reply_text(
            f"❌ Нет доступа\n\nВаш Chat ID: <code>{chat_id}</code>",
            parse_mode='HTML'
        )
        return
    
    await show_account_selection(update, context)

async def show_account_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать выбор аккаунта"""
    users = await get_users_from_firebase()
    
    if not users:
        if update.callback_query:
            await update.callback_query.message.reply_text("📭 Нет аккаунтов в базе")
        else:
            await update.message.reply_text("📭 Нет аккаунтов в базе")
        return
    
    keyboard = []
    for user in users:
        display_name = user.replace('@gmail.com', '')
        keyboard.append([InlineKeyboardButton(f"👤 {display_name}", callback_data=f"user_{user}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "👥 <b>Выберите аккаунт:</b>\n\nВыберите пользователя для просмотра рейсов"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

async def show_flights_for_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_email: str):
    """Показать рейсы для выбранного пользователя"""
    query = update.callback_query
    await query.answer()
    
    orders = await get_orders_from_firebase()
    
    user_orders = [o for o in orders if o.get('userEmail') == user_email]
    
    if not user_orders:
        await query.message.edit_text(
            f"📭 У пользователя {user_email} нет рейсов",
            parse_mode='HTML'
        )
        return
    
    flights = {}
    for order in user_orders:
        flight_num = extract_flight_number(order['fileName'])
        if flight_num:
            flight_name = format_flight_name(order['fileName'])
            
            cargo_count = 0
            for i, row in enumerate(order['data']):
                if i > 0 and row.get('data'):
                    if is_valid_cargo(row.get('data', [])):
                        cargo_count += 1
            
            if flight_num not in flights:
                flights[flight_num] = {
                    'name': flight_name,
                    'count': 0
                }
            flights[flight_num]['count'] += cargo_count
    
    if not flights:
        await query.message.edit_text(
            f"📭 У пользователя {user_email} нет грузов",
            parse_mode='HTML'
        )
        return
    
    keyboard = []
    sorted_flights = sorted(flights.items(), key=lambda x: int(x[0]))
    
    for flight_num, data in sorted_flights:
        keyboard.append([
            InlineKeyboardButton(
                f"✈️ Рейс {flight_num} ({data['count']} грузов)",
                callback_data=f"flight_{user_email}_{flight_num}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад к аккаунтам", callback_data="back_to_accounts")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    display_name = user_email.replace('@gmail.com', '')
    message = f"✈️ <b>Рейсы пользователя {display_name}</b>\n\nВыберите рейс для отправки грузов:"
    
    await query.message.edit_text(
        message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def send_flight_cargos_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, user_email: str, flight_number: str):
    """Отправить грузы из выбранного рейса"""
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    
    await query.message.edit_text(f"🔍 Ищу рейс {flight_number}...")
    
    orders = await get_orders_from_firebase()
    
    matching_orders = []
    for order in orders:
        if order.get('userEmail') == user_email:
            order_num = extract_flight_number(order['fileName'])
            if order_num == flight_number:
                matching_orders.append(order)
    
    if not matching_orders:
        await query.message.edit_text(f"❌ Рейс {flight_number} не найден")
        return
    
    total_cargos = 0
    for order in matching_orders:
        for i, row in enumerate(order['data']):
            if i > 0 and row.get('data'):
                if is_valid_cargo(row.get('data', [])):
                    total_cargos += 1
    
    if total_cargos == 0:
        await query.message.edit_text(f"📭 Нет грузов в рейсе {flight_number}")
        return
    
    progress_msg = await query.message.edit_text(
        f"📤 <b>Отправка...</b>\n\n"
        f"✈️ Рейс: {flight_number}\n"
        f"📦 Грузов: {total_cargos}\n"
        f"⏳ Отправлено: 0/{total_cargos}",
        parse_mode='HTML'
    )
    
    sent_count = 0
    errors = 0
    
    for order in matching_orders:
        flight_name = format_flight_name(order['fileName'])
        
        for i, row in enumerate(order['data']):
            if i == 0:
                continue
            
            row_data = row.get('data', [])
            if not row_data:
                continue
            
            if not is_valid_cargo(row_data):
                continue
            
            employee = row.get('employee', '')
            status = row.get('status', 'не оплачено')
            payment_date = row.get('paymentDate', '')
            
            try:
                message = create_cargo_message(
                    flight_name, row_data, employee, status, payment_date
                )
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                
                sent_count += 1
                
                if sent_count % 5 == 0 or sent_count == total_cargos:
                    await progress_msg.edit_text(
                        f"📤 <b>Отправка...</b>\n\n"
                        f"✈️ Рейс: {flight_number}\n"
                        f"📦 Грузов: {total_cargos}\n"
                        f"✅ Отправлено: {sent_count}/{total_cargos}\n"
                        f"❌ Ошибок: {errors}",
                        parse_mode='HTML'
                    )
                
                await asyncio.sleep(0.3)
                
            except Exception as e:
                print(f"❌ Ошибка отправки: {e}")
                errors += 1
    
    keyboard = [[InlineKeyboardButton("🔙 Выбрать другой рейс", callback_data=f"user_{user_email}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await progress_msg.edit_text(
        f"✅ <b>Готово!</b>\n\n"
        f"✈️ Рейс: {flight_number}\n"
        f"📦 Грузов: {total_cargos}\n"
        f"✅ Успешно: {sent_count}\n"
        f"❌ Ошибок: {errors}",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    data = query.data
    
    if data == "back_to_accounts":
        await show_account_selection(update, context)
    
    elif data.startswith("user_"):
        user_email = data.replace("user_", "")
        await show_flights_for_user(update, context, user_email)
    
    elif data.startswith("flight_"):
        parts = data.replace("flight_", "").split("_")
        if len(parts) >= 2:
            user_email = "_".join(parts[:-1])
            flight_number = parts[-1]
            await send_flight_cargos_callback(update, context, user_email, flight_number)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """ℹ️ <b>Помощь</b>

<b>Команды:</b>
/start - Приветствие
/routes - Выбор аккаунта и рейса
/help - Эта помощь

<b>Как отправить грузы:</b>
1. Напиши /routes
2. Выбери аккаунт
3. Выбери рейс
4. Бот отправит все грузы

<b>О компании:</b>
🚚 Kargo_Express - карго-доставка 🇺🇿 ➡️ 🇰🇬"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')

# ============================================
# ЗАПУСК
# ============================================

def main():
    """Запуск бота"""
    print("🤖 Запуск бота...")
    print(f"📱 Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("routes", routes_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("✅ Бот запущен! Ctrl+C для остановки")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()