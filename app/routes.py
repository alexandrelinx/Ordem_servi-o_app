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
from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask import flash, redirect, url_for
from app import login_manager 
from flask import session
from flask_login import current_user
from flask_login import current_user, login_required
from flask_login import LoginManager
import os
from flask import send_from_directory, current_app
from app.db import conectar
from functools import wraps
from flask import Blueprint, redirect, url_for, flash
from flask import request, flash, redirect, url_for, render_template
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from flask_mail import Message
from app import mail 
from dotenv import load_dotenv # ajuste para seu modelo User
from datetime import datetime
import pytz
from datetime import datetime, timezone
from app.util.timezone import agora_brasilia
from twilio.base.exceptions import TwilioRestException
from flask import Blueprint, render_template, request, redirect, url_for, flash
from twilio.rest import Client






load_dotenv()  # carrega as variáveis do .env para o ambiente

main = Blueprint('main', __name__)



@main.route('/imagens/<path:filename>')
def imagens(filename):
    diretorio_imagens = os.path.join(current_app.root_path, 'imagens')
    return send_from_directory(diretorio_imagens, filename)


@main.route('/')
def raiz():
    # Redireciona para /login
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        if not usuario or not senha:
            flash('Por favor, preencha usuário e senha.', 'warning')
            return render_template('login.html')

        usuario = usuario.strip().lower()
        user = User.query.filter_by(usuario=usuario)  # já retorna User ou None

        if user and check_password_hash(user.senha_hash, senha):
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('main.dashboard_completo'))
        else:
            flash('Credenciais inválidas.', 'danger')
            print("Usuário não encontrado ou senha incorreta:", usuario)

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('main.login'))


@main.route('/trocar_usuario/<int:user_id>')
@login_required
def trocar_usuario(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('main.dashboard_completo'))

    logout_user()
    # Redireciona para login, pode passar o user_id para pré-preencher se quiser
    return redirect(url_for('main.login', user_id=user_id))
#Rotas para login e logout

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.perfil != 'admin':
            flash('Acesso negado: apenas administradores.', 'danger')
            return redirect(url_for('main.dashboard_completo'))
        return f(*args, **kwargs)
    return decorated_function



@main.route('/cadastro/usuarios', methods=['GET', 'POST'])
@admin_required

def cadastro_usuario():
   

    if request.method == 'POST':
        perfil = request.form['perfil'] 
        usuario = request.form['usuario']
        senha = request.form['senha']

        
        if perfil not in ['admin', 'usuario']:
           flash('Perfil inválido.', 'danger')
           return redirect(request.url)

        senha_hash = generate_password_hash(senha)

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuario (usuario, senha_hash, perfil) VALUES (?, ?, ?)", (usuario, senha_hash, perfil))
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')
        finally:
            conn.close()
    return render_template('cadastro_usuario.html')

@main.route('/usuarios/cadastro', methods=['GET', 'POST'])
@admin_required
def cadastro_usuario_menu():

    if request.method == 'POST':
        perfil = request.form['perfil'] 
        usuario = request.form['usuario']
        senha = request.form['senha']

           
        if perfil not in ['admin', 'usuario']:
          flash('Perfil inválido.', 'danger')
          return redirect(request.url)

        senha_hash = generate_password_hash(senha)

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuario (usuario, senha_hash, perfil) VALUES (?, ?, ?)", (usuario, senha_hash, perfil))
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('main.listar_usuarios'))
        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')
        finally:
            conn.close()

    return render_template('cadastro_usuario_menu.html')  # Template diferente, baseado em 'base.html'

@main.route('/usuarios')
@admin_required
def consultar_usuario():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, usuario , perfil FROM usuario ORDER BY usuario ASC")
        usuarios = cursor.fetchall()
    finally:
        conn.close()
    return render_template('consultar_usuarios.html', usuarios=usuarios)

@main.route('/usuarios/listar')
def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, usuario , perfil FROM usuario ORDER BY usuario ASC")
        usuarios_raw = cursor.fetchall()
        # Transformar em lista de dicionários para facilitar o uso no template
        usuarios = []
        for row in usuarios_raw:
            usuarios.append({
                'id': row[0],
                'usuario': row[1],
                'perfil': row[2]
            })
    finally:
        conn.close()
    return render_template('listar_usuarios.html', usuarios=usuarios)


