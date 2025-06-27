import sqlite3
import os
from collections import defaultdict
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'banco', 'solicitacoes.db')

def conectar():
   # return sqlite3.connect(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
    return conn

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()

    # Supondo que suas tabelas sejam algo assim, ajuste conforme seu banco
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS setores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status_atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )""")

    
    cursor.execute("""   
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL
     )""")
     


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        solicitante_id INTEGER,
        equipamento_id INTEGER,
        setor_id INTEGER,
        status_id INTEGER,
        data_solicitacao TEXT,
        hora_solicitacao TEXT,
        problema TEXT,
        analise_problema TEXT,
        solucao TEXT,
        valor_servico REAL,
        data_conclusao TEXT,
        hora_conclusao TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (solicitante_id) REFERENCES solicitantes(id),
        FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id),
        FOREIGN KEY (setor_id) REFERENCES setores(id),
        FOREIGN KEY (status_id) REFERENCES status_atendimentos(id)
    )""")

    conn.commit()
    conn.close()

def carregar_nomes_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes ORDER BY nome")
    nomes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return nomes

def carregar_nomes_solicitantes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM solicitantes ORDER BY nome")
    nomes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return nomes

def carregar_nomes_equipamentos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM equipamentos ORDER BY nome")
    nomes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return nomes

def carregar_nomes_setores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM setores ORDER BY nome")
    nomes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return nomes

def carregar_status_atendimentos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM status_atendimentos ORDER BY nome")
    nomes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return nomes

