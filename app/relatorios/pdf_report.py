from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

styles = getSampleStyleSheet()

def gerar_relatorio_os_por_cliente_pdf(dados, totais):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),  # alterado para landscape
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    elementos = []

    for cliente, meses in dados.items():
        elementos.append(Paragraph(f"Cliente: <b>{cliente}</b>", styles['Heading2']))
        elementos.append(Spacer(1, 12))

        for mes, os_list in meses.items():
            elementos.append(Paragraph(f"Mês: <b>{mes}</b>", styles['Heading3']))
            elementos.append(Spacer(1, 6))

            data = [["Solicitante", "Data Solicitação", "Problema", "Equipamento", "Data Conclusão", "Valor Serviço "]]

            for os_item in os_list:
                data.append([
                    os_item.get("solicitante", ""),
                    os_item.get("data_solicitacao", ""),
                    os_item.get("problema", ""),
                    os_item.get("equipamento", ""),
                    os_item.get("data_conclusao", ""),
                    f"{os_item.get('valor_servico', 0.0):.2f}",
                ])

            total_mes = totais[cliente][mes]
            data.append(["", "", "", "", "Total:", f"{total_mes:.2f}"])

            tabela = Table(data, colWidths=[3*cm, 3*cm, 12*cm, 3*cm, 3*cm, 2.5*cm])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),  # Alinha a coluna "Valor Serviço (R$)" à direita
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('ALIGN', (-2,-1), (-1,-1), 'RIGHT'),
            ]))

            elementos.append(tabela)
            elementos.append(Spacer(1, 20))

        elementos.append(PageBreak())

    doc.build(elementos)
    buffer.seek(0)
    return buffer


def gerar_relatorio_os_detalhado_pdf(os_detalhes):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),  # também alterado para landscape
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    elementos = []
    estilos = getSampleStyleSheet()

    elementos.append(Paragraph(f"Relatório Detalhado da OS ID: {os_detalhes.get('id', '')}", estilos['Heading1']))
    elementos.append(Spacer(1, 12))

    campos = [
        ("Cliente", os_detalhes.get("cliente", "")),
        ("Solicitante", os_detalhes.get("solicitante", "")),
        ("Equipamento", os_detalhes.get("equipamento", "")),
        ("Setor", os_detalhes.get("setor", "")),
        ("Status", os_detalhes.get("status", "")),
        ("Data Solicitação", os_detalhes.get("data_solicitacao", "")),
        ("Hora Solicitação", os_detalhes.get("hora_solicitacao", "")),
        ("Problema", os_detalhes.get("problema", "")),
        ("Análise do Problema", os_detalhes.get("analise_problema", "")),
        ("Solução", os_detalhes.get("solucao", "")),
        ("Valor do Serviço (R$)", f"{os_detalhes.get('valor_servico', 0.0):.2f}"),
        ("Data Conclusão", os_detalhes.get("data_conclusao", "")),
        ("Hora Conclusão", os_detalhes.get("hora_conclusao", "")),
    ]

    for label, valor in campos:
        elementos.append(Paragraph(f"<b>{label}:</b> {valor}", estilos['Normal']))
        elementos.append(Spacer(1, 8))

    doc.build(elementos)
    buffer.seek(0)
    return buffer
