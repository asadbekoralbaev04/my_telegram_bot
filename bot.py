# =========================================
# File: telegram_bot/bot.py
# =========================================

import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from aiogram.filters import Command
from aiogram import F
from aiogram.filters.callback_data import CallbackData
import os

# =========================
# BOT VA USTOZ
BOT_TOKEN = "8382037003:AAEj6c23EtMLYOeeftwRnWvQY_RaxmF9vPw"
USTOZ_ID = 1122869478  # ustozning telegram ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# JSON fayl
# File: telegram_bot/students.json
@dp.message(Command("students"))
async def show_groups_to_teacher(message: types.Message):
    if message.from_user.id != USTOZ_ID:
        return

    load_students()  # <<< SHU QATORNI QO‘SH

    await message.answer("Guruhni tanlang:", reply_markup=groups_keyboard_for_teacher())

DATA_FILE = "students.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        students_data = json.load(f)
else:
    students_data = {}

# >>> SHU YERGA QO‘SH <<<
def load_students():
    global students_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            students_data = json.load(f)
    else:
        students_data = {}
# =========================
# Location tugmasi
location_button = KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)
keyboard_location = ReplyKeyboardMarkup(keyboard=[[location_button]], resize_keyboard=True)

# =========================
# Til tanlash uchun callback
class LanguageCallback(CallbackData, prefix="lang"):
    lang: str

language_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="O‘zbekcha", callback_data=LanguageCallback(lang="uz").pack())],
    [InlineKeyboardButton(text="Qaraqalpaqsha", callback_data=LanguageCallback(lang="qq").pack())]
])

# =========================
# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = str(message.from_user.id)

    if message.from_user.id == USTOZ_ID:
        await message.answer("Assalomu alaykum, ustoz!\n/students buyrug‘ini yuboring.")
        return

    if user_id in students_data:
        students_data.pop(user_id)

    await message.answer("Tilni tanlang:", reply_markup=language_keyboard)

# =========================
# Til tanlash
@dp.callback_query(LanguageCallback.filter())
async def choose_language(callback: types.CallbackQuery, callback_data: LanguageCallback):
    user_id = str(callback.from_user.id)
    lang = callback_data.lang
    students_data[user_id] = {"lang": lang}

    if lang == "uz":
        await callback.message.answer(
            "Assalomu alaykum! Amaliyotga kelganingizni ro‘yxatga olish uchun ma’lumotlaringizni yuboring.\n\nIsmingizni yozing:"
        )
    else:
        await callback.message.answer(
            "Assalawma aleykum! Ámeliyatqa kelgeninizdi dizimge alıw ushın maǵlıwmatlarıńızdı jiberiń.\n\nAtıńızdı jazıń:"
        )
    await callback.answer()

# =========================
# Ism, familiya, guruh
@dp.message(F.text)
async def handle_name(message: types.Message):
    if message.from_user.id == USTOZ_ID:
        return

    user_id = str(message.from_user.id)
    user = students_data.get(user_id, {})

    if "name" not in user:
        user["name"] = message.text
        students_data[user_id] = user
        await message.answer("Familiyangizni yozing:")
        return

    if "surname" not in user:
        user["surname"] = message.text
        students_data[user_id] = user
        await message.answer("Guruhingizni yozing:")
        return

    if "group" not in user:
        user["group"] = message.text
        students_data[user_id] = user
        await message.answer("Endi location yuboring:", reply_markup=keyboard_location)
        return

# =========================
# Location
@dp.message(F.content_type == ContentType.LOCATION)
async def location_handler(message: types.Message):
    if message.from_user.id == USTOZ_ID:
        return

    user = students_data.get(user_id)
    if not user:
        await message.answer("Avval /start bosing.")
        return

    user["lat"] = message.location.latitude
    user["lon"] = message.location.longitude

    await message.answer("✅ Location saqlandi, endi rasm yuboring:")

# =========================
# Photo
@dp.message(F.content_type == ContentType.PHOTO)
async def photo_handler(message: types.Message):
    if message.from_user.id == USTOZ_ID:
        return

    user_id = str(message.from_user.id)
    user = students_data.get(user_id)

    photo = message.photo[-1]
    file_id = photo.file_id

    user["photo_file_id"] = file_id

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(students_data, f, ensure_ascii=False, indent=4)

    await bot.send_photo(
        USTOZ_ID,
        file_id,
        caption=f"👤 {user['name']} {user['surname']}\n🎓 Guruh: {user['group']}"
    )

    if "lat" in user and "lon" in user:
        await bot.send_location(USTOZ_ID, user["lat"], user["lon"])

    await message.answer("✅ Ma’lumotlar yuborildi!")

