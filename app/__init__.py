import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.db import criar_tabela  # função sqlite3 pura para tabela OS
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ordem_servico'

    # Caminho para banco
    base_dir = os.path.abspath(os.path.dirname(__file__))
    banco_dir = os.path.join(base_dir, '..', 'banco')
    os.makedirs(banco_dir, exist_ok=True)
    db_path = os.path.join(banco_dir, 'solicitacoes.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configurações do e-mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'alexandremos@gmail.com'
    app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD')
 
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from app.models import User  # importa modelo User
        criar_tabela()              # cria tabela das OS (sqlite3 pura)
        db.create_all()             # cria tabelas SQLAlchemy (ex: User)

    from app.routes import main
    app.register_blueprint(main)

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
