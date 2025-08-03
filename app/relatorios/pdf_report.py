import os
import platform
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from app.db import obter_relatorio_os_por_cliente, somar_valores
from io import BytesIO

def gerar_relatorio_os_por_cliente_pdf(dados, totais,status_filtro=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elementos = []
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        name="TituloCentralizado",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=20
    )

    style_direita = ParagraphStyle(
        name='DireitaNegrito',
        parent=styles['Heading2'],
        alignment=TA_RIGHT,
        fontSize=12,
        spaceBefore=20
    )

    def cabecalho(canvas, doc):
        canvas.saveState()
        largura, altura = landscape(A4)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta onde está esse script
        APP_DIR = os.path.dirname(BASE_DIR)                    # pasta app
        logo_path = os.path.join(APP_DIR, "imagens", "ordem_de_servico1.jpg")

        print("Logo path:", logo_path)
        print("Existe a logo?", os.path.exists(logo_path))

        if os.path.exists(logo_path):
            try:
                canvas.drawImage(logo_path, 40, altura - 70, width=60, height=40, preserveAspectRatio=True)
            except Exception as e:
                print(f"Erro ao desenhar logo: {e}")
                pass
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
        canvas.drawCentredString(largura / 2.0, 20, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()

    total_geral = 0.0
    #elementos.append(Spacer(1, 12))

    total_por_cliente = {
       cliente: sum(mes_valores.values())
       for cliente, mes_valores in totais.items()
    }

    for cliente, meses in dados.items():
        elementos.append(Paragraph(f"<b>Cliente: {cliente}</b>", styles['Heading2']))
        for mes, os_list in meses.items():
            elementos.append(Paragraph(f"<b>Mês: {mes}</b>", styles['Heading3']))

            tabela_data = [["Solicitante", "Data Solicitação", "Problema", "Equipamento", "Data Conclusão", "Valor (R$)","Status" ]]
            subtotal_mes = 0.0

            for ordem in os_list:
                if status_filtro and ordem.get("status") != status_filtro:
                    continue  # pula OSs que não têm o status desejado


                valor_servico = ordem.get("valor_servico") or 0.0
                linha = [
                    ordem.get("solicitante", ""),
                    ordem.get("data_solicitacao", ""),
                    ordem.get("problema", ""),
                    ordem.get("equipamento", ""),
                    ordem.get("data_conclusao", ""),
                    f'{valor_servico:.2f}',
                    ordem.get("status", "")
                ]
                subtotal_mes += valor_servico
                tabela_data.append(linha)

            tabela = Table(tabela_data, colWidths=[2.5*cm, 3*cm, 12*cm, 3*cm, 3*cm,3*cm,2.5*cm])
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

        # <-- ADICIONE AQUI:
        total_cliente = total_por_cliente.get(cliente, 0.0)
        elementos.append(Paragraph(f"<b>Total do Cliente {cliente}: R$ {total_cliente:.2f}</b>", style_direita))
        elementos.append(Spacer(1, 0.5 * cm))


    elementos.append(Spacer(1, 0.5 * cm))

    # Totais finais (total de todas as OS de todos os clientes/meses)
    valor_total_absoluto = sum(
        sum(mes_valores.values()) for mes_valores in totais.values()
    )

    elementos.append(Paragraph(f"<b>Total Deste Relatório: R$ {total_geral:.2f}</b>", style_direita))
    elementos.append(Paragraph(f"<b>Total Geral de TODAS as OS: R$ {valor_total_absoluto:.2f}</b>", style_direita))

    doc.build(elementos, onFirstPage=cabecalho, onLaterPages=cabecalho)

    buffer.seek(0)
    return buffer