# =========================
# USTOZ PANEL

def groups_keyboard_for_teacher():
    groups = sorted({u["group"] for u in students_data.values() if "group" in u})
    buttons = [[InlineKeyboardButton(text=g, callback_data=f"group:{g}")] for g in groups]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def students_keyboard_for_teacher(group):
    buttons = []
    for uid, s in students_data.items():
        if s.get("group") == group:
            buttons.append([InlineKeyboardButton(text=f"{s['name']} {s['surname']}", callback_data=f"student:{uid}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:groups")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# =========================
# /students
@dp.message(Command("students"))
async def show_groups_to_teacher(message: types.Message):
    if message.from_user.id != USTOZ_ID:
        return
    load_students()
    await message.answer("Guruhni tanlang:", reply_markup=groups_keyboard_for_teacher())

@dp.callback_query(F.data.startswith("group:"))
async def show_students_in_group(callback: types.CallbackQuery):
    group = callback.data.split(":")[1]

    if callback.message and callback.message.text:
        try:
            await callback.message.edit_text(
                f"{group} guruhi talabalari:",
                reply_markup=students_keyboard_for_teacher(group)
            )
        except Exception:
            await bot.send_message(
                callback.from_user.id,
                f"{group} guruhi talabalari:",
                reply_markup=students_keyboard_for_teacher(group)
            )
    else:
        await bot.send_message(
            callback.from_user.id,
            f"{group} guruhi talabalari:",
            reply_markup=students_keyboard_for_teacher(group)
        )

    await callback.answer()


@dp.callback_query(F.data.startswith("student:"))
async def show_student_details(callback: types.CallbackQuery):
    uid = callback.data.split(":")[1]
    s = students_data.get(uid)

    text = f"👤 {s['name']} {s['surname']}\n🎓 Guruh: {s['group']}"

    buttons = []
    buttons.append([InlineKeyboardButton(text="📍 Location", callback_data=f"loc:{uid}")])
    buttons.append([InlineKeyboardButton(text="🖼 Rasm", callback_data=f"photo:{uid}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back:group:{s['group']}")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data.startswith("loc:"))
async def show_location(callback: types.CallbackQuery):
    uid = callback.data.split(":")[1]
    s = students_data.get(uid)
    await bot.send_location(callback.from_user.id, s["lat"], s["lon"])
    await callback.answer()

@dp.callback_query(F.data.startswith("photo:"))
async def show_photo(callback: types.CallbackQuery):
    uid = callback.data.split(":")[1]
    s = students_data.get(uid)

    buttons = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back:group:{s['group']}")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_photo(callback.from_user.id, s["photo_file_id"], reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data == "back:groups")
async def back_to_groups(callback: types.CallbackQuery):
    if callback.from_user.id != USTOZ_ID:
        await callback.answer("❌ Ruxsat yo‘q", show_alert=True)
        return

    load_students()

    if callback.message.text:
        await callback.message.edit_text(
            "Guruhni tanlang:",
            reply_markup=groups_keyboard_for_teacher()
        )
    else:
        await callback.message.delete()
        await bot.send_message(
            callback.from_user.id,
            "Guruhni tanlang:",
            reply_markup=groups_keyboard_for_teacher()
        )

    await callback.answer()


@dp.callback_query(F.data.startswith("back:group:"))
async def back_to_group(callback: types.CallbackQuery):
    group = callback.data.split("back:group:")[1]

    # Xabar mavjud va text bo‘lsa edit qiling
    if callback.message and callback.message.text:
        try:
            await callback.message.edit_text(
                f"{group} guruhi talabalari:",
                reply_markup=students_keyboard_for_teacher(group)
            )
        except Exception as e:
            # Agar edit_text ishlamasa, yangi xabar yuboramiz
            await bot.send_message(
                callback.from_user.id,
                f"{group} guruhi talabalari:",
                reply_markup=students_keyboard_for_teacher(group)
            )
    else:
        # Xabar yo‘q bo‘lsa yangi xabar yuboramiz
        await bot.send_message(
            callback.from_user.id,
            f"{group} guruhi talabalari:",
            reply_markup=students_keyboard_for_teacher(group)
        )

    await callback.answer()


# =========================
# RUN
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
