import os
import platform
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER

from app.db import obter_relatorio_os_por_cliente

def gerar_relatorio_geral_por_cliente_pdf(nome_arquivo="relatorio_os_por_cliente.pdf"):
    dados = obter_relatorio_os_por_cliente()

    # Cria a pasta "relatorios" se não existir
    pasta_relatorios = os.path.join(os.getcwd(), "relatorios")
    os.makedirs(pasta_relatorios, exist_ok=True)

    # Define o caminho completo do arquivo
    caminho_arquivo = os.path.join(pasta_relatorios, nome_arquivo)

    # Gera o PDF em modo paisagem
    doc = SimpleDocTemplate(caminho_arquivo, pagesize=landscape(A4))
    largura, altura = landscape(A4)

    elementos = []
    styles = getSampleStyleSheet()

    # Estilo centralizado para o título
    titulo_style = ParagraphStyle(
        name="TituloCentralizado",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=20
    )

    def cabecalho(canvas, doc):
        canvas.saveState()
        largura, altura = landscape(A4)

        logo_path = "c:/ForPoint/V3/ordem_servico/imagens/Resolvidodownload.jpg"
        if os.path.exists(logo_path):
            try:
                canvas.drawImage(logo_path, 40, altura - 70, width=60, height=40, preserveAspectRatio=True)
            except Exception:
                pass

        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawCentredString(largura / 2.0, altura - 50, "Relatório de OS por Cliente")

        canvas.setFont("Helvetica", 10)
        data_emissao = datetime.now().strftime("Emitido em: %d/%m/%Y %H:%M")
        canvas.drawCentredString(largura / 2.0, altura - 65, data_emissao)

        canvas.setFont("Helvetica", 9)
        numero_pagina = f"Página {canvas.getPageNumber()}"
        canvas.drawCentredString(largura / 2.0, 20, numero_pagina)

        canvas.restoreState()

    elementos.append(Spacer(1, 12))

    total_geral = 0.0

    # Itera por cliente
    for cliente, meses in dados.items():
        elementos.append(Paragraph(f"<b>Cliente: {cliente}</b>", styles['Heading2']))
        # Itera por mês dentro do cliente
        for mes, os_list in meses.items():
            elementos.append(Paragraph(f"<b>Mês: {mes}</b>", styles['Heading3']))

            tabela_data = [["Solicitante", "Data Solicitação", "Problema", "Equipamento", "Data Conclusão", "Valor (R$)"]]
            subtotal_mes = 0.0

            for ordem in os_list:
                valor_servico = ordem.get("valor_servico") or 0.0
                linha = [
                    ordem.get("solicitante", ""),
                    ordem.get("data_solicitacao", ""),
                    ordem.get("problema", ""),
                    ordem.get("equipamento", ""),
                    ordem.get("data_conclusao", ""),
                    f'{valor_servico:.2f}'
                ]
                subtotal_mes += valor_servico
                tabela_data.append(linha)

            tabela = Table(tabela_data, colWidths=[3*cm, 3*cm, 12*cm, 3*cm, 3*cm, 2.5*cm])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            elementos.append(tabela)
            elementos.append(Paragraph(f"<b>Subtotal {mes}: R$ {subtotal_mes:.2f}</b>", styles['Normal']))
            elementos.append(Spacer(1, 0.3 * cm))
            total_geral += subtotal_mes

        elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph(f"<b>Total Geral de OS: R$ {total_geral:.2f}</b>", styles['Heading2']))

    doc.build(elementos, onFirstPage=cabecalho, onLaterPages=cabecalho)

    # Abre o PDF automaticamente, conforme o sistema operacional
    if platform.system() == "Windows":
        os.startfile(caminho_arquivo)
    elif platform.system() == "Darwin":
        os.system(f"open '{caminho_arquivo}'")
    else:
        os.system(f"xdg-open '{caminho_arquivo}'")