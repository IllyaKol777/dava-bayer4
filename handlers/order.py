from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.reply import main_menu
import sqlite3
from datetime import datetime

router = Router()

# ❗️Заміни на свій Telegram ID
ADMIN_ID = 6314661034

# Машина станів для оформлення замовлення
class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()

# Початок оформлення замовлення через інлайн кнопку
@router.callback_query(F.data == "order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Вкажіть ваше ім'я та прізвище:")
    await state.set_state(OrderState.waiting_for_name)
    await callback.answer()  # Закриває кружечок загрузки

@router.message(OrderState.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введіть номер телефону:")
    await state.set_state(OrderState.waiting_for_phone)

@router.message(OrderState.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введіть адресу доставки або відділення пошти:")
    await state.set_state(OrderState.waiting_for_address)

@router.message(OrderState.waiting_for_address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()

    conn = sqlite3.connect("data/dava_bayer.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    """, (message.from_user.id,))
    products = cur.fetchall()
    conn.close()

    if not products:
        await message.answer("Ваша корзина порожня ❌")
        await state.clear()
        return

    total = sum(price * quantity for _, price, quantity in products)
    product_list = "\n".join([
        f"• {name} — {price} грн × {quantity} шт = {price * quantity} грн"
        for name, price, quantity in products
    ])

    admin_text = (
        f"🛒 НОВЕ ЗАМОВЛЕННЯ:\n\n"
        f"👤 Ім'я: {data['name']}\n📞 Телефон: {data['phone']}\n📍 Адреса: {data['address']}\n\n"
        f"🛍 Товари:\n{product_list}\n\n"
        f"💰 Сума: {total} грн\n"
        f"Telegram: @{message.from_user.username or 'немає'}\n"
        f"ID: {message.from_user.id}"
    )

    await message.answer("✅ Дякуємо за замовлення! Ми скоро з вами звʼяжемося.")
    await message.answer("Повертаємо вас у головне меню ⬇️", reply_markup=main_menu)
    await state.clear()

    await message.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

    conn = sqlite3.connect("data/dava_bayer.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()
