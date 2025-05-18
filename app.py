import os
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuración usando variable de entorno DATABASE_URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://usuario:password@host:puerto/dbname'  # valor por defecto si no está la variable
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui')  # También en variable de entorno si quieres

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.before_first_request
def crear_tablas():
    db.create_all()

@app.route('/')
def index():
    if 'usuario' in session:
        return f"Hola, {session['usuario']}! <a href='/logout'>Cerrar sesión</a>"
    return render_template('VulnerableWeb.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash('Las contraseñas no coinciden.', 'error')
        return redirect(url_for('index'))

    existing_user = Usuario.query.filter(
        (Usuario.username == username) | (Usuario.email == email)
    ).first()

    if existing_user:
        flash('El usuario o email ya existe.', 'error')
        return redirect(url_for('index'))

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    nuevo_usuario = Usuario(username=username, email=email, password=hashed_password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username_or_email = request.form['email']
    password = request.form['password']

    user = Usuario.query.filter(
        (Usuario.username == username_or_email) | (Usuario.email == username_or_email)
    ).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session['usuario'] = user.username
        flash('Inicio de sesión exitoso.', 'success')
        return redirect(url_for('index'))
    else:
        flash('Usuario o contraseña incorrectos.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
