from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app.db import (
    criar_tabela, obter_os, inserir_os, carregar_nomes_clientes,
    carregar_nomes_solicitantes, carregar_nomes_equipamentos,
    carregar_nomes_setores, carregar_status_atendimentos,
    obter_os_por_id, atualizar_os, excluir_os, somar_valores, obter_relatorio_os_por_cliente_com_totais, obter_relatorio_os_por_cliente 
)
from app.relatorios.relatorio import gerar_relatorio_pdf
from io import BytesIO
from datetime import datetime
from collections import defaultdict
from datetime import datetime
from app import db
from flask import Flask,send_file, abort, Blueprint, render_template, request, redirect, url_for, flash, send_file, Response,  make_response
from app.relatorios.pdf_report import gerar_relatorio_os_por_cliente_pdf
from werkzeug.security import generate_password_hash ,check_password_hash
from app.models import User
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask import flash, redirect, url_for
from app import login_manager 
from flask import session
from flask_login import current_user
from flask_login import current_user, login_required
from flask_login import LoginManager
main = Blueprint('main', __name__)


@main.route('/')
def raiz():
    # Redireciona para /login
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario').strip().lower()
        senha = request.form.get('senha')
        user = User.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.senha_hash, senha):  # ou user.check_password(senha) se tiver método no model
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            print("Usuário encontrado:", user.usuario)
            print("Senha correta?", check_password_hash(user.senha_hash, senha))
            return redirect(url_for('main.dashboard_completo'))
        else:
            flash('Credenciais inválidas.', 'danger')
            print("Usuário não encontrado:", usuario)
    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('main.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    return f"Olá, {current_user.usuario}! Você está logado." 


# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ordem_servico'

    from .routes import main
    app.register_blueprint(main)

    from app.db import criar_tabela

    @app.before_first_request
    def inicializar_banco():
        criar_tabela()

    return app

@main.route('/')
def dashboard_completo():
   
    ordens = obter_os()
    print(ordens)
    total_valor = somar_valores()
    usuario = current_user.usuario if current_user.is_authenticated else None
    return render_template('dashboard.html', ordens=ordens, total=total_valor,usuario=usuario)

#login_manager = LoginManager()
#login_manager.login_view = 'main.login'  # ou o nome correto da rota
#login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/nova-os', methods=['GET', 'POST'])
def nova_os():
    if request.method == 'POST':
        dados = {
            "cliente": request.form.get('cliente'),
            "solicitante": request.form.get('solicitante'),
            "equipamento": request.form.get('equipamento'),
            "setor": request.form.get('setor'),
            "status": request.form.get('status'),
            "data_solicitacao": request.form.get('data_solicitacao'),
            "hora_solicitacao": request.form.get('hora_solicitacao'),
            "problema": request.form.get('problema'),
            "analise_problema": request.form.get('analise_problema'),
            "solucao": request.form.get('solucao'),
            "valor_servico": float(request.form.get('valor_servico') or 0),
            "data_conclusao": request.form.get('data_conclusao'),
            "hora_conclusao": request.form.get('hora_conclusao'),
        }
        inserir_os(dados)
        flash("Ordem de Serviço criada com sucesso!", "success")
        return redirect(url_for('main.dashboard'))

    clientes = carregar_nomes_clientes()
    solicitantes = carregar_nomes_solicitantes()
    equipamentos = carregar_nomes_equipamentos()
    setores = carregar_nomes_setores()
    status_list = carregar_status_atendimentos()

    return render_template('nova_os.html',
                           clientes=clientes,
                           solicitantes=solicitantes,
                           equipamentos=equipamentos,
                           setores=setores,
                           status_list=status_list)



def format_date_br_para_html(data_br):
    try:
        return datetime.strptime(data_br, "%d/%m/%Y").strftime("%Y-%m-%d")
    except Exception:
        return ''

def format_time_br_para_html(hora_br):
    try:
        return datetime.strptime(hora_br, "%H:%M:%S").strftime("%H:%M")
    except Exception:
        try:
            return datetime.strptime(hora_br, "%H:%M").strftime("%H:%M")
        except Exception:
            return ''

def format_date_html_para_br(data_html):
    try:
        return datetime.strptime(data_html, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return ''

def format_time_html_para_br(hora_html):
    try:
        # Recebe HH:MM, adiciona :00 para segundos
        return datetime.strptime(hora_html, "%H:%M").strftime("%H:%M:%S")
    except Exception:
        return ''



@main.route('/alterar-os/<int:os_id>', methods=['GET', 'POST'])
def alterar_os(os_id):
    os_registro = obter_os_por_id(os_id)
    if not os_registro:
        flash("Ordem de Serviço não encontrada.", "danger")
        return redirect(url_for('main.consultar_os'))

    if request.method == 'POST':
        dados = {
            "cliente": request.form.get('cliente'),
            "solicitante": request.form.get('solicitante'),
            "equipamento": request.form.get('equipamento'),
            "setor": request.form.get('setor'),
            "status": request.form.get('status'),
            "data_solicitacao": format_date_html_para_br(request.form.get('data_solicitacao')),
            "hora_solicitacao": format_time_html_para_br(request.form.get('hora_solicitacao')),
            "problema": request.form.get('problema'),
            "analise_problema": request.form.get('analise_problema'),
            "solucao": request.form.get('solucao'),
            "valor_servico": float(request.form.get('valor_servico') or 0),
             "data_conclusao": format_date_html_para_br(request.form.get('data_conclusao')),
            "hora_conclusao": format_time_html_para_br(request.form.get('hora_conclusao')),
        }
        atualizar_os(os_id, dados)
        flash("Ordem de Serviço atualizada com sucesso!", "success")
        return redirect(url_for('main.consultar_os'))

# converte data e hora do formato dd/mm/yyyy e HH:MM:SS para o formato HTML esperado
    os_registro['data_solicitacao'] = format_date_br_para_html(os_registro.get('data_solicitacao'))
    os_registro['data_conclusao'] = format_date_br_para_html(os_registro.get('data_conclusao'))
    os_registro['hora_solicitacao'] = format_time_br_para_html(os_registro.get('hora_solicitacao'))
    os_registro['hora_conclusao'] = format_time_br_para_html(os_registro.get('hora_conclusao'))


    clientes = carregar_nomes_clientes()
    solicitantes = carregar_nomes_solicitantes()
    equipamentos = carregar_nomes_equipamentos()
    setores = carregar_nomes_setores()
    status_list = carregar_status_atendimentos()

    return render_template('alterar_os.html',
                           os_registro=os_registro,
                           clientes=clientes,
                           solicitantes=solicitantes,
                           equipamentos=equipamentos,
                           setores=setores,
                           status_list=status_list)

@main.route('/excluir-os/<int:os_id>', methods=['GET'])
def excluir_os_route(os_id):
    excluir_os(os_id)
    flash("Ordem de Serviço excluída com sucesso!", "success")
    return redirect(url_for('main.consultar_os'))

@main.route('/relatorio/<int:os_id>')
def relatorio_os(os_id):
    os_registro = obter_os_por_id(os_id)
    if not os_registro:
        flash("Ordem de Serviço não encontrada para gerar relatório.", "danger")
        return redirect(url_for('main.consultar_os'))

    buffer = gerar_relatorio_pdf(os_registro)
    return send_file(buffer,
                     as_attachment=True,
                     download_name=f'OS_{os_id}.pdf',
                     mimetype='application/pdf')

@main.route('/consultar-os')
def consultar_os():
    cliente = request.args.get('cliente')
    status = request.args.get('status')

    ordens = obter_os(cliente=cliente, status=status)
    total_valor = somar_valores()

    return render_template('consultar_os.html', ordens=ordens, total=total_valor,
                           cliente=cliente, status=status)



@main.route('/relatorio-os-cliente')
def relatorio_os_cliente():
    cliente_selecionado = request.args.get('cliente', '').strip()

    # Supondo que 'db' seja seu módulo de acesso ao banco com essa função
    dados, totais =obter_relatorio_os_por_cliente_com_totais()


        # Cálculo do total geral de todos os meses de todos os clientes
    total_geral = sum(
        sum(mes_valores.values()) for mes_valores in totais.values()
    )

    if cliente_selecionado:
        dados = {cliente_selecionado: dados.get(cliente_selecionado, {})}
        totais = {cliente_selecionado: totais.get(cliente_selecionado, {})}
    else:
        # Se nenhum cliente foi selecionado, traz todos os clientes (dados e totais completos)
        # Não faz nada, mantém os dados originais completos

        # Só pra garantir, cliente_selecionado fica vazio para o template saber que é "todos"
        cliente_selecionado = ''
    clientes = carregar_nomes_clientes()

    return render_template('relatorio_os_cliente.html',
                           dados=dados,
                           totais=totais,
                           clientes=clientes,
                           cliente_selecionado=cliente_selecionado,
                           total_geral=total_geral )




@main.route('/relatorio-os-cliente/pdf')
def relatorio_os_cliente_pdf():
    cliente_selecionado = request.args.get('cliente', '').strip()
    dados, totais = obter_relatorio_os_por_cliente_com_totais()

    if cliente_selecionado:
        dados = {cliente_selecionado: dados.get(cliente_selecionado, {})}
        totais = {cliente_selecionado: totais.get(cliente_selecionado, {})}

    buffer = gerar_relatorio_os_por_cliente_pdf (dados, totais)

    return send_file(buffer,
                     as_attachment=True,
                     download_name='relatorio_os_cliente.pdf',
                     mimetype='application/pdf')






#Rotas para login e logout

# # @main.route('/cadastro/usuarios', methods=['GET', 'POST'])
# # def cadastro_usuario():
    
# #     if request.method == 'POST':
# #         usuario = request.form.get('usuario', '').strip()
# #         senha = request.form.get('senha', '').strip()

# #         if not usuario or not senha:
# #             flash("Usuário e senha são obrigatórios.", "warning")
# #             return redirect(request.url)

# #         senha_hash = generate_password_hash(senha)

# #         conn = get_db_connection()

# #         existente = conn.execute("SELECT 1 FROM usuario WHERE usuario = ?", (usuario,)).fetchone()
# #         if existente:
# #             flash("Usuário já existe.", "danger")
# #             conn.close()
# #             return redirect(request.url)

# #         conn.execute("INSERT INTO usuario (usuario, senha_hash) VALUES (?, ?)", (usuario, senha_hash))
# #         conn.commit()
# #         conn.close()

# #         flash("Usuário cadastrado com sucesso!", "success")
# #         return redirect(url_for('login'))  # ou outra página
# #     print("Renderizando cadastro_usuario.html")
# #     return render_template('cadastro_usuario.html')

# # @main.route('/usuarios')
# # def consultar_usuario():
# #     conn = get_db_connection()
# #     usuarios = conn.execute("SELECT id, usuario FROM usuario ORDER BY usuario ASC").fetchall()
# #     conn.close()
# #     return render_template('consultar_usuarios.html', usuarios=usuarios)

# # @main.route('/usuarios', methods=['GET'])
# # def listar_usuarios():
# #     conn = get_db_connection()
# #     usuarios = conn.execute("SELECT id, usuario FROM usuario ORDER BY usuario ASC").fetchall()
# #     conn.close()
# #     return render_template('listar_usuarios.html', usuarios=usuarios)

# # @main.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
# # def editar_usuario(id):
# #     conn = get_db_connection()

# #     if request.method == 'POST':
# #         usuario = request.form.get('usuario', '').strip()
# #         senha = request.form.get('senha', '').strip()

# #         if not usuario:
# #             flash("O nome de usuário é obrigatório.", "warning")
# #             return redirect(request.url)

# #         # Atualiza com ou sem nova senha
# #         if senha:
# #             senha_hash = generate_password_hash(senha)
# #             conn.execute(
# #                 "UPDATE usuario SET usuario = ?, senha_hash = ? WHERE id = ?",
# #                 (usuario, senha_hash, id)
# #             )
# #         else:
# #             conn.execute(
# #                 "UPDATE usuario SET usuario = ? WHERE id = ?",
# #                 (usuario, id)
# #             )

# #         conn.commit()
# #         conn.close()
# #         flash("Usuário atualizado com sucesso!", "success")
# #         return redirect(url_for('listar_usuarios'))

# #     # GET: carregar dados do usuário
# #     usuario = conn.execute("SELECT * FROM usuario WHERE id = ?", (id,)).fetchone()
# #     conn.close()

# #     if usuario is None:
# #         flash("Usuário não encontrado.", "danger")
# #         return redirect(url_for('listar_usuarios'))

# #     return render_template('editar_usuario.html', usuario=usuario)

# # @main.route('/usuarios/excluir/<int:id>', methods=['POST'])
# # def excluir_usuario(id):
# #     conn = get_db_connection()
# #     conn.execute("DELETE FROM usuario WHERE id = ?", (id,))
# #     conn.commit()
# #     conn.close()
# #     flash("Usuário excluído com sucesso!", "success")
# #     return redirect(url_for('listar_usuarios'))
