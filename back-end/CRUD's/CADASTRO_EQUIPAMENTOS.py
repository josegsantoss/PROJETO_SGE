from flask import Flask, request, jsonify
from database.db import get_db_connection

app = Flask(__name__)

# CREATE
@app.route('/equipamentos', methods=['POST'])
def cadastrar_equipamento():

    dados = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO equipamento
        (marca, modelo, tipo_produto, num_serial)
        VALUES (%s, %s, %s, %s)
    """, (
        dados['marca'],
        dados['modelo'],
        dados['tipo_produto'],
        dados['num_serial']
    ))

    conn.commit()

    return jsonify({"mensagem": "Equipamento cadastrado com sucesso"}), 201


# READ ALL
@app.route('/equipamentos', methods=['GET'])
def listar_equipamentos():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore

    cursor.execute("SELECT * FROM equipamento")

    equipamentos = cursor.fetchall()

    return jsonify(equipamentos)


# READ ONE
@app.route('/equipamentos/<int:id_equipamento>', methods=['GET'])
def buscar_equipamento(id_equipamento):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore

    cursor.execute(
        "SELECT * FROM equipamento WHERE id_equipamento = %s",
        (id_equipamento,)
    )

    equipamento = cursor.fetchone()

    if equipamento:
        return jsonify(equipamento)

    return jsonify({"erro": "Equipamento não encontrado"}), 404


# UPDATE
@app.route('/equipamentos/<int:id_equipamento>', methods=['PUT'])
def atualizar_equipamento(id_equipamento):

    dados = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE equipamento
        SET marca = %s,
            modelo = %s,
            tipo_produto = %s,
            num_serial = %s
        WHERE id_equipamento = %s
    """, (
        dados['marca'],
        dados['modelo'],
        dados['tipo_produto'],
        dados['num_serial'],
        id_equipamento
    ))

    conn.commit()

    return jsonify({"mensagem": "Equipamento atualizado com sucesso"})


# DELETE
@app.route('/equipamentos/<int:id_equipamento>', methods=['DELETE'])
def excluir_equipamento(id_equipamento):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM equipamento WHERE id_equipamento = %s",
        (id_equipamento,)
    )

    conn.commit()

    return jsonify({"mensagem": "Equipamento excluído com sucesso"})
