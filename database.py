import sqlite3
from datetime import datetime


def init_db():
    with sqlite3.connect("data/dava_bayer.db") as conn:
        cur = conn.cursor()

        cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            photo TEXT,
            price INTEGER
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            created_at TEXT
        )
        ''')

        conn.commit()

        """
        cur.execute("DELETE FROM products")
        products = products = [
            ("Штани", "Чорні джогери", "Зручні штани для повсякденного носіння", "logo.png", 650),
            ("Худі", "Синє худі", "Тепле худі з капюшоном", "logo.png", 750),
            ("Шорти", "Спортивні шорти", "Легкі шорти для тренувань", "logo.png", 400),
            ("Взуття", "Кросівки Nike", "Бігові кросівки з амортизацією", "logo.png", 1200),
            ("Аксесуари", "Ремінь", "Шкіряний ремінь чорного кольору", "logo.png", 300),
            ("Шапки", "Зимова шапка", "Шапка з флісовою підкладкою", "logo.png", 250),
            ("Рукавиці", "Рукавиці вовняні", "Теплі рукавиці з орнаментом", "logo.png", 200),
            ("Футболки", "Футболка біла", "Класична біла футболка з бавовни", "logo.png", 350)
        ]
        cur.executemany('''
            INSERT INTO products (category, name, description, photo, price)
            VALUES (?, ?, ?, ?, ?)
        ''', products)

        # Користувач
        cur.execute("DELETE FROM users")
        test_user = (123456789, "Ілля Тестовий", "test_user", datetime.now().isoformat())
        cur.execute('''
            INSERT OR REPLACE INTO users (user_id, full_name, username, created_at)
            VALUES (?, ?, ?, ?)
        ''', test_user)

        # Кошик (для тестового користувача)
        cur.execute("DELETE FROM cart")
        cart_items = [
            (123456789, 1, 2),  # 2 мийних засоби
            (123456789, 2, 1),  # 1 крем
        ]
        cur.executemany('''
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (?, ?, ?)
        ''', cart_items)

        conn.commit()
        print("Базу даних ініціалізовано та заповнено тестовими даними.")
        """

if __name__ == "__main__":
    init_db()
