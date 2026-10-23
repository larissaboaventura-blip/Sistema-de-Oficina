"""Regra de veículos. Todo veículo pertence a um cliente cadastrado"""
import re
from datetime import date
from bd import ErroNegocio, execute, query

# Corrigido v.marca e adicionado espaço ao final da query
SELECT = ("SELECT v.id, v.cliente_id, c.nome AS cliente_nome, v.placa, v.marca, v.modelo, v.ano, v.cor "
          "FROM veiculos v JOIN clientes c ON c.id=v.cliente_id ")

def _validar(d):
    placa = (d.get("placa") or "").upper().replace("-","").strip()
    if not re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9]{2}", placa):
        raise ErroNegocio("Placa inválida (ex: ABC1D23).")
    if not (d.get("marca") or "").strip() or not (d.get("modelo") or "").strip():
        raise ErroNegocio("Informe a marca e o modelo.")
    try:
        ano = int(d.get("ano"))
    except (TypeError, ValueError):
        raise ErroNegocio("Ano inválido.")
    # Corrigido +_1 para + 1
    if not 1950 <= ano <= date.today().year + 1:
        raise ErroNegocio("Ano fora do intervalo permitido.")
    try:
        cliente_id = int(d.get("cliente_id"))
    except (TypeError, ValueError):
        raise ErroNegocio("Selecione o proprietário do veículo.")
    # Corrigido % para %s e a tupla (cliente_id,)
    if not query("SELECT id FROM clientes WHERE id = %s", (cliente_id,)):
        raise ErroNegocio("O cliente não está cadastrado.", 404)
    return placa, ano, cliente_id

# Listar veículo
def listar():
    return query(SELECT + "ORDER BY c.nome, v.modelo")

def obter(id):
    r = query(SELECT + "WHERE v.id = %s", (id,))
    if not r:
        raise ErroNegocio("Veículo não encontrado.", 404)
    return r[0]

# Verificar placa existente (Sintaxe SQL e argumentos corrigidos)
def _placa_em_uso(placa, ignorar_id=0):
    return query("SELECT id FROM veiculos WHERE placa = %s AND id <> %s", (placa, ignorar_id))

# Cadastrar veículo
def cadastrar(d):
    placa, ano, cid = _validar(d)
    if _placa_em_uso(placa):
        raise ErroNegocio("Placa já cadastrada.", 409)
    id_, _ = execute("INSERT INTO veiculos (cliente_id, placa, marca, modelo, ano, cor) VALUES (%s,%s,%s,%s,%s,%s)",
                     (cid, placa, d["marca"].strip(), d["modelo"].strip(), ano, d.get("cor")))
    return obter(id_)

# Editar veículos
def editar(id_, d):
    obter(id_)  # Corrigido de Id_ para id_
    placa, ano, cid = _validar(d)
    if _placa_em_uso(placa, id_):
        raise ErroNegocio("Placa já está cadastrada em outro veículo.", 409)
    execute("UPDATE veiculos SET cliente_id=%s, placa=%s, marca=%s, modelo=%s, ano=%s, cor=%s WHERE id=%s",
            (cid, placa, d["marca"].strip(), d["modelo"].strip(), ano, d.get("cor"), id_))
    return obter(id_)

def excluir(id_):
    obter(id_)
    if query("SELECT id FROM agendamentos WHERE veiculo_id = %s LIMIT 1", (id_,)):
        raise ErroNegocio("Veículo possui agendamentos associados. Exclua-os antes.", 409)
    execute("DELETE FROM veiculos WHERE id = %s", (id_,))