import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# ✅ URL de PostgreSQL (Render)
POSTGRESQL_URL = "postgresql://usuarios_db_5qvs_user:Dqhqqj7Bha1hHLypk3QGHcZarlLbm4ON@dpg-d0l19bffte5s7394585g-a.oregon-postgres.render.com/usuarios_db_5qvs"

# Configuración de Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRESQL_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True

db = SQLAlchemy(app)

# Modelo de usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Pruebas unitarias
class PruebasUsuario(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            # 🔁 Eliminar usuarios de prueba por correo
            correos_prueba = [
                "test@correo.com",
                "noexiste@correo.com",
                "duplicado@correo.com"
            ]
            for correo in correos_prueba:
                usuario = Usuario.query.filter_by(email=correo).first()
                if usuario:
                    db.session.delete(usuario)
            db.session.commit()
            db.session.remove()

    # 🧪 Prueba 1: Crear un nuevo usuario
    def test_crear_usuario(self):
        with app.app_context():
            nuevo = Usuario(username="Test", email="test@correo.com", password="1234")
            db.session.add(nuevo)
            db.session.commit()
            usuario = Usuario.query.filter_by(email="test@correo.com").first()
            self.assertIsNotNone(usuario)
            self.assertEqual(usuario.username, "Test")

    # 🧪 Prueba 2: Buscar usuario existente
    def test_buscar_usuario(self):
        with app.app_context():
            usuario = Usuario(username="Test", email="test@correo.com", password="1234")
            db.session.add(usuario)
            db.session.commit()

            buscado = Usuario.query.filter_by(email="test@correo.com").first()
            self.assertIsNotNone(buscado)

    # 🧪 Prueba 3: Usuario inexistente
    def test_usuario_inexistente(self):
        with app.app_context():
            usuario = Usuario.query.filter_by(email="noexiste@correo.com").first()
            self.assertIsNone(usuario)

    # 🧪 Prueba 4: Evitar correo duplicado
    def test_usuario_duplicado(self):
        with app.app_context():
            original = Usuario(username="Test", email="test@correo.com", password="1234")
            db.session.add(original)
            db.session.commit()

            duplicado = Usuario(username="Repetido", email="test@correo.com", password="abcd")
            with self.assertRaises(Exception):
                db.session.add(duplicado)
                db.session.commit()

    # 🧪 Prueba 5: Eliminar usuario
    def test_eliminar_usuario(self):
        with app.app_context():
            usuario = Usuario(username="Test", email="test@correo.com", password="1234")
            db.session.add(usuario)
            db.session.commit()

            # Eliminar
            usuario = Usuario.query.filter_by(email="test@correo.com").first()
            db.session.delete(usuario)
            db.session.commit()

            usuario_borrado = Usuario.query.filter_by(email="test@correo.com").first()
            self.assertIsNone(usuario_borrado)

if __name__ == '__main__':
    unittest.main()
