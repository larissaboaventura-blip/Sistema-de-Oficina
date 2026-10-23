"""Regras de clientes. O CPF é guardado apenas como hash bcrypt (LGPD)."""
import re
from autenticacao import conferir, gerar_hash
from bd import ErroNegocio, execute, query

COLUNAS = "id, nome, telefone, email, endereco, criado_em"


def so_digitos(s):
    return re.sub(r"\D", "", s or "")


def cpf_valido(cpf):
    """Teste acadêmico: valida apenas a quantidade de dígitos (11), sem checar dígitos verificadores."""
    return len(so_digitos(cpf)) == 11


def _validar(d, cpf_obrigatorio):
    nome = (d.get("nome") or "").strip()
    email = (d.get("email") or "").strip()
    if len(nome) < 3:
        raise ErroNegocio("Informe o nome completo.")
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ErroNegocio("E-mail inválido.")
    cpf = so_digitos(d.get("cpf"))
    if cpf_obrigatorio or cpf:
        if not cpf_valido(cpf):
            raise ErroNegocio("CPF deve conter 11 dígitos.")
    return nome, cpf, email


def _cpf_ja_existe(cpf, ignorar_id=None):
    for r in query("SELECT id, cpf_hash FROM clientes"):
        if r["id"] != ignorar_id and conferir(cpf, r["cpf_hash"]):
            return True
    return False


def listar(termo=""):
    termo = (termo or "").strip()
    if not termo:
        return query(f"SELECT {COLUNAS} FROM clientes ORDER BY nome")
    like = f"%{termo}%"
    achados = query(f"SELECT {COLUNAS} FROM clientes WHERE nome LIKE %s OR email LIKE %s "
                    "OR telefone LIKE %s ORDER BY nome", (like, like, like))
    cpf = so_digitos(termo)
    if len(cpf) == 11:  # hash bcrypt não permite LIKE: compara um a um
        ids = {a["id"] for a in achados}
        for r in query("SELECT id, cpf_hash FROM clientes"):
            if r["id"] not in ids and conferir(cpf, r["cpf_hash"]):
                achados += query(f"SELECT {COLUNAS} FROM clientes WHERE id = %s", (r["id"],))
    return achados


def obter(id_):
    r = query(f"SELECT {COLUNAS} FROM clientes WHERE id = %s", (id_,))
    if not r:
        raise ErroNegocio("Cliente não encontrado.", 404)
    return r[0]


def cadastrar(d):
    nome, cpf, email = _validar(d, True)
    if _cpf_ja_existe(cpf):
        raise ErroNegocio("Já existe cliente com este CPF.", 409)
    id_, _ = execute("INSERT INTO clientes (nome, cpf_hash, telefone, email, endereco) VALUES (%s,%s,%s,%s,%s)",
                     (nome, gerar_hash(cpf), d.get("telefone"), email or None, d.get("endereco")))
    return obter(id_)


def editar(id_, d):
    obter(id_)
    nome, cpf, email = _validar(d, False)
    if cpf and _cpf_ja_existe(cpf, id_):
        raise ErroNegocio("Já existe outro cliente com este CPF.", 409)
    execute("UPDATE clientes SET nome=%s, telefone=%s, email=%s, endereco=%s WHERE id=%s",
            (nome, d.get("telefone"), email or None, d.get("endereco"), id_))
    if cpf:
        execute("UPDATE clientes SET cpf_hash=%s WHERE id=%s", (gerar_hash(cpf), id_))
    return obter(id_)


def excluir(id_):
    obter(id_)
    if query("SELECT id FROM veiculos WHERE cliente_id = %s LIMIT 1", (id_,)):
        raise ErroNegocio("Cliente possui veículos cadastrados. Exclua-os antes.", 409)
    execute("DELETE FROM clientes WHERE id = %s", (id_,))
