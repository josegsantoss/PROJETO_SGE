from flask import Flask, request, jsonify
from CRUDS.connection import get_connection

app = Flask(__name__)


def cadastrar_equipamento():

    dados = request.json

    conn = get_connection()
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


def listar_equipamentos():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore

    cursor.execute("SELECT * FROM equipamento")

    equipamentos = cursor.fetchall()

    return jsonify(equipamentos)


def buscar_equipamento(id_equipamento):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore

    cursor.execute(
        "SELECT * FROM equipamento WHERE id_equipamento = %s",
        (id_equipamento,)
    )

    equipamento = cursor.fetchone()

    if equipamento:
        return jsonify(equipamento)

    return jsonify({"erro": "Equipamento não encontrado"}), 404



def atualizar_equipamento(id_equipamento):

    dados = request.json

    conn = get_connection()
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



def excluir_equipamento(id_equipamento):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM equipamento WHERE id_equipamento = %s",
        (id_equipamento,)
    )

    conn.commit()

    return jsonify({"mensagem": "Equipamento excluído com sucesso"})
