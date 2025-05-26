import os
import pickle
import datetime
from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# Necesario para manejar solicitudes de origen cruzado en despliegue
# (frontend y backend en dominios diferentes)
from flask_cors import CORS 
# Aunque urllib.parse.urlparse está importado, no se usa directamente en este app.py.
# Lo mantengo por si tenías planes de usarlo o por consistencia con tus versiones anteriores.
from urllib.parse import urlparse 

app = Flask(__name__)
bcrypt = Bcrypt(app)

# --- Configuración de CORS (Descomenta y ajusta para despliegue) ---
# Si tu frontend y backend están en dominios diferentes (ej. Netlify y Render),
# NECESITAS habilitar CORS. Sé específico con los orígenes permitidos.
# Puedes añadir múltiples orígenes si tu frontend se despliega en varios lugares.
# CORS(app, resources={r"/*": {"origins": [
#     "https://tu-dominio-netlify.netlify.app", # <-- ¡REEMPLAZA CON EL DOMINIO REAL DE TU FRONTEND!
#     "http://localhost:3000",                  # Para desarrollo local de un frontend JS (ej. React)
#     "http://127.0.0.1:5000"                   # Si accedes al frontend desde la misma IP del backend en desarrollo
# ]}})

# --- Configuración de la Base de Datos ---
# Se obtiene la URL de la base de datos de la variable de entorno (ESENCIAL PARA DESPLIEGUE)
db_url = os.getenv('DATABASE_URL')

# --- CONFIGURACIÓN PARA DESARROLLO LOCAL ---
# Si la variable de entorno DATABASE_URL no está definida (común en desarrollo local),
# usa una URL predeterminada para tu PostgreSQL local.
# ¡CAMBIA 'tu_usuario', 'tu_contraseña' y 'nombre_de_tu_bd_local' con tus credenciales reales!
if not db_url:
    print("ADVERTENCIA: La variable de entorno DATABASE_URL no está definida. Usando configuración LOCAL predeterminada.")
    db_url = "postgresql://tu_usuario:tu_contraseña@localhost:5432/nombre_de_tu_bd_local" # <--- ¡CAMBIA ESTO PARA LOCAL!

# Render y SQLAlchemy prefieren 'postgresql://' en lugar de 'postgres://'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Clave secreta para sesiones y seguridad. ¡CAMBIA ESTO EN PRODUCCIÓN! ---
# Idealmente, usa una variable de entorno: os.getenv('SECRET_KEY')
# Para desarrollo local, proporciona una cadena segura por defecto.
app.secret_key = os.getenv('SECRET_KEY', 'una_clave_secreta_muy_larga_y_aleatoria_para_desarrollo_seguridad_app') 

db = SQLAlchemy(app)

# --- Modelos de SQLAlchemy ---

# Modelo de usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Modelo para los logs de ataques detectados
class LogAtaque(db.Model):
    __tablename__ = 'log_ataques'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    timestamp_ataque = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# --- Carga del Modelo de IA ---
# Asegúrate de que 'modelo_ataques.pkl' esté en una carpeta llamada 'modelo_ia'
# en la raíz de tu proyecto.
MODEL_PATH = 'modelo_ia/modelo_ataques.pkl' 
ai_model = None
# Si tu modelo requiere un vectorizador (ej. TfidfVectorizer) usado durante el entrenamiento,
# también deberías cargarlo aquí. Por ejemplo:
# VECTORIZER_PATH = 'modelo_ia/tu_vectorizador.pkl'
# vectorizer = None

try:
    with open(MODEL_PATH, 'rb') as f:
        ai_model = pickle.load(f)
    print(f"✅ Modelo de IA 'modelo_ataques.pkl' cargado exitosamente.")
    
    # Si tienes un vectorizador separado, cárgalo aquí:
    # with open(VECTORIZER_PATH, 'rb') as f_vec:
    #     vectorizer = pickle.load(f_vec)
    # print(f"✅ Vectorizador cargado exitosamente.")

except FileNotFoundError:
    print(f"❌ ERROR: Uno o ambos archivos del modelo/vectorizador no se encontraron en '{os.path.dirname(MODEL_PATH)}'.")
    print("Asegúrate de que la ruta sea correcta y los archivos .pkl existan.")