def inserir_os(dados):
    conn = conectar()
    cursor = conn.cursor()
    # Tenta obter os ids das tabelas relacionadas (se não existirem, cria)
    cliente_id = obter_ou_criar_id(conn, 'clientes', dados["cliente"])
    solicitante_id = obter_ou_criar_id(conn, 'solicitantes', dados["solicitante"])
    equipamento_id = obter_ou_criar_id(conn, 'equipamentos', dados["equipamento"])
    setor_id = obter_ou_criar_id(conn, 'setores', dados["setor"])
    status_id = obter_ou_criar_id(conn, 'status_atendimentos', dados["status"])

    cursor.execute("""
    INSERT INTO solicitacoes (
        cliente_id, solicitante_id, equipamento_id, setor_id, status_id,
        data_solicitacao, hora_solicitacao, problema, analise_problema,
        solucao, valor_servico, data_conclusao, hora_conclusao
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cliente_id,
        solicitante_id,
        equipamento_id,
        setor_id,
        status_id,
        dados["data_solicitacao"],
        dados["hora_solicitacao"],
        dados["problema"],
        dados["analise_problema"],
        dados["solucao"],
        dados["valor_servico"],
        dados["data_conclusao"],
        dados["hora_conclusao"]
    ))
    conn.commit()
    conn.close()

def obter_ou_criar_id(conn, tabela, nome):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {tabela} WHERE nome = ?", (nome,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute(f"INSERT INTO {tabela} (nome) VALUES (?)", (nome,))
        conn.commit()
        return cursor.lastrowid

def obter_os(cliente=None, status=None):
    conn = conectar()
    cursor = conn.cursor()
   # cursor.execute("""
    query ="""
    SELECT
        s.id,
        c.nome as cliente,
        so.nome as solicitante,
        e.nome as equipamento,
        se.nome as setor,
        st.nome as status,
        s.data_solicitacao,
        s.hora_solicitacao,
        s.problema,
        s.analise_problema,
        s.solucao,
        s.valor_servico,
        s.data_conclusao,
        s.hora_conclusao
    FROM solicitacoes s
    LEFT JOIN clientes c ON s.cliente_id = c.id
    LEFT JOIN solicitantes so ON s.solicitante_id = so.id
    LEFT JOIN equipamentos e ON s.equipamento_id = e.id
    LEFT JOIN setores se ON s.setor_id = se.id
    LEFT JOIN status_atendimentos st ON s.status_id = st.id
    """
    conditions = []
    params = []

    if cliente:
        conditions.append("c.nome = ?")
        params.append(cliente)
    if status:
        conditions.append("st.nome = ?")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY s.id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
    #return rows

def obter_os_por_id(os_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        s.id,
        c.nome as cliente,
        so.nome as solicitante,
        e.nome as equipamento,
        se.nome as setor,
        st.nome as status,
        s.data_solicitacao,
        s.hora_solicitacao,
        s.problema,
        s.analise_problema,
        s.solucao,
        s.valor_servico,
        s.data_conclusao,
        s.hora_conclusao
    FROM solicitacoes s
    LEFT JOIN clientes c ON s.cliente_id = c.id
    LEFT JOIN solicitantes so ON s.solicitante_id = so.id
    LEFT JOIN equipamentos e ON s.equipamento_id = e.id
    LEFT JOIN setores se ON s.setor_id = se.id
    LEFT JOIN status_atendimentos st ON s.status_id = st.id
    WHERE s.id = ?
    """, (os_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)  # converte para dict para facilitar acesso no relatorio
    return None
    # return row
   
def obter_relatorio_os_por_cliente():
    """
    Retorna um dict com os dados das OS agrupados por cliente e mês:
    {
      "Cliente A": {
        "2025-06": [
          { dados da OS 1 },
          { dados da OS 2 },
          ...
        ],
        ...
      },
      ...
    }
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        c.nome as cliente,
        so.nome as solicitante,
        s.data_solicitacao,
        s.problema,
        e.nome as equipamento,
        s.data_conclusao,
        s.valor_servico
    FROM solicitacoes s
    LEFT JOIN clientes c ON s.cliente_id = c.id
    LEFT JOIN solicitantes so ON s.solicitante_id = so.id
    LEFT JOIN equipamentos e ON s.equipamento_id = e.id
    ORDER BY c.nome, s.data_solicitacao
    """)
    rows = cursor.fetchall()
    conn.close()

    resultado = defaultdict(lambda: defaultdict(list))

    for row in rows:
        cliente = row["cliente"] or "Sem Cliente"
        data_solicitacao = row["data_solicitacao"]
        # Extrai o mês/ano no formato YYYY-MM para agrupar
        try:
            mes = datetime.strptime(data_solicitacao, "%Y-%m-%d").strftime("%Y-%m")
        except Exception:
            mes = "Data Inválida"
          
        os_info = {
            "solicitante": row["solicitante"] or "",
            "data_solicitacao": data_solicitacao or "",
            "problema": row["problema"] or "",
            "equipamento": row["equipamento"] or "",
            "data_conclusao": row["data_conclusao"] or "",
            "valor_servico": row["valor_servico"] or 0.0,
        }

        resultado[cliente][mes].append(os_info)

    return resultado


def atualizar_os(os_id, dados):
    conn = conectar()
    cursor = conn.cursor()
    cliente_id = obter_ou_criar_id(conn, 'clientes', dados["cliente"])
    solicitante_id = obter_ou_criar_id(conn, 'solicitantes', dados["solicitante"])
    equipamento_id = obter_ou_criar_id(conn, 'equipamentos', dados["equipamento"])
    setor_id = obter_ou_criar_id(conn, 'setores', dados["setor"])
    status_id = obter_ou_criar_id(conn, 'status_atendimentos', dados["status"])

    cursor.execute("""
    UPDATE solicitacoes SET
        cliente_id = ?, solicitante_id = ?, equipamento_id = ?, setor_id = ?, status_id = ?,
        data_solicitacao = ?, hora_solicitacao = ?, problema = ?, analise_problema = ?,
        solucao = ?, valor_servico = ?, data_conclusao = ?, hora_conclusao = ?
    WHERE id = ?
    """, (
        cliente_id,
        solicitante_id,
        equipamento_id,
        setor_id,
        status_id,
        dados["data_solicitacao"],
        dados["hora_solicitacao"],
        dados["problema"],
        dados["analise_problema"],
        dados["solucao"],
        dados["valor_servico"],
        dados["data_conclusao"],
        dados["hora_conclusao"],
        os_id
    ))
    conn.commit()
    conn.close()

def excluir_os(os_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM solicitacoes WHERE id = ?", (os_id,))
    conn.commit()
    conn.close()

def somar_valores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_servico) FROM solicitacoes")
    total = cursor.fetchone()[0]
    conn.close()
    return total or 0



def obter_relatorio_os_por_cliente_com_totais(cliente=None):
    conn = conectar()
    cursor = conn.cursor()

    if cliente:
        cursor.execute("""
        SELECT
            c.nome as cliente,
            so.nome as solicitante,
            s.data_solicitacao,
            s.problema,
            e.nome as equipamento,
            s.data_conclusao,
            s.valor_servico
        FROM solicitacoes s
        LEFT JOIN clientes c ON s.cliente_id = c.id
        LEFT JOIN solicitantes so ON s.solicitante_id = so.id
        LEFT JOIN equipamentos e ON s.equipamento_id = e.id
        WHERE c.nome = ?
        ORDER BY c.nome, s.data_solicitacao
        """, (cliente,))
    else:
        cursor.execute("""
        SELECT
            c.nome as cliente,
            so.nome as solicitante,
            s.data_solicitacao,
            s.problema,
            e.nome as equipamento,
            s.data_conclusao,
            s.valor_servico
        FROM solicitacoes s
        LEFT JOIN clientes c ON s.cliente_id = c.id
        LEFT JOIN solicitantes so ON s.solicitante_id = so.id
        LEFT JOIN equipamentos e ON s.equipamento_id = e.id
        ORDER BY c.nome, s.data_solicitacao
        """)

    rows = cursor.fetchall()
    conn.close()

    resultado = defaultdict(lambda: defaultdict(list))
    totais = defaultdict(lambda: defaultdict(float))  # cliente -> mes -> total

    for row in rows:
        cliente_nome = row["cliente"] or "Sem Cliente"
        data_solicitacao = row["data_solicitacao"]
        try:
            mes = datetime.strptime(data_solicitacao, "%Y-%m-%d").strftime("%Y-%m")
        except Exception:
            mes = "Data Inválida"

        os_info = {
            "solicitante": row["solicitante"] or "",
            "data_solicitacao": data_solicitacao or "",
            "problema": row["problema"] or "",
            "equipamento": row["equipamento"] or "",
            "data_conclusao": row["data_conclusao"] or "",
            "valor_servico": row["valor_servico"] or 0.0,
        }

        resultado[cliente_nome][mes].append(os_info)
        totais[cliente_nome][mes] += os_info["valor_servico"]

    return resultado, totais
