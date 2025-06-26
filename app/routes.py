from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app.db import (
    criar_tabela, obter_os, inserir_os, carregar_nomes_clientes,
    carregar_nomes_solicitantes, carregar_nomes_equipamentos,
    carregar_nomes_setores, carregar_status_atendimentos,
    obter_os_por_id, atualizar_os, excluir_os, somar_valores
)
from app.relatorios.relatorio import gerar_relatorio_pdf
from app.db import obter_relatorio_os_por_cliente 
from flask import request, render_template
import io
from datetime import datetime
from collections import defaultdict
from datetime import datetime
from app import db 
from flask import request, render_template, make_response
from weasyprint import HTML
from flask import request, render_template, Blueprint
import pdfkit
from flask import Response, render_template, request


main = Blueprint('main', __name__)

# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ordem_servico'

    from .routes import main
    app.register_blueprint(main)

    from .db import criar_tabela

    @app.before_first_request
    def inicializar_banco():
        criar_tabela()

    return app

@main.route('/')
def dashboard():
    ordens = obter_os()
    print(ordens)
    total_valor = somar_valores()
    return render_template('dashboard.html', ordens=ordens, total=total_valor)

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
        return redirect(url_for('main.dashboard'))

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
    dados, totais = db.obter_relatorio_os_por_cliente_com_totais()

    if cliente_selecionado:
        dados = {cliente_selecionado: dados.get(cliente_selecionado, {})}
        totais = {cliente_selecionado: totais.get(cliente_selecionado, {})}
    else:
        # Se nenhum cliente foi selecionado, traz todos os clientes (dados e totais completos)
        # Não faz nada, mantém os dados originais completos

        # Só pra garantir, cliente_selecionado fica vazio para o template saber que é "todos"
        cliente_selecionado = ''
    clientes = db.carregar_nomes_clientes()

    return render_template('relatorio_os_cliente.html',
                           dados=dados,
                           totais=totais,
                           clientes=clientes,
                           cliente_selecionado=cliente_selecionado)



import pdfkit
from flask import Response, render_template, request

@main.route('/relatorio-os-cliente/pdf')
def relatorio_os_cliente_pdf():
    cliente_selecionado = request.args.get('cliente', '').strip()
    dados, totais = db.obter_relatorio_os_por_cliente_com_totais()

    if cliente_selecionado:
        dados = {cliente_selecionado: dados.get(cliente_selecionado, {})}
        totais = {cliente_selecionado: totais.get(cliente_selecionado, {})}

    html = render_template('relatorio_os_cliente_pdf.html',
                           dados=dados,
                           totais=totais,
                           cliente_selecionado=cliente_selecionado)
    
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')  # Ajuste o caminho
    pdf = pdfkit.from_string(html, False, configuration=config)

    response = Response(pdf, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=relatorio_os_cliente.pdf'
    return response