except Exception as e:
    print(f"❌ ERROR al cargar el modelo de IA o vectorizador: {e}")

# --- Función Auxiliar para Clasificar Texto con IA ---
def classify_text_with_ai(text_to_analyze):
    if ai_model is None:
        print("❌ Error: Modelo de IA no cargado, no se puede clasificar el texto.")
        # En producción, si el modelo no carga, considera devolver True (ataque) por seguridad.
        # Aquí, devolvemos False para no bloquear la app durante el desarrollo.
        return False 

    is_sqli_attack = False
    try:
        # --- ¡IMPORTANTE! REEMPLAZA LA SIMULACIÓN CON LA LÓGICA REAL DE TU MODELO ---
        # 1. PREPROCESAMIENTO: Si tu modelo espera texto preprocesado o vectorizado,
        #    realiza ese paso aquí. Por ejemplo, si usaste un TfidfVectorizer:
        # if vectorizer:
        #     processed_text = vectorizer.transform([text_to_analyze])
        # else:
        #     # Si el vectorizador no cargó, o tu modelo no lo necesita.
        #     processed_text = [text_to_analyze] # O algún otro formato que tu modelo espere.

        # 2. PREDICCIÓN: Llama al método .predict() de tu modelo.
        #    Asegúrate de que el formato de entrada sea el correcto (ej. una lista con el texto/vector).
        prediction = ai_model.predict([text_to_analyze]) 
        # O: prediction = ai_model.predict(processed_text) si usaste un vectorizador.

        # 3. INTERPRETACIÓN: Interpreta la salida de tu modelo.
        #    Si tu modelo es de clasificación binaria (ej. 0 para seguro, 1 para ataque):
        is_sqli_attack = (prediction[0] == 1) 

        # Si tu modelo devuelve probabilidades y necesitas un umbral:
        # probabilities = ai_model.predict_proba([text_to_analyze])
        # threshold = 0.5 # Ajusta este umbral según la curva ROC de tu modelo
        # is_sqli_attack = (probabilities[0][1] > threshold) # Probabilidad de ser la clase de ataque (asumiendo clase 1 es ataque)

        # --- FIN DEL BLOQUE DE REEMPLAZO ---

    except Exception as e:
        print(f"❌ Error durante la predicción del modelo de IA: {e}")
        # Por seguridad, si hay un error en la predicción, es mejor asumir que es un ataque.
        is_sqli_attack = True 

    return is_sqli_attack

# --- Rutas de la Aplicación ---

# Ruta principal: Sirve el archivo HTML de la aplicación web vulnerable.
@app.route('/')
def index():
    return render_template('VulnerableWeb (1).html')

# Ruta para el dashboard de ataques.
@app.route('/ataques.html')
def ataques_page():
    return render_template('ataques.html')

# Endpoint API para obtener los ataques detectados y mostrarlos en el dashboard.
@app.route('/api/attacks', methods=['GET'])
def get_attacks():
    try:
        # Consulta todos los ataques y los ordena por fecha y hora descendente.
        attacks = LogAtaque.query.order_by(LogAtaque.timestamp_ataque.desc()).all()
        formatted_attacks = []
        for attack in attacks:
            formatted_attacks.append({
                "id": attack.id,
                "fecha": attack.fecha.strftime('%Y-%m-%d'),
                "hora": attack.hora.strftime('%H:%M:%S')
            })
        print(f"✅ Enviando {len(formatted_attacks)} registros de ataques al dashboard.")
        return jsonify(formatted_attacks)
    except Exception as e:
        print(f"❌ Error al obtener ataques de la base de datos para el API: {e}")
        return jsonify({"status": "error", "message": "Error al recuperar los ataques detectados."}), 500

