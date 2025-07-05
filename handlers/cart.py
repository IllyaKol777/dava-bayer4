from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

router = Router()

@router.callback_query(F.data.startswith("add_to_cart:"))
async def add_to_cart(call: CallbackQuery):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[1])

    conn = sqlite3.connect("data/dava_bayer.db")
    cur = conn.cursor()

    cur.execute("SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
    result = cur.fetchone()

    if result:
        cur.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id=? AND product_id=?", (user_id, product_id))
    else:
        cur.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)", (user_id, product_id))

    conn.commit()
    conn.close()

    await call.answer("Товар додано в кошик ✅", show_alert=False)


@router.message(F.text == "🛒 Кошик")
async def show_cart(message: Message):
    user_id = message.from_user.id

    conn = sqlite3.connect("data/dava_bayer.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT cart.product_id, products.name, products.price, cart.quantity 
        FROM cart 
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    """, (user_id,))
    items = cur.fetchall()
    conn.close()

    if not items:
        await message.answer("Ваша корзина порожня 🛒")
        return

    total = 0
    for product_id, name, price, quantity in items:
        subtotal = price * quantity
        total += subtotal

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Видалити", callback_data=f"remove_from_cart:{product_id}")]
        ])

        await message.answer(
            f"<b>{name}</b>\n💰 Ціна: {price} грн\n🔢 Кількість: {quantity}\n📦 Сума: {subtotal} грн",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    checkout_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оформити замовлення", callback_data="order")]
    ])
    await message.answer(f"Загальна сума: <b>{total}</b> грн", parse_mode="HTML", reply_markup=checkout_btn)


@router.callback_query(F.data.startswith("remove_from_cart:"))
async def remove_from_cart(call: CallbackQuery):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[1])

    conn = sqlite3.connect("data/dava_bayer.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()

    await call.answer("Товар видалено 🗑")
    await call.message.delete()

