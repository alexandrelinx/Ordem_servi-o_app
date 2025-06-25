from app import create_app
from app.db import criar_tabela

criar_tabela()  # cria as tabelas antes de iniciar o app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
