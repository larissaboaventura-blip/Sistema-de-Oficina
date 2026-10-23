"""Autenticação: bcrypt (senha e CPF) e sessão com tempo de expiração."""
import time
from functools import wraps
import bcrypt
from flask import jsonify, redirect, session
from bd import ErroNegocio, query

EXPIRACAO_SEGUNDOS = 30 * 60  # 30 minutos


def gerar_hash(texto):
    return bcrypt.hashpw(texto.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")


def conferir(texto, hash_salvo):
    try:
        return bcrypt.checkpw(texto.encode("utf-8"), hash_salvo.encode("utf-8"))
    except ValueError:
        return False


def autenticar(login, senha):
    login, senha = (login or "").strip(), senha or ""
    if not login or not senha:
        raise ErroNegocio("Informe usuário e senha.", 400)
    u = query("SELECT id, nome, senha_hash FROM usuarios WHERE login = %s", (login,))
    # mensagem única: não revela se o usuário existe
    if not u or not conferir(senha, u[0]["senha_hash"]):
        raise ErroNegocio("Usuário ou senha inválidos.", 401)
    return u[0]


def iniciar_sessao(usuario):
    session.clear()
    session.permanent = True
    session.update(usuario_id=usuario["id"], nome=usuario["nome"], login_em=time.time())


def logado():
    if "usuario_id" not in session:
        return False
    if time.time() - session.get("login_em", 0) > EXPIRACAO_SEGUNDOS:
        session.clear()
        return False
    return True


def api_protegida(f):
    @wraps(f)
    def interno(*a, **k):
        if not logado():
            return jsonify(erro="Sessão expirada. Faça login novamente."), 401
        return f(*a, **k)
    return interno


def pagina_protegida(f):
    @wraps(f)
    def interno(*a, **k):
        return f(*a, **k) if logado() else redirect("/login?expirou=1")
    return interno


    