@main.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
      
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()
        perfil = request.form.get('perfil', '').strip()

        if not usuario:
            flash("O nome de usuário é obrigatório.", "warning")
            return redirect(request.url)

        try:
            if senha:
                senha_hash = generate_password_hash(senha)
                cursor.execute(
                    "UPDATE usuario SET usuario = ?, senha_hash = ?, perfil = ? WHERE id = ?",
                    (usuario, senha_hash, perfil, id)
                )
            else:
                cursor.execute(
                    "UPDATE usuario SET usuario = ?, perfil = ? WHERE id = ?",
                    (usuario, perfil, id)
                )
            conn.commit()
            flash("Usuário atualizado com sucesso!", "success")
            return redirect(url_for('main.listar_usuarios'))
        except Exception as e:
            flash(f"Erro ao atualizar usuário: {e}", "danger")
        finally:
            conn.close()

    # GET: carregar dados do usuário
    try:
        cursor.execute("SELECT * FROM usuario WHERE id = ?", (id,))
        usuario = cursor.fetchone()
    finally:
        conn.close()

    if usuario is None:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for('main.listar_usuarios'))

    return render_template('editar_usuario.html', usuario=usuario)

@main.route('/usuarios/excluir/<int:id>', methods=['POST'])
@admin_required
def excluir_usuario(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM usuario WHERE id = ?", (id,))
        conn.commit()
        flash("Usuário excluído com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao excluir usuário: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('main.listar_usuarios'))




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

@main.route('/dashboard_completo')
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

from twilio.rest import Client


def enviar_sms(mensagem, celular_destino):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=mensagem,
        from_='+13133950184',  # Seu número Twilio
        to=celular_destino      # Exemplo: '+5599999999999'
    )
    print(f'SMS enviado, SID: {message.sid}')

from datetime import datetime

@main.route('/nova-os', methods=['GET', 'POST'])
def nova_os():
    if request.method == 'POST':

  # A data e hora vêm do form, no formato ISO, tipo: '2025-07-09' e '14:30'
        data_solicitacao_raw = request.form.get('data_solicitacao')  # 'YYYY-MM-DD'
        hora_solicitacao_raw = request.form.get('hora_solicitacao')  # 'HH:MM'

        # Converte para dd/mm/yyyy e HH:MM:SS para salvar no formato desejado
        data_solicitacao = datetime.strptime(data_solicitacao_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        hora_solicitacao = hora_solicitacao_raw + ':00'  # adiciona segundos para ficar HH:MM:SS


        dados = {
            "cliente": request.form.get('cliente'),
            "solicitante": request.form.get('solicitante'),
            "equipamento": request.form.get('equipamento'),
            "setor": request.form.get('setor'),
            "status": request.form.get('status'),
            "data_solicitacao": data_solicitacao,
            "hora_solicitacao": hora_solicitacao, 
            "problema": request.form.get('problema'),
            "analise_problema": request.form.get('analise_problema'),
            "solucao": request.form.get('solucao'),
            "valor_servico": float(request.form.get('valor_servico') or 0),
            "data_conclusao": format_date_html_para_br(request.form.get('data_conclusao')),
            "hora_conclusao": format_date_html_para_br(request.form.get('hora_conclusao')),
        }
        inserir_os(dados)



        # Enviar email
        try:
            
            enviar_email(
                destino="alexandremos@gmail.com",
                assunto="Nova Ordem de Serviço Criada",
                mensagem=f"Uma nova OS foi criada para o cliente {dados['cliente']} com status {dados['status']}."
            )

        except Exception as e:
            print(f"Erro ao enviar email: {e}")

        # Enviar SMS (comente se não quiser enviar SMS)
        try:
            enviar_sms(
                mensagem=f"Nova OS criada para {dados['cliente']} com status {dados['status']}.",
                celular_destino='+5581985879259'  # seu número celular no formato internacional
            )
        except Exception as e:
            print(f"Erro ao enviar SMS: {e}")

        flash("Ordem de Serviço criada com sucesso!", "success")
        return redirect(url_for('main.dashboard_completo'))
    
       # Para GET, gera data e hora atuais:
    brasilia = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(timezone.utc).astimezone(brasilia)
    data_atual = agora.strftime('%Y-%m-%d')    # formato para input type=date
    hora_atual = agora.strftime('%H:%M')  

    
   
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
                           status_list=status_list,
                           data_atual=data_atual,
                           hora_atual=hora_atual)

# Funções para enviar email e SMS (exemplos simples)
def enviar_email(destino, assunto, mensagem):
    remetente = "alexandremos@gmail.com"
    senha = os.getenv('GMAIL_APP_PASSWORD')
   

    msg = MIMEText(mensagem)
    msg['Subject'] = assunto
    msg['From'] = remetente
    msg['To'] = destino

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(remetente, senha)
        smtp.send_message(msg)



def enviar_sms(mensagem, celular_destino):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    if not account_sid or not auth_token:
        print("⚠️ TWILIO_ACCOUNT_SID ou TWILIO_AUTH_TOKEN não configurados. SMS não enviado.")
        return False

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=mensagem,
            from_='+13133950184',  # Seu número Twilio
            to=celular_destino
        )
        print("✅ SMS enviado com sucesso. SID:", message.sid)
        return True

    except TwilioRestException as e:
        print(f"❌ Erro do Twilio ao enviar SMS: {e}")
        return False

    except Exception as e:
        print(f"❌ Erro inesperado ao enviar SMS: {e}")
        return False


