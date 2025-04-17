import sqlite3

def get_connection():
    # Establece la conexión a la base de datos SQLite
    conn = sqlite3.connect("victim.db", check_same_thread=False)
    return conn

def setup():
    conn = get_connection()
    cursor = conn.cursor()

    # Crear tabla 'users' si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
