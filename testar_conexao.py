"""Testar a conexão com o bamco de dados testar_conexao.py"""
from bd import testar_conexao
try:
    print("Conexão OK: ", testar_conexao())
except Exception as e:
    print("Falha na conexão:", e)