import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect('hiring_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, type TEXT, result TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('hiring_pro.db')
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('hiring_pro.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row[0].encode()):
        return True
    return False

def add_history(username, action_type, result):
    conn = sqlite3.connect('hiring_pro.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (username, type, result) VALUES (?, ?, ?)", (username, action_type, result))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect('hiring_pro.db')
    c = conn.cursor()
    c.execute("SELECT type, result FROM history WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return [{"type": r[0], "result": r[1]} for r in rows]