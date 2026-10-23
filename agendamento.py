
"""Regras de agendamento de serviços."""
from datetime import datetime
from bd import ErroNegocio, execute, query

STATUS = ("AGENDADO", "EM_ANDAMENTO", "CONCLUIDO", "CANCELADO")

SELECT = """
SELECT a.id, a.data_agendamento, a.status, a.observacao,
       s.id AS servico_id, s.descricao AS servico, s.valor,
       v.id AS veiculo_id, v.placa, v.marca, v.modelo, v.ano, v.cor,
       c.id AS cliente_id, c.nome AS cliente_nome, c.telefone, c.email, c.endereco
FROM agendamentos a
JOIN veiculos v ON v.id = a.veiculo_id
JOIN clientes c ON c.id = v.cliente_id
JOIN servicos s ON s.id = a.servico_id
"""


def _data(valor):
    try:
        return datetime.fromisoformat((valor or "").replace("Z", ""))
    except ValueError:
        raise ErroNegocio("Data/hora inválida.")


def listar():
    return query(SELECT + "ORDER BY a.data_agendamento ASC, a.id ASC")


def listar_servicos():
    return query("SELECT id, descricao, valor FROM servicos ORDER BY descricao")


def obter(id_):
    r = query(SELECT + "WHERE a.id = %s", (id_,))
    if not r:
        raise ErroNegocio("Agendamento não encontrado.", 404)
    return r[0]


def cadastrar(d):
    data = _data(d.get("data_agendamento"))
    if not query("SELECT id FROM veiculos WHERE id = %s", (d.get("veiculo_id"),)):
        raise ErroNegocio("Veículo não encontrado.", 404)
    if not query("SELECT id FROM servicos WHERE id = %s", (d.get("servico_id"),)):
        raise ErroNegocio("Serviço não encontrado.", 404)
    id_, _ = execute("INSERT INTO agendamentos (veiculo_id, servico_id, data_agendamento, observacao) "
                     "VALUES (%s,%s,%s,%s)", (d["veiculo_id"], d["servico_id"], data, d.get("observacao")))
    return obter(id_)


def editar(id_, d):
    """Atualiza a data (obrigatória) e, se enviados, status e observação."""
    atual = obter(id_)
    data = _data(d.get("data_agendamento"))
    status = d.get("status", atual["status"])
    if status not in STATUS:
        raise ErroNegocio("Status inválido.")
    execute("UPDATE agendamentos SET data_agendamento=%s, status=%s, observacao=%s WHERE id=%s",
            (data, status, d.get("observacao", atual["observacao"]), id_))
    return obter(id_)


def excluir(id_):
    obter(id_)
    execute("DELETE FROM agendamentos WHERE id = %s", (id_,))
        