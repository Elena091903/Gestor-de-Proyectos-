# auth_controller.py
# Controlador simple para autenticar usuarios contra la colección 'usuarios'.

from mongo_con import MongoConnection

class AuthController:
    def __init__(self, conn: MongoConnection = None):
        self.conn = conn or MongoConnection()
        self.usuarios = self.conn.get_collection('usuarios')

    def find_user(self, username: str):
        """Devuelve el documento del usuario o None si no existe."""
        return self.usuarios.find_one({'usuario': username})

    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        if not stored_password:
            return False
        if stored_password == provided_password:
            return True
        if stored_password.startswith('hash_simulado_'):
            suffix = stored_password.split('hash_simulado_', 1)[1]
            return suffix == provided_password
        return False

    def authenticate(self, username: str, password: str):
        """
        Intento de login. Retorna (ok: bool, user_doc or None, message: str).
        """
        user = self.find_user(username)
        if not user:
            return False, None, 'Usuario no encontrado.'
        if not user.get('activo', True):
            return False, None, 'Usuario inactivo. Contacta al administrador.'
        stored = user.get('contrasena')
        if not self.verify_password(stored, password):
            return False, None, 'Contraseña incorrecta.'
        # OK
        return True, user, 'Autenticado.'
