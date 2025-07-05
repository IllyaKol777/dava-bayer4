from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import shop_menu
from utils.texts import SHOP_TEXT
from database import sqlite3
from keyboards.inline import product_buttons
from aiogram.types import FSInputFile
import os

router = Router()

@router.message(F.text == "🛍 Магазин")
async def open_shop(message: Message):
    await message.answer(SHOP_TEXT, reply_markup=shop_menu)

@router.message(F.text.in_({"👖 Штани", "👕 Худі", "🩳 Шорти", "👟 Взуття", "🧢 Аксесуари", "🎩 Шапки", "🧤 Рукавиці", "👚 Футболки", "🧥 Куртки / Жилетки"}))
async def show_category(message: Message):
    category = message.text.split(' ', 1)[-1]
    with sqlite3.connect("data/dava_bayer.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, photo, price FROM products WHERE category=?", (category,))
        products = cur.fetchall()
        if not products:
            await message.answer(f"🔍 Наразі немає товарів у категорії <b>{category}</b>.", parse_mode="HTML")
            return
        for product in products:
            product_id, name, desc, photo, price = product
            photo = os.path.basename(photo)
            caption = f"<b>{name}</b>\n{desc}\n💵 {price} грн"
            photo = FSInputFile(os.path.join("static/uploads", photo))
            await message.answer_photo(photo=photo, caption=caption, reply_markup=product_buttons(product_id), parse_mode="HTML")
