from CONECTAR.funcaoConectar import conectar
from flask import Flask, jsonify


app = Flask(__name__)

#ROTAS PARA A TABELA CADASTRO USUÁRIO
##ROTA GET
##############################################
@app.route("/CadastroUsuario", methods=["GET"])
def listar_Cadastros():
    conn = conectar()
    #conn.execute("PRAGMA foreign_keys = ON") #ativa as chaves estrangeiras das tabelas (pois, não é ativado por padrão)
    cursor = conn.cursor()
    cursor.execute("SELECT IDCadastroUsuario, NomeUsuario, SenhaUsuario, SetorUsuario FROM CadastroUsuario")
    dados = [
        {"id": row[0], "NomeUsuario": row[1], "SenhaUsuario": row[2], "SetorUsuario": row[3]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(dados)

##ROTA DELETE
#############################################
from flask import jsonify, abort

@app.route("/CadastroUsuario/<int:id_usuario>", methods=["DELETE"])
def deletar_usuario(id_usuario):
    conn = conectar()
    cursor = conn.cursor()

    # tenta apagar o registro informado
    cursor.execute("DELETE FROM CadastroUsuario WHERE IDCadastroUsuario = ?", (id_usuario,))
    conn.commit()

    # cursor.rowcount informa quantas linhas foram afetadas
    if cursor.rowcount == 0:
        conn.close()
        # nenhum registro com esse ID → devolve 404
        abort(404, description="Usuário não encontrado")

    conn.close()
    # 204 = No Content (padrão para deleções bem‑sucedidas)
    return ("", 204)


##ROTA INSERT
#############################################

from flask import request, jsonify, abort
@app.route("/CadastroUsuario", methods=["POST"])
def criar_usuario():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Validação de campos obrigatórios
    campos_obrigatorios = {"NomeUsuario", "SenhaUsuario", "SetorUsuario"}
    if not campos_obrigatorios.issubset(dados.keys()):
        abort(400, description=f"Campos obrigatórios: {', '.join(campos_obrigatorios)}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO CadastroUsuario (NomeUsuario, SenhaUsuario, SetorUsuario) "
        "VALUES (?, ?, ?)",
        (dados["NomeUsuario"], dados["SenhaUsuario"], dados["SetorUsuario"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    # 201 Created + Location do recurso recém‑criado
    resposta = jsonify({"id": novo_id, **dados})
    resposta.status_code = 201
    resposta.headers["Location"] = f"/CadastroUsuario/{novo_id}"
    return resposta

##ROTA UPDATE
#############################################
@app.route("/CadastroUsuario/<int:id_usuario>", methods=["PUT", "PATCH"])
def atualizar_usuario(id_usuario):
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Para PUT, garanta que todos os campos estejam presentes
    if request.method == "PUT":
        campos_esperados = {"NomeUsuario", "SenhaUsuario", "SetorUsuario"}
        if not campos_esperados.issubset(dados.keys()):
            abort(400, description=f"PUT requer todos os campos: {', '.join(campos_esperados)}")

    # Monta dinamicamente o SQL somente com os campos enviados
    campos_validos = {"NomeUsuario", "SenhaUsuario", "SetorUsuario"}
    set_clauses = []
    valores = []
    for campo in campos_validos & dados.keys():
        set_clauses.append(f"{campo} = ?")
        valores.append(dados[campo])

    if not set_clauses:
        abort(400, description="Nenhum campo válido para atualizar")

    valores.append(id_usuario)  # último parâmetro é o WHERE

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE CadastroUsuario SET {', '.join(set_clauses)} WHERE IDCadastroUsuario = ?",
        tuple(valores)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Usuário não encontrado")

    conn.close()
    # 204 = No Content, mas você pode devolver 200 com o JSON atualizado se preferir
    return ("", 204)


if __name__ == "__main__":
    app.run(debug=True)

