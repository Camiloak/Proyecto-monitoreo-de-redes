import unittest
from app import create_app, db, Usuario

class UsuarioTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test_config=True)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_crear_usuario(self):
        with self.app.app_context():
            nuevo = Usuario(username="Test1", email="test1@example.com", password="123")
            db.session.add(nuevo)
            db.session.commit()
            self.assertIsNotNone(Usuario.query.filter_by(email="test1@example.com").first())

    def test_usuario_existente(self):
        with self.app.app_context():
            usuario1 = Usuario(username="User1", email="dup@example.com", password="abc")
            db.session.add(usuario1)
            db.session.commit()

            usuario2 = Usuario(username="User2", email="dup@example.com", password="xyz")
            db.session.add(usuario2)

            with self.assertRaises(Exception):
                db.session.commit()

    def test_login_correcto(self):
        with self.app.app_context():
            usuario = Usuario(username="LoginUser", email="login@example.com", password="pass")
            db.session.add(usuario)
            db.session.commit()

            encontrado = Usuario.query.filter_by(email="login@example.com", password="pass").first()
            self.assertIsNotNone(encontrado)
            self.assertEqual(encontrado.username, "LoginUser")

    def test_login_fallido(self):
        with self.app.app_context():
            usuario = Usuario(username="Fallido", email="fail@example.com", password="123")
            db.session.add(usuario)
            db.session.commit()

            encontrado = Usuario.query.filter_by(email="fail@example.com", password="wrong").first()
            self.assertIsNone(encontrado)

    def test_eliminar_usuario(self):
        with self.app.app_context():
            usuario = Usuario(username="Eliminar", email="delete@example.com", password="321")
            db.session.add(usuario)
            db.session.commit()

            db.session.delete(usuario)
            db.session.commit()

            eliminado = Usuario.query.filter_by(email="delete@example.com").first()
            self.assertIsNone(eliminado)

if __name__ == '__main__':
    unittest.main()
