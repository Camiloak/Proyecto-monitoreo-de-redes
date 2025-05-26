from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Detectar entorno: Render usa DATABASE_URL; en local usamos SQLite
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Asegurarse de que sea compatible con psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
else:
    # Base de datos en memoria para pruebas o desarrollo local
    database_url = 'sqlite:///local.db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta_segura'

db = SQLAlchemy(app)

# Modelo Usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    return render_template('VulnerableWeb.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    existing_user = Usuario.query.filter_by(username=username).first()
    if existing_user:
        return "El usuario ya existe", 400

    nuevo_usuario = Usuario(username=username, password=hashed_password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = Usuario.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return "Inicio de sesión exitoso"
    else:
        return "Usuario o contraseña incorrectos", 401

# Crear las tablas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
