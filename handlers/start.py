from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import main_menu
from utils.texts import WELCOME_TEXT
import sqlite3
from datetime import datetime

router = Router()

@router.message(F.text.in_({"/start", "🔙 Назад"}))
async def start_handler(message: Message):
    conn = sqlite3.connect("data/dava_bayer.db")
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM users WHERE user_id = ?", (message.from_user.id,))
    user_exists = cur.fetchone()

    if not user_exists:
        cur.execute('''
            INSERT INTO users (user_id, full_name, username, created_at)
            VALUES (?, ?, ?, ?)
        ''', (
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()

    conn.close()


    await message.answer(WELCOME_TEXT, reply_markup=main_menu)
