"""Entrada no sistema"""
import os 
from datetime import timedelta
from flask import Flask
from autenticacao import EXPIRACAO_SEGUNDOS
from rotas import bp


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")
app.config.update(
    PERMANET_SESSION_LIFETIME=timedelta(seconds=EXPIRACAO_SEGUNDOS),
    SESSION_REFRESH_EACH_REQUEST=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)