def format_date_br_para_html(data_br):
    try:
        return datetime.strptime(data_br, "%Y-%m-%d").strftime("%d/%m/%Y")
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
        return datetime.strptime(hora_html, "%H:%M:%S").strftime("%H:%M")
    except Exception:
        return ''


@main.route('/alterar-os/<int:os_id>', methods=['GET', 'POST'])
@admin_required
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


    os_registro['data_solicitacao'] = datetime.strptime(
        os_registro.get('data_solicitacao'), '%d/%m/%Y'
    ).strftime('%Y-%m-%d') if os_registro.get('data_solicitacao') else ''

    os_registro['data_conclusao'] = datetime.strptime(
        os_registro.get('data_conclusao'), '%d/%m/%Y'
    ).strftime('%Y-%m-%d') if os_registro.get('data_conclusao') else ''

    # Já para hora, converte para HH:MM (para input type="time")
    os_registro['hora_solicitacao'] = os_registro.get('hora_solicitacao')[:5] if os_registro.get('hora_solicitacao') else ''
    os_registro['hora_conclusao'] = os_registro.get('hora_conclusao')[:5] if os_registro.get('hora_conclusao') else ''




# converte data e hora do formato dd/mm/yyyy e HH:MM:SS para o formato HTML esperado
   # os_registro['data_solicitacao'] = format_date_br_para_html(os_registro.get('data_solicitacao'))
   # os_registro['data_conclusao'] = format_date_br_para_html(os_registro.get('data_conclusao'))
   # os_registro['hora_solicitacao'] = format_time_br_para_html(os_registro.get('hora_solicitacao'))
   # os_registro['hora_conclusao'] = format_time_br_para_html(os_registro.get('hora_conclusao'))


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
@admin_required
def excluir_os_route(os_id):
    excluir_os(os_id)
    flash("Ordem de Serviço excluída com sucesso!", "success")
    return redirect(url_for('main.consultar_os'))


@main.route('/consultar-os')
@login_required
def consultar_os():
    cliente = request.args.get('cliente')
    status = request.args.get('status')
    perfil_usuario = current_user.perfil 
    ordens = obter_os(cliente=cliente, status=status)
    total_valor = somar_valores()

    return render_template('consultar_os.html', ordens=ordens, total=total_valor,
                           cliente=cliente, status=status, perfil_usuario=perfil_usuario )


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




# Função auxiliar genérica
def executar_query(query, params=(), fetch=False):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        rows = cursor.fetchall()
        conn.close()
        return rows
    conn.commit()
    conn.close()

# ------------------ CLIENTES ------------------

@main.route('/clientes')
def listar_clientes():
    clientes = executar_query("SELECT * FROM clientes ORDER BY nome", fetch=True)
    return render_template('consultar_cliente.html', clientes=clientes)

@main.route('/parametros/clientes')
def consultar_clientes():
    clientes = executar_query("SELECT * FROM clientes ORDER BY nome", fetch=True)
    return render_template('consultar_cliente.html', clientes=clientes)


@main.route('/parametros/clientes/novo', methods=['GET', 'POST'])
def novo_cliente():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip().upper()

        if nome:
            try:
                executar_query("INSERT INTO clientes (nome) VALUES (?)", (nome,))
                flash('Cliente adicionado com sucesso!', 'success')
            except:
                flash('Erro: cliente já existe ou problema no cadastro.', 'danger')

        return redirect(url_for('main.listar_clientes'))

    return render_template('editar_cliente.html', cliente=None, tipo='cliente')


@main.route('/parametros/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip().upper()
        if nome:
            executar_query("UPDATE clientes SET nome = ? WHERE id = ?", (nome, id))
            flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('main.listar_clientes'))
    else:
        cliente = executar_query("SELECT * FROM clientes WHERE id = ?", (id,), fetch=True)
        if cliente:
            return render_template('editar_cliente.html', registro=cliente[0], tipo='cliente')
        else:
            flash('Cliente não encontrado.', 'danger')
            return redirect(url_for('main.listar_clientes'))


