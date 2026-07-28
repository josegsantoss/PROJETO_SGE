from database.connection import get_connection
import mysql.connector

def verificarLogin(email, senha):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore

    sql = """
    SELECT * FROM usuario WHERE email = %s AND senha = %s
    """

    try:
        cursor.execute(sql, (email,senha))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        if usuario:
            return usuario
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()

def cadastrarLogin(id_usuario, senha, email, cargo, departamento, salario, telefone, nivel_de_permissao):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore

    sql = """
    INSERT INTO usuario (id_usuario, senha, email, cargo, departamento, salario, telefone, nivel_de_permissao)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(sql, (id_usuario, senha, email, cargo, departamento, salario, telefone, nivel_de_permissao))
        conn.commit() # Obrigatório para salvar o cadastro no banco de dados
        cursor.close()
        conn.close()
        return True # Retorna verdadeiro indicando que o cadastro deu certo
        
    except Exception as e:
        print(e)
        conn.rollback() # Desfaz em caso de erro
        conn.close()
        return False

def listarLogin():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore

    sql = """
    SELECT * FROM usuario
    """

    try:
        cursor.execute(sql)
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        if usuarios:
            return usuarios
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()




# def listar_clientes():
#     """
#     Lista todos os clientes
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     cursor.execute(
#         "SELECT id_cliente, nome_cliente, telefone, celular, cpf, cnpj, email, cep FROM cliente ORDER BY nome_cliente"
#     )

#     clientes = cursor.fetchall()
#     conn.close()

#     return jsonify(clientes)


# def buscar_cliente(id_cliente):
#     """
#     Busca um cliente específico
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     cursor.execute(
#         "SELECT id_cliente, nome_cliente, telefone, celular, cpf, cnpj, email, cep FROM cliente WHERE id_cliente = %s",
#         (id_cliente,)
#     )

#     cliente = cursor.fetchone()
#     conn.close()

#     if cliente:
#         return jsonify(cliente)

#     return jsonify({"erro": "Cliente não encontrado"}), 404

# def buscar_cliente_por_cpf(cpf):
#     """
#     Busca um cliente pelo CPF
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     cursor.execute(
#         "SELECT id_cliente, nome_cliente, telefone, celular, cpf, cnpj, email, cep FROM cliente WHERE cpf = %s",
#         (cpf,)
#     )

#     cliente = cursor.fetchone()
#     conn.close()

#     if cliente:
#         return jsonify(cliente)

#     return jsonify({"erro": "Cliente não encontrado"}), 404


# def buscar_cliente_por_cnpj(cnpj):
#     """
#     Busca um cliente pelo CNPJ
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     cursor.execute(
#         "SELECT id_cliente, nome_cliente, telefone, celular, cpf, cnpj, email, cep FROM cliente WHERE cnpj = %s",
#         (cnpj,)
#     )

#     cliente = cursor.fetchone()
#     conn.close()

#     if cliente:
#         return jsonify(cliente)

#     return jsonify({"erro": "Cliente não encontrado"}), 404


# def atualizar_cliente(id_cliente):
#     """
#     Atualiza os dados de um cliente
#     """
#     dados = request.json

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     # Verifica se cliente existe
#     cursor.execute("SELECT id_cliente FROM cliente WHERE id_cliente = %s", (id_cliente,))
#     if not cursor.fetchone():
#         conn.close()
#         return jsonify({"erro": "Cliente não encontrado"}), 404

#     cursor = conn.cursor()

#     sql = """
#     UPDATE cliente
#     SET nome_cliente = %s,
#         telefone = %s,
#         celular = %s,
#         cpf = %s,
#         cnpj = %s,
#         email = %s,
#         cep = %s
#     WHERE id_cliente = %s
#     """

#     try:
#         cursor.execute(sql, (
#             dados.get('nome_cliente'),
#             dados.get('telefone', None),
#             dados.get('celular', None),
#             dados.get('cpf', None),
#             dados.get('cnpj', None),
#             dados.get('email', None),
#             dados.get('cep', None),
#             id_cliente
#         ))

#         conn.commit()
#         conn.close()

#         return jsonify({"mensagem": "Cliente atualizado com sucesso"})

#     except Exception as e:
#         conn.close()
#         return jsonify({"erro": f"Erro ao atualizar: {str(e)}"}), 400


# def deletar_cliente(id_cliente):
#     """
#     Deleta um cliente
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     # Verifica se existe
#     cursor.execute("SELECT id_cliente FROM cliente WHERE id_cliente = %s", (id_cliente,))
#     if not cursor.fetchone():
#         conn.close()
#         return jsonify({"erro": "Cliente não encontrado"}), 404

#     cursor = conn.cursor()

#     try:
#         cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
#         conn.commit()
#         conn.close()

#         return jsonify({"mensagem": "Cliente deletado com sucesso"})

#     except Exception as e:
#         conn.close()
#         return jsonify({"erro": f"Erro ao deletar: {str(e)}"}), 400


# def buscar_cliente_por_celular(celular):
#     """
#     Busca um cliente pelo celular
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     cursor.execute(
#         "SELECT id_cliente, nome_cliente, telefone, celular, cpf, cnpj, email, cep FROM cliente WHERE celular = %s",
#         (celular,)
#     )

#     cliente = cursor.fetchone()
#     conn.close()

#     if cliente:
#         return jsonify(cliente)

#     return jsonify({"erro": "Cliente não encontrado"}), 404


# def buscar_clientes_por_nome(nome):
#     """
#     Busca clientes por nome (busca parcial/LIKE)
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     cursor.execute(
#         "SELECT id_cliente, nome_cliente, telefone, celular, cpf, cnpj, email, cep FROM cliente WHERE nome_cliente LIKE %s ORDER BY nome_cliente",
#         (f"%{nome}%",)
#     )

#     clientes = cursor.fetchall()
#     conn.close()

#     if clientes:
#         return jsonify(clientes)

#     return jsonify({"mensagem": "Nenhum cliente encontrado"}), 404


# def buscar_clientes_por_cep(cep):
#     """
#     Busca clientes por CEP
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True) #type: ignore

#     cursor.execute(
#         "SELECT id_cliente, nome_cliente, telefone, celular, cpf, cnpj, email, cep FROM cliente WHERE cep = %s ORDER BY nome_cliente",
#         (cep,)
#     )

#     clientes = cursor.fetchall()
#     conn.close()

#     if clientes:
#         return jsonify(clientes)

#     return jsonify({"mensagem": "Nenhum cliente encontrado com esse CEP"}), 404


# if __name__ == '__main__':
#     app.run(debug=True)
