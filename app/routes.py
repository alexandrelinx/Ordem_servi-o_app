from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app.db import (
    criar_tabela, obter_os, inserir_os, carregar_nomes_clientes,
    carregar_nomes_solicitantes, carregar_nomes_equipamentos,
    carregar_nomes_setores, carregar_status_atendimentos,
    obter_os_por_id, atualizar_os, excluir_os, somar_valores
)
from app.relatorios.relatorio import gerar_relatorio_pdf
import io

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

@main.route('/alterar-os/<int:os_id>', methods=['GET', 'POST'])
def alterar_os(os_id):
    os_registro = obter_os_por_id(os_id)
    if not os_registro:
        flash("Ordem de Serviço não encontrada.", "danger")
        return redirect(url_for('main.dashboard'))

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
        atualizar_os(os_id, dados)
        flash("Ordem de Serviço atualizada com sucesso!", "success")
        return redirect(url_for('main.dashboard'))

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
    return redirect(url_for('main.dashboard'))

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
