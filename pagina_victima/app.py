from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'secreto'

# Conexión a MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Proyeto123@localhost/usuarios_db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Modelo
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Página principal
@app.route('/')
def index():
    return render_template('VulnerableWeb.html')

# Registro
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm_password']

    if password != confirm:
        return "Las contraseñas no coinciden"

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    nuevo_usuario = Usuario(username=username, email=email, password=hashed_password)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return "Registro exitoso"

# Inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and bcrypt.check_password_hash(usuario.password, password):
        return "Inicio de sesión exitoso"
    else:
        return "Credenciales incorrectas"

if __name__ == '__main__':
    app.run(debug=True)
