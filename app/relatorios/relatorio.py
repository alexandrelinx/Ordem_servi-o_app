from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime
import os
import io

def gerar_relatorio_pdf(dados_os):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    elementos = []
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, leading=22, spaceAfter=12)
    style_header = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontSize=12, spaceAfter=6, textColor=colors.darkblue)
    style_normal = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, leading=14)
    style_bold = ParagraphStyle('BoldStyle', parent=style_normal, fontName='Helvetica-Bold')

    # Logo (ajuste o caminho conforme sua estrutura)
    logo_path = os.path.join(os.getcwd(),"app", "imagens", "Resolvidodownload.jpg")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=4*cm, height=2.5*cm)
    else:
        logo = Paragraph("Logo não encontrada", style_normal)
    print(logo_path)
    empresa_info = [
        [Paragraph("<b>AMOS Serviços de Tecnologia</b>", style_title)],
        [Paragraph("Endereço: AV Sapucaia, 50 - Ibura UR2 - Recife/PE - CEP 51340-720", style_normal)],
        [Paragraph("Telefone: (81) 98587-9259", style_normal)],
        [Paragraph("E-mail: alexandre.malaquiassilva@gmail.com", style_normal)]
    ]
    empresa_tabela = Table(empresa_info, colWidths=[12*cm])
    empresa_tabela.setStyle(TableStyle([("LEFTPADDING", (0,0), (-1,-1), 0)]))

    cabecalho = Table([[logo, empresa_tabela]], colWidths=[4.5*cm, 11*cm])
    cabecalho.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
    ]))
    elementos.append(cabecalho)
    elementos.append(Spacer(1, 20))

    titulo = Paragraph(f"Ordem de Serviço Nº {dados_os['id']}", style_title)
    elementos.append(titulo)
    elementos.append(Spacer(1, 10))

    os_info = [
        ["Cliente", dados_os["cliente"]],
        ["Solicitante", dados_os["solicitante"]],
        ["Equipamento", dados_os["equipamento"]],
        ["Setor", dados_os["setor"]],
        ["Status", dados_os["status"]],
        ["Data da Solicitação", dados_os["data_solicitacao"]],
        ["Hora da Solicitação", dados_os["hora_solicitacao"]],
        ["Data de Conclusão", dados_os["data_conclusao"]],
        ["Hora de Conclusão", dados_os["hora_conclusao"]],
        ["Valor", f'R$ {float(dados_os["valor_servico"]):,.2f}'.replace('.', ',')]
    ]
    tabela_dados = Table(os_info, colWidths=[5*cm, 10*cm])
    tabela_dados.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.black),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabela_dados)
    elementos.append(Spacer(1, 20))

    for titulo_texto, campo_texto in [
        ("Problema Relatado", dados_os["problema"]),
        ("Análise Técnica", dados_os["analise_problema"]),
        ("Solução Aplicada", dados_os["solucao"]),
    ]:
        elementos.append(Paragraph(titulo_texto, style_header))
        elementos.append(Paragraph(campo_texto, style_normal))
        elementos.append(Spacer(1, 12))

    elementos.append(Spacer(1, 30))
    assinaturas = [
        ["__________________________________", "__________________________________"],
        ["Assinatura do Cliente", "Assinatura do Técnico"]
    ]
    tabela_assinaturas = Table(assinaturas, colWidths=[8*cm, 8*cm])
    tabela_assinaturas.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 1), (-1, -1), 10)
    ]))
    elementos.append(tabela_assinaturas)

    elementos.append(Spacer(1, 20))
    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
    elementos.append(Paragraph(f"Emitido em: {data_emissao}", style_normal))

    doc.build(elementos)
    buffer.seek(0)
    return buffer
