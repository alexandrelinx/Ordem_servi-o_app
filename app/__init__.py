import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.db import criar_tabela  # função sqlite3 pura para tabela OS

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ordem_servico'

    # Caminho absoluto fixo para a pasta banco
    base_dir = os.path.abspath(os.path.dirname(__file__))

   # Caminho absoluto fixo para a pasta banco
   # banco_dir = r"C:\ForPoint\V3\ordem_servico_app\banco"

    banco_dir = os.path.join(base_dir, '..', 'banco')
    os.makedirs(banco_dir, exist_ok=True)  # cria a pasta banco se não existir

    db_path = os.path.join(banco_dir, 'solicitacoes.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

   
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app.models import User  # ← ADICIONE ESTA LINHA
        criar_tabela()  # cria tabela das OS no banco sqlite3 (se não existir)
        db.create_all()  # cria tabela dos usuários com SQLAlchemy (se não existir)

    from app.routes import main
    app.register_blueprint(main)

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

