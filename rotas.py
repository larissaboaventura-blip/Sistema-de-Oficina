"""Todas as rotas HTTP (páginas e API JSON)."""
import os
from functools import wraps
import mysql.connector
from flask import Blueprint, jsonify, redirect, request, send_from_directory, session
import agendamento, autenticacao as auth, clientes, veiculos
from bd import ErroNegocio, testar_conexao

bp = Blueprint("rotas", __name__)
PASTA = os.path.join(os.path.dirname(__file__), "templates")


def tratar(f):
    """Converte erros em respostas JSON padronizadas."""
    @wraps(f)
    def interno(*a, **k):
        try:
            return f(*a, **k)
        except ErroNegocio as e:
            return jsonify(erro=e.mensagem), e.status
        except mysql.connector.Error:
            return jsonify(erro="Erro ao acessar o banco de dados."), 500
    return interno


def pagina(nome):
    return send_from_directory(PASTA, nome)


# ---------- páginas ----------
@bp.route("/")
def raiz():
    return redirect("/principal" if auth.logado() else "/login")


@bp.route("/login")
def p_login():
    return pagina("login.html")


@bp.route("/principal")
@auth.pagina_protegida
def p_principal():
    return pagina("principal.html")


@bp.route("/clientes")
@auth.pagina_protegida
def p_clientes():
    return pagina("clientes.html")


@bp.route("/veiculos")
@auth.pagina_protegida
def p_veiculos():
    return pagina("veiculos.html")


@bp.route("/agendamentos")
@auth.pagina_protegida
def p_agendamentos():
    return pagina("agendamentos.html")


# ---------- autenticação ----------
@bp.post("/api/login")
@tratar
def login():
    d = request.get_json(silent=True) or {}
    auth.iniciar_sessao(auth.autenticar(d.get("login"), d.get("senha")))
    return jsonify(ok=True, nome=session["nome"])


@bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@bp.get("/api/me")
@auth.api_protegida
def me():
    return jsonify(nome=session["nome"])


@bp.get("/api/teste-conexao")
@tratar
def teste_conexao():
    return jsonify(testar_conexao())


# ---------- clientes ----------
@bp.get("/api/clientes")
@auth.api_protegida
@tratar
def c_listar():
    return jsonify(clientes.listar(request.args.get("q", "")))


@bp.post("/api/clientes")
@auth.api_protegida
@tratar
def c_cadastrar():
    return jsonify(clientes.cadastrar(request.get_json(silent=True) or {})), 201


@bp.put("/api/clientes/<int:id_>")
@auth.api_protegida
@tratar
def c_editar(id_):
    return jsonify(clientes.editar(id_, request.get_json(silent=True) or {}))


@bp.delete("/api/clientes/<int:id_>")
@auth.api_protegida
@tratar
def c_excluir(id_):
    clientes.excluir(id_)
    return jsonify(ok=True)


# ---------- veículos ----------
@bp.get("/api/veiculos")
@auth.api_protegida
@tratar
def v_listar():
    return jsonify(veiculos.listar())


@bp.post("/api/veiculos")
@auth.api_protegida
@tratar
def v_cadastrar():
    return jsonify(veiculos.cadastrar(request.get_json(silent=True) or {})), 201


@bp.put("/api/veiculos/<int:id_>")
@auth.api_protegida
@tratar
def v_editar(id_):
    return jsonify(veiculos.editar(id_, request.get_json(silent=True) or {}))


@bp.delete("/api/veiculos/<int:id_>")
@auth.api_protegida
@tratar
def v_excluir(id_):
    veiculos.excluir(id_)
    return jsonify(ok=True)


# ---------- agendamentos ----------
@bp.get("/api/servicos")
@auth.api_protegida
@tratar
def s_listar():
    return jsonify(agendamento.listar_servicos())


@bp.get("/api/agendamentos")
@auth.api_protegida
@tratar
def a_listar():
    return jsonify(agendamento.listar())


@bp.post("/api/agendamentos")
@auth.api_protegida
@tratar
def a_cadastrar():
    return jsonify(agendamento.cadastrar(request.get_json(silent=True) or {})), 201


@bp.put("/api/agendamentos/<int:id_>")
@auth.api_protegida
@tratar
def a_editar(id_):
    return jsonify(agendamento.editar(id_, request.get_json(silent=True) or {}))


@bp.delete("/api/agendamentos/<int:id_>")
@auth.api_protegida
@tratar
def a_excluir(id_):
    agendamento.excluir(id_)
    return jsonify(ok=True)

