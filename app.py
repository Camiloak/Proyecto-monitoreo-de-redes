from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuración de la base de datos PostgreSQL (URL en variable de entorno)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://usuario:password@host:puerto/dbname')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'tu_clave_secreta_aqui'

db = SQLAlchemy(app)

# Modelo Usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Ruta principal
@app.route('/')
def index():
    return render_template('VulnerableWeb.html')

# Registro
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Verificar si usuario existe
    existing_user = Usuario.query.filter_by(username=username).first()
    if existing_user:
        return "El usuario ya existe", 400

    nuevo_usuario = Usuario(username=username, password=hashed_password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return redirect(url_for('index'))

# Inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = Usuario.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return "Inicio de sesión exitoso"
    else:
        return "Usuario o contraseña incorrectos", 401

if __name__ == '__main__':
    # Crear tablas en la base de datos (solo la primera vez)
    with app.app_context():
        db.create_all()

    app.run(debug=True)
