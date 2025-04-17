from backend.database import get_connection

# LOGIN vulnerable (para pruebas de inyección SQL)
def login_inseguro(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    # Consulta vulnerable intencionalmente
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user

# REGISTRO seguro (solo para tener usuarios)
def registrar_usuario(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