# --- Ruta para procesar comentarios con detección de SQLi ---
# ¡IMPORTANTE! Para que esta ruta funcione, el JavaScript en VulnerableWeb (1).html
# debe ser modificado para enviar los comentarios a este endpoint (ej. usando 'fetch').
@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    # Se espera que el comentario se envíe como un JSON con la clave 'commentText'.
    data = request.get_json()
    comment_text = data.get('commentText', '').strip()

    if not comment_text:
        return jsonify({"status": "error", "message": "No se recibió texto de comentario."}), 400

    print(f"💬 Recibido comentario para analizar: '{comment_text}'")

    # Clasifica el texto del comentario usando el modelo de IA.
    is_attack = classify_text_with_ai(comment_text)

    try:
        if is_attack:
            print(f"🚨 Ataque SQL detectado en comentario: '{comment_text}'")
            now = datetime.datetime.utcnow()
            # Registra el ataque en la base de datos.
            log_entry = LogAtaque(fecha=now.date(), hora=now.time(), timestamp_ataque=now)
            db.session.add(log_entry)
            db.session.commit()
            print("✅ Intento de ataque registrado en 'log_ataques'.")
            # Devuelve una respuesta de error al frontend.
            return jsonify({"status": "attack_detected", "message": "¡Intento de inyección SQL detectado en el comentario!"}), 403 # 403 Forbidden
        else:
            print(f"✅ Comentario seguro: '{comment_text}'.")
            # Si el comentario es seguro, aquí se guardaría en la base de datos (si hubiera una tabla de comentarios).
            # Por ahora, solo devuelve una confirmación de éxito.
            return jsonify({"status": "success", "message": "Comentario seguro y procesado."})
    except Exception as e:
        print(f"❌ Error en la operación de base de datos para submit_comment: {e}")
        db.session.rollback() # Deshace la transacción en caso de error.
        return jsonify({"status": "error", "message": "Error interno del servidor al procesar el comentario."}), 500

# Ruta de Registro de Usuario (con detección de SQLi en 'username')
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username') # Usar .get() para evitar KeyError si el campo no existe.
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Clasifica el nombre de usuario con el modelo de IA.
    is_attack = classify_text_with_ai(username)

    if is_attack:
        print(f"🚨 Ataque SQL detectado en registro (username): '{username}'")
        now = datetime.datetime.utcnow()
        log_entry = LogAtaque(fecha=now.date(), hora=now.time(), timestamp_ataque=now)
        db.session.add(log_entry)
        db.session.commit()
        return "¡Intento de inyección SQL detectado en el nombre de usuario! Operación bloqueada.", 403
    
    if password != confirm_password:
        return "Las contraseñas no coinciden", 400

    # Verifica si el usuario o correo ya existen antes de registrar.
    if Usuario.query.filter((Usuario.username == username) | (Usuario.email == email)).first():
        return "El usuario o correo ya existe", 400

    # Hashea la contraseña y crea el nuevo usuario.
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    nuevo_usuario = Usuario(username=username, email=email, password=hashed_password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Redirige al índice después del registro exitoso.
    return redirect(url_for('index')) 

# Ruta de Inicio de Sesión (con detección de SQLi en 'email')
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    # Clasifica el email con el modelo de IA.
    is_attack = classify_text_with_ai(email)

    if is_attack:
        print(f"🚨 Ataque SQL detectado en login (email): '{email}'")
        now = datetime.datetime.utcnow()
        log_entry = LogAtaque(fecha=now.date(), hora=now.time(), timestamp_ataque=now)
        db.session.add(log_entry)
        db.session.commit()
        return "¡Intento de inyección SQL detectado en el email! Operación bloqueada.", 403

    # Busca al usuario y verifica la contraseña hasheada.
    user = Usuario.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return "Inicio de sesión exitoso" # En una aplicación real, aquí se gestionaría la sesión del usuario.
    else:
        return "Correo o contraseña incorrectos", 401

# Crea todas las tablas de la base de datos definidas en los modelos (Usuario, LogAtaque)
# Esto se ejecuta al inicio de la aplicación para asegurar que las tablas existan.
with app.app_context():
    db.create_all()
    print("✅ Todas las tablas de la base de datos verificadas/creadas (usuario, log_ataques).")

# --- Bloque de Ejecución Principal ---
if __name__ == '__main__':
    # Obtiene el puerto de la variable de entorno 'PORT' (común en plataformas de despliegue)
    # o usa 5000 por defecto para desarrollo local.
    port = int(os.environ.get("PORT", 5000)) 
    
    # Para despliegue en producción:
    # 1. Cambia 'debug=True' a 'debug=False'.
    # 2. Usa un servidor de producción como Gunicorn (recomendado).
    #    El comando de inicio en Render sería 'gunicorn app:app'
    #    (asegúrate de que gunicorn esté en tu requirements.txt).
    app.run(debug=True, host='0.0.0.0', port=port)