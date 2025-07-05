from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
import uuid
import asyncio
import json

from aiogram.types import Update
from bot import bot, dp  # Твій бот і dispatcher з усіма підключеними роутерами

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
DATABASE = 'data/dava_bayer.db'

WEBHOOK_URL = 'https://dava-bayer.onrender.com/webhook'  # Вкажи свій домен Render

CATEGORIES = [
    'Штани', 'Худі', 'Шорти', 'Взуття', 'Аксесуари', 'Шапки', 'Рукавиці', 'Куртки / Жилетки', 'Футболки'
]

# Підключення до БД
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Головна сторінка
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Додавання продукту
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        photo_file = request.files['photo']
        if photo_file:
            filename = secure_filename(photo_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            photo_file.save(photo_path)
            photo = '/' + photo_path
        else:
            photo = ''

        conn = get_db_connection()
        conn.execute('INSERT INTO products (category, name, description, photo, price) VALUES (?, ?, ?, ?, ?)',
                     (category, name, description, photo, price))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_product.html', categories=CATEGORIES)

# Редагування продукту
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        photo_file = request.files['photo']
        if photo_file and photo_file.filename != '':
            filename = secure_filename(photo_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            photo_file.save(photo_path)
            photo = '/' + photo_path
        else:
            photo = product['photo']

        conn.execute('''
            UPDATE products
            SET category = ?, name = ?, description = ?, photo = ?, price = ?
            WHERE id = ?
        ''', (category, name, description, photo, price, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_product.html', product=product, categories=CATEGORIES)

# Видалення продукту
@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Вебхук для Telegram
@app.route('/webhook', methods=['POST'])
async def process_webhook():
    try:
        raw_data = await request.get_data()
        update = Update.model_validate(json.loads(raw_data))
        await dp.feed_update(bot, update)
    except Exception as e:
        print('Помилка обробки:', e)
    return 'OK', 200

# Встановлення webhook перед першим запитом
@app.before_first_request
def setup_webhook():
    asyncio.run(bot.set_webhook(WEBHOOK_URL))
    print('Webhook встановлено:', WEBHOOK_URL)

if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(host='0.0.0.0', port=5000)




"""
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
import uuid
import threading
import asyncio
from aiogram.types import Update
from bot import bot, dp
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

DATABASE = 'data/dava_bayer.db'

CATEGORIES = [
    'Штани', 'Худі', 'Шорти', 'Взуття', 'Аксесуари', 'Шапки', 'Рукавиці', 'Куртки / Жилетки', 'Футболки'
]



def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)


@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        photo_file = request.files['photo']
        if photo_file:
            filename = secure_filename(photo_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            photo_file.save(photo_path)
            photo = '/' + photo_path
        else:
            photo = ''

        conn = get_db_connection()
        conn.execute('INSERT INTO products (category, name, description, photo, price) VALUES (?, ?, ?, ?, ?)',
                     (category, name, description, photo, price))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_product.html', categories=CATEGORIES)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        photo_file = request.files['photo']
        if photo_file and photo_file.filename != '':
            filename = secure_filename(photo_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            photo_file.save(photo_path)
            photo = '/' + photo_path
        else:
            photo = product['photo']

        conn.execute('''
            UPDATE products
            SET category = ?, name = ?, description = ?, photo = ?, price = ?
            WHERE id = ?
        ''', (category, name, description, photo, price, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_product.html', product=product, categories=CATEGORIES)


@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))



def run_flask():
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(host='0.0.0.0', port=5000)


def run_bot():
    asyncio.sleep(10)
    asyncio.run(bot_main())


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    
    
    run_bot()


def run_flask():
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(host='0.0.0.0', port=5000)

def run_bot_thread():
    asyncio.run(bot_main())

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    bot_thread = threading.Thread(target=run_bot_thread)
    flask_thread.start()
    bot_thread.start()
    flask_thread.join()
    bot_thread.join()


@app.route("/webhook", methods=["POST"])
async def process_webhook():
    try:
        raw_data = await request.get_data()
        update = Update.model_validate(json.loads(raw_data))
        await dp.feed_update(bot, update)
    except Exception as e:
        print("Помилка обробки:", e)
    return "OK", 200

if __name__ == "__main__":

    # Встановити webhook
    async def on_startup():
        webhook_url = "https://dava-bayer.onrender.com/webhook"
        await bot.set_webhook(webhook_url)

    asyncio.run(on_startup())
    app.run(host="0.0.0.0", port=5000)

"""