@main.route('/parametros/clientes/excluir/<int:id>')
def excluir_cliente(id):
    executar_query("DELETE FROM clientes WHERE id = ?", (id,))
    flash('Cliente excluído com sucesso!', 'warning')
    return redirect(url_for('main.listar_clientes'))


# ------------------ SOLICITANTES ------------------

@main.route('/solicitantes')
def listar_solicitantes():
    solicitantes = executar_query("SELECT * FROM solicitantes ORDER BY nome", fetch=True)
    return render_template('consultar_solicitantes.html', solicitantes=solicitantes)



@main.route('/parametros/solicitantes')
def consultar_solicitantes():
    solicitantes = executar_query("SELECT * FROM solicitantes ORDER BY nome", fetch=True)
    return render_template('consultar_solicitantes.html', solicitantes=solicitantes)


@main.route('/parametros/solicitantes/novo', methods=['GET', 'POST'])
def novo_solicitantes():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip().upper()
    
        if nome:
            try:
              executar_query("INSERT INTO solicitantes (nome) VALUES (?)", (nome,))
              flash('Solicitante adicionado com sucesso!', 'success')
            except:
             flash('Erro: Solicitante já existe ou problema no cadastro.', 'danger')
        return redirect(url_for('main.listar_solicitantes'))

    return render_template('editar_solicitantes.html', solicitantes=None, tipo='solicitantes')

@main.route('/parametros/solicitantes/editar/<int:id>',  methods=['GET', 'POST'])
def editar_solicitantes(id):
    if request.method == 'POST':
       nome = request.form.get('nome', '').strip().upper()
       if nome:
         executar_query("UPDATE solicitantes SET nome = ? WHERE id = ?", (nome, id))
         flash('solicitantes atualizado com sucesso!', 'success')
       return redirect(url_for('main.listar_solicitantes'))
    else:
        solicitantes = executar_query("SELECT * FROM solicitantes WHERE id = ?", (id,), fetch=True)
        if solicitantes:
            return render_template('editar_solicitantes.html', registro=solicitantes[0], tipo='solicitantes')
        else:
            flash('Solicitante não encontrado.', 'danger')
            return redirect(url_for('main.listar_solicitantes'))



@main.route('/parametros/solicitantes/excluir/<int:id>')
def excluir_solicitantes(id):
    executar_query("DELETE FROM solicitantes WHERE id = ?", (id,))
    flash('Solicitante excluído com sucesso!', 'warning')
    return redirect(url_for('main.listar_solicitantes'))


# ------------------ EQUIPAMENTOS ------------------

@main.route('/equipamentos')
def listar_equipamentos():
    equipamentos = executar_query("SELECT * FROM equipamentos ORDER BY nome", fetch=True)
    return render_template('consultar_equipamentos.html', equipamentos=equipamentos)

@main.route('/parametros/equipamentos')
def consultar_equipamentos():
    equipamentos = executar_query("SELECT * FROM equipamentos ORDER BY nome", fetch=True)
    return render_template('consultar_equipamentos.html', equipamentos=equipamentos)

@main.route('/parametros/equipamentos/novo',  methods=['GET', 'POST'])
def novo_equipamentos():
    if request.method == 'POST':
      nome = request.form.get('nome', '').strip().upper()

      if nome:
         try:
            executar_query("INSERT INTO equipamentos (nome) VALUES (?)", (nome,))
            flash('Equipamento adicionado com sucesso!', 'success')
         except:
            flash('Erro: Equipamento já existe ou problema no cadastro.', 'danger')
   
      return redirect(url_for('main.listar_equipamentos'))

    return render_template('editar_equipamentos.html', equipamentos=None, tipo='equipamento')

@main.route('/parametros/equipamentos/editar/<int:id>',methods=['GET', 'POST'])
def editar_equipamentos(id):
    if request.method == 'POST':
      nome = request.form.get('nome', '').strip().upper()
      if nome:
        executar_query("UPDATE equipamentos SET nome = ? WHERE id = ?", (nome, id))
        flash('Equipamento atualizado com sucesso!', 'success')
      return redirect(url_for('main.listar_equipamentos'))
    else:
        equipamentos = executar_query("SELECT * FROM equipamentos WHERE id = ?", (id,), fetch=True)
        if equipamentos:
            return render_template('editar_equipamentos.html', registro=equipamentos[0], tipo='equipamento')
        else:
            flash('Equipamento não encontrado.', 'danger')
            return redirect(url_for('main.listar_equipamentos'))

