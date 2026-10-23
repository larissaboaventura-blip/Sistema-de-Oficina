"""Acesso ao MySQL"""
import os
from datetime import date, datetime
import mysql.connector

CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
     port=os.getenv("DB_PORT", "3306"),
     user=os.getenv("DB_USER", "root"),
     password=os.getenv("DB_PASSWORD", "12345"),
     database=os.getenv("DB_NAME", "saep_db_v1"),
)

class ErroNegocio(Exception):
    """Validação de conexão"""
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem, self.status = mensagem, status
        
def conectar():
    return mysql.connector.connect(**CONFIG)

def _limpar(linha):
    return {k: (v.isoformat() if isinstance(v, (datetime, date)) else v) for k, v in linha.items()}

def query(sql, params=()):
    con = conectar()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, params)
        return [_limpar(r) for r in cur.fetchall()]
    finally:
        con.close()

def execute(sql, params=()):
    """INSERT, UPDATE, DELETE. Retoma id_inserido, linhas_afetadas"""
    con = conectar()
    try: 
        cur = con.cursor()
        cur.execute(sql, params)
        con. commit()
        return cur.lastrowid, cur.rowcount
    finally:
        con.close()
        
def testar_conexao():
    return query("SELECT DATABASE() AS banco, VERSION() AS versao") [0]