from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuración directa para PostgreSQL sin usar .env
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@servidor:puerto/nombre_basedatos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta_segura'

db = SQLAlchemy(app)

# Modelo de Usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Ruta principal
@app.route('/')
def index():
    return render_template('VulnerableWeb.html')

# Registro
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return "Las contraseñas no coinciden", 400

    if Usuario.query.filter((Usuario.username == username) | (Usuario.email == email)).first():
        return "El usuario o correo ya existe", 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    nuevo_usuario = Usuario(username=username, email=email, password=hashed_password)

    db.session.add(nuevo_usuario)
    db.session.commit()

    return redirect(url_for('index'))

# Inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = Usuario.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return "Inicio de sesión exitoso"
    else:
        return "Usuario o contraseña incorrectos", 401

# Crear las tablas si no existen
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Tablas creadas o ya existentes en la base de datos.")

    app.run(debug=True)
