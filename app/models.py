from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import conectar

# class User(db.Model, UserMixin):
#     __tablename__ = 'usuario' 
#     id = db.Column(db.Integer, primary_key=True)
#     usuario = db.Column(db.String(150), unique=True, nullable=False)
#     senha_hash = db.Column(db.String(256), nullable=False)

#     def set_password(self, senha):
#         self.senha_hash = generate_password_hash(senha)

#     def check_password(self, senha):
#         return check_password_hash(self.senha_hash, senha)


class User(UserMixin):
    def __init__(self, id, usuario, senha_hash, perfil):
        self.id = id
        self.usuario = usuario
        self.senha_hash = senha_hash
        self.perfil = perfil

    class query:
        @staticmethod
        def filter_by(usuario):
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE usuario = ?", (usuario,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return User(row["id"], row["usuario"], row["senha_hash"], row["perfil"])
            return None

        @staticmethod
        def get(user_id):
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return User(row["id"], row["usuario"], row["senha_hash"], row["perfil"])
            return None
