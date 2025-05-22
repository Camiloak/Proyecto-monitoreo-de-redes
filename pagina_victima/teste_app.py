import unittest
from app import app, db, Usuario

class AppTestCase(unittest.TestCase):
    # Se ejecuta antes de cada prueba
    def setUp(self):
        # Configuramos la app para modo testing
        app.config['TESTING'] = True
        # Usamos una base de datos en memoria para pruebas, sin afectar la real
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app
        # Cliente de prueba para hacer requests a la app
        self.client = app.test_client()

        # Crear las tablas en la base de datos de pruebas
        with self.app.app_context():
            db.create_all()

    # Se ejecuta después de cada prueba
    def tearDown(self):
        # Limpiamos la base de datos para que la siguiente prueba empiece limpia
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Prueba 1: Registro exitoso de un usuario nuevo
    def test_register_user_success(self):
        # Enviamos POST a /register con datos válidos
        response = self.client.post('/register', data={
            'username': 'user1',
            'password': 'password1'
        }, follow_redirects=True)

        # Comprobamos que la respuesta sea código 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verificamos que el usuario haya sido guardado en la BD
        with self.app.app_context():
            user = Usuario.query.filter_by(username='user1').first()
            self.assertIsNotNone(user)  # El usuario debe existir

    # Prueba 2: Registro con nombre de usuario ya existente (debe fallar)
    def test_register_user_duplicate(self):
        # Primero creamos un usuario para simular duplicado
        with self.app.app_context():
            user = Usuario(username='user2', password='fakehash')
            db.session.add(user)
            db.session.commit()

        # Intentamos registrar otro usuario con el mismo username
        response = self.client.post('/register', data={
            'username': 'user2',
            'password': 'password2'
        })

        # Debe devolver error 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Y el mensaje de error esperado
        self.assertIn('El usuario ya existe', response.data.decode('utf-8'))

    # Prueba 3: Inicio de sesión exitoso con usuario registrado
    def test_login_success(self):
        # Primero registramos el usuario
        self.client.post('/register', data={
            'username': 'user3',
            'password': 'password3'
        })

        # Intentamos iniciar sesión con las credenciales correctas
        response = self.client.post('/login', data={
            'username': 'user3',
            'password': 'password3'
        })

        # Comprobamos que la respuesta sea exitosa (código 200)
        self.assertEqual(response.status_code, 200)
        # Y que el mensaje de éxito esté en la respuesta
        self.assertIn('Inicio de sesión exitoso', response.data.decode('utf-8'))

    # Prueba 4: Inicio de sesión fallido por contraseña incorrecta
    def test_login_wrong_password(self):
        # Registramos un usuario
        self.client.post('/register', data={
            'username': 'user4',
            'password': 'correctpass'
        })

        # Intentamos iniciar sesión con contraseña incorrecta
        response = self.client.post('/login', data={
            'username': 'user4',
            'password': 'wrongpass'
        })

        # Debe devolver error 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)
        # Y el mensaje de error esperado
        self.assertIn('Usuario o contraseña incorrectos', response.data.decode('utf-8'))

    # Prueba 5: Inicio de sesión fallido por usuario no existente
    def test_login_nonexistent_user(self):
        # Intentamos iniciar sesión con un usuario que no existe
        response = self.client.post('/login', data={
            'username': 'nonexistent',
            'password': 'nopass'
        })

        # Debe devolver error 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)
        # Y el mensaje de error esperado
        self.assertIn('Usuario o contraseña incorrectos', response.data.decode('utf-8'))

# Ejecuta las pruebas si se ejecuta este archivo directamente
if __name__ == '__main__':
    unittest.main()
