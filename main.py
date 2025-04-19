import telebot
from telebot import types
import datetime
import re
import os

bot = telebot.TeleBot("7858465354:AAEmhBMVosGXMFo0ah64GgPe8me0_umkwwA")
orders_file = "orders.txt"

menu_items = {
    "Lavash": 30000,
    "Burger": 25000,
    "Cola": 7000,
    "Pizza": 40000
}
savatcha = {}

user_states = {}

# === FOYDALI FUNKSIYALAR ===
def is_valid_phone(phone):
    return bool(re.match(r'^\+998(93|94|50|51|88|95|97|98|99|33)\d{7}$', phone))

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📜 Menyu", "🛒 Savatcha")
    markup.row("📦 Buyurtma berish", "🎁 Aksiya")
    markup.row("📍 Manzil")
    return markup

def menu_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in menu_items:
        markup.add(f"➕ {item}")
    markup.add("🔙 Ortga")
    return markup

def tolov_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Payme", url="https://payme.uz"))
    markup.add(types.InlineKeyboardButton("💳 Click", url="https://click.uz"))
    return markup

# === /START ===
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Assalomu alaykum! Kafemizga xush kelibsiz.", reply_markup=main_menu())

# === MENYU ===
@bot.message_handler(func=lambda msg: msg.text == "📜 Menyu")
def send_menu(message):
    text = "📋 Menyu:\n"
    for item, price in menu_items.items():
        text += f"{item} - {price} so'm\n"
    bot.send_message(message.chat.id, text, reply_markup=menu_buttons())

@bot.message_handler(func=lambda msg: msg.text == "🔙 Ortga")
def go_back(message):
    bot.send_message(message.chat.id, "🔙 Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

# === SAVATCHAGA QO‘SHISH ===
@bot.message_handler(func=lambda msg: msg.text.startswith("➕"))
def add_to_cart(message):
    item = message.text.replace("➕ ", "")
    if item in menu_items:
        savatcha.setdefault(message.from_user.id, []).append(item)
        bot.send_message(message.chat.id, f"✅ {item} savatchaga qo‘shildi.")
    else:
        bot.send_message(message.chat.id, "⚠ Noto‘g‘ri mahsulot!")

# === SAVATCHANI KO‘RISH ===
@bot.message_handler(func=lambda msg: msg.text == "🛒 Savatcha")
def view_cart(message):
    items = savatcha.get(message.from_user.id, [])
    if not items:
        bot.send_message(message.chat.id, "Savatchangiz bo‘sh.")
        return
    text = "🛒 Savatchangiz:\n"
    total = 0
    for item in items:
        text += f"- {item} ({menu_items[item]} so'm)\n"
        total += menu_items[item]
    text += f"\nJami: {total} so‘m"
    bot.send_message(message.chat.id, text, reply_markup=tolov_buttons())

# === BUYURTMA BERISH ===
@bot.message_handler(func=lambda msg: msg.text == "📦 Buyurtma berish")
def order_start(message):
    user_states[message.chat.id] = {"step": "name"}
    bot.send_message(message.chat.id, "Ismingizni kiriting:")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, {}).get("step") == "name")
def get_name(message):
    user_states[message.chat.id]["name"] = message.text
    user_states[message.chat.id]["step"] = "phone"
    bot.send_message(message.chat.id, "Telefon raqamingizni kiriting (masalan, +99893xxxxxxx):")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, {}).get("step") == "phone")
def get_phone(message):
    if not is_valid_phone(message.text):
        bot.send_message(message.chat.id, "⚠ Raqam noto‘g‘ri. +998 bilan kiriting.")
        return
    user_states[message.chat.id]["phone"] = message.text
    user_states[message.chat.id]["step"] = "address"
    bot.send_message(message.chat.id, "Manzilingizni kiriting:")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, {}).get("step") == "address")
def get_address(message):
    user_states[message.chat.id]["address"] = message.text
    user_states[message.chat.id]["step"] = "confirm"
    bot.send_message(message.chat.id, "Buyurtmani tasdiqlaysizmi? (Ha/Yoq)")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, {}).get("step") == "confirm")
def confirm_order(message):
    if message.text.lower() != "ha":
        bot.send_message(message.chat.id, "❌ Buyurtma bekor qilindi.", reply_markup=main_menu())
        user_states.pop(message.chat.id, None)
        return

    data = user_states[message.chat.id]
    items = savatcha.get(message.from_user.id, [])
    total = sum([menu_items[i] for i in items])
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order_text = f"Buyurtma ({time}):\nIsm: {data['name']}\nTel: {data['phone']}\nManzil: {data['address']}\n\n"
    order_text += "\n".join(items)
    order_text += f"\nJami: {total} so‘m\n"

    with open(orders_file, "a", encoding="utf-8") as f:
        f.write(order_text + "\n---\n")

    savatcha[message.from_user.id] = []
    user_states.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "✅ Buyurtma qabul qilindi. Tez orada yetkaziladi.", reply_markup=main_menu())

# === AKSIYA VA MANZIL ===
@bot.message_handler(func=lambda msg: msg.text == "📍 Manzil")
def manzil(message):
    bot.send_message(message.chat.id, "📍 Navoiy shahar, Mustaqillik ko‘chasi 12-uy")

@bot.message_handler(func=lambda msg: msg.text == "🎁 Aksiya")
def aksiya(message):
    bot.send_message(message.chat.id, "🎉 Bugungi aksiya: Lavash + Cola = 35 000 so‘m")

# === ISHGA TUSHURISH ===
bot.polling()