@main.route('/parametros/equipamentos/excluir/<int:id>')
def excluir_equipamentos(id):
    executar_query("DELETE FROM equipamentos WHERE id = ?", (id,))
    flash('equipamentos excluído com sucesso!', 'warning')
    return redirect(url_for('main.listar_equipamentos'))


# ------------------ SETORES ------------------

@main.route('/setores')
def listar_setores():
    setores = executar_query("SELECT * FROM setores ORDER BY nome", fetch=True)
    return render_template('consultar_setores.html', setores=setores)

@main.route('/parametros/setores')
def consultar_setores():
    setores = executar_query("SELECT * FROM setores ORDER BY nome", fetch=True)
    return render_template('consultar_setores.html', setores=setores)

@main.route('/parametros/setores/novo', methods=['GET', 'POST'])
def novo_setores():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip().upper()
        if nome:
            try:
              executar_query("INSERT INTO setores (nome) VALUES (?)", (nome,))
              flash('Setor adicionado com sucesso!', 'success')
            except:
              flash('Erro: Setor já existe ou problema no cadastro.', 'danger')
        return redirect(url_for('main.listar_setores'))
    return render_template('editar_setores.html', registro=None, tipo='setor')
 
@main.route('/parametros/setores/editar/<int:id>',  methods=['GET', 'POST'])
def editar_setores(id):
   if request.method == 'POST':
       nome = request.form.get('nome', '').strip().upper()
       if nome:
           executar_query("UPDATE setores SET nome = ? WHERE id = ?", (nome, id))
           flash('Setor atualizado com sucesso!', 'success')
       return redirect(url_for('main.listar_setores'))
   
   else:
       setores = executar_query("SELECT * FROM setores WHERE id = ?", (id,), fetch=True)
       if setores:
            return render_template('editar_setores.html', registro=setores[0], tipo='setor')
       else:
            flash('Setor não encontrado.', 'danger')
            return redirect(url_for('main.listar_setores'))

@main.route('/parametros/setores/excluir/<int:id>')
def excluir_setores(id):
    executar_query("DELETE FROM setores WHERE id = ?", (id,))
    flash('Setor excluído com sucesso!', 'warning')
    return redirect(url_for('main.listar_setores'))


# ------------------ STATUS_ATENDIMENTO ------------------

@main.route('/status_atendimentos')
def listar_status_atendimentos():
    status_atendimentos = executar_query("SELECT * FROM status_atendimentos ORDER BY nome", fetch=True)
    return render_template('consultar_status_atendimentos.html', status_atendimentos=status_atendimentos)

@main.route('/parametros/status_atendimentos')
def consultar_status_atendimentos():
    status_atendimentos = executar_query("SELECT * FROM status_atendimentos ORDER BY nome", fetch=True)
    return render_template('consultar_status_atendimentos.html', status_atendimentos=status_atendimentos)

@main.route('/parametros/status_atendimentos/novo', methods=['GET', 'POST'])
def novo_status_atendimentos():
   if request.method == 'POST':
        nome = request.form.get('nome', '').strip().upper()

        if nome:
           try:
              executar_query("INSERT INTO status_atendimentos (nome) VALUES (?)", (nome,))
              flash('Status adicionado com sucesso!', 'success')
           except:
             flash('Erro: setor já existe ou problema no cadastro.', 'danger')
        return redirect(url_for('main.listar_status_atendimentos'))
   
   return render_template('editar_status_atendimentos.html', status_atendimentos=None, tipo='status_atendimentos')

@main.route('/parametros/status_atendimentos/editar/<int:id>', methods=['GET', 'POST'])
def editar_status_atendimentos(id):
    if request.method == 'POST':
       nome = request.form.get('nome', '').strip().upper()
       if nome:
           executar_query("UPDATE status_atendimentos SET nome = ? WHERE id = ?", (nome, id))
           flash('Status atualizado com sucesso!', 'success')
       return redirect(url_for('main.listar_status_atendimentos'))
    else:
        status_atendimentos = executar_query("SELECT * FROM status_atendimentos WHERE id = ?", (id,), fetch=True)
        if status_atendimentos:
            return render_template('editar_status_atendimentos.html', registro=status_atendimentos[0], tipo='status_atendimentos')
        else:
            flash('Cliente não encontrado.', 'danger')
            return redirect(url_for('main.listar_status_atendimentos'))

@main.route('/parametros/status_atendimentos/excluir/<int:id>')
def excluir_status_atendimentos(id):
    executar_query("DELETE FROM status_atendimentos WHERE id = ?", (id,))
    flash('Status excluído com sucesso!', 'warning')
    return redirect(url_for('main.listar_status_atendimentos'))