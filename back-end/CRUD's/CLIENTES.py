from CRUDS.connection import get_connection

class Cliente:
    @staticmethod
    def listar_clientes():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT id_cliente, nome_cliente, telefone, cpf, email
        FROM cliente
        ORDER BY nome_cliente
        """

        try:
            cursor.execute(sql)
            clientes = cursor.fetchall()
            cursor.close()
            conn.close()
            if clientes:
                return clientes
            else:
                return None
            
        except Exception as e:
            print(e)
            conn.close()

    @staticmethod
    def buscar_por_id(id_cliente):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT id_cliente, nome_cliente, telefone, cpf, email
        FROM cliente
        WHERE id_cliente = %s
        """

        try:
            cursor.execute(sql, (id_cliente,))
            cliente = cursor.fetchone()
            cursor.close()
            conn.close()
            if cliente:
                return cliente
            else:
                return None
            
        except Exception as e:
            print(e)
            conn.close()

    @staticmethod
    def buscar_cliente_por_cpf(cpf):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT id_cliente, nome_cliente, telefone, cpf, email
        FROM cliente
        WHERE cpf = %s
        """

        try:
            cursor.execute(sql, (cpf,))
            cliente = cursor.fetchone()
            cursor.close()
            conn.close()
            if cliente:
                return cliente
            else:
                return None
            
        except Exception as e:
            print(e)
            conn.close()

    @staticmethod
    def cadastrar_cliente(nome_cliente, telefone, cpf, email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        INSERT INTO cliente (nome_cliente, telefone, cpf, email)
        VALUES (%s, %s, %s, %s)
        """

        try:
            cursor.execute(sql, (nome_cliente, telefone, cpf, email))
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(e)
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def atualizar_cliente(id_cliente, nome_cliente, telefone, cpf, email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT id_cliente FROM cliente WHERE id_cliente = %s
        """

        try:
            cursor.execute(sql, (id_cliente,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return False

            sql_update = """
            UPDATE cliente
            SET nome_cliente = %s, telefone = %s, cpf = %s, email = %s
            WHERE id_cliente = %s
            """

            cursor.execute(sql_update, (nome_cliente, telefone, cpf, email, id_cliente))
            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print(e)
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def deletar_cliente(id_cliente):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT id_cliente FROM cliente WHERE id_cliente = %s
        """

        try:
            cursor.execute(sql, (id_cliente,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return False

            sql_delete = """
            DELETE FROM cliente WHERE id_cliente = %s
            """

            cursor.execute(sql_delete, (id_cliente,))
            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print(e)
            conn.rollback()
            conn.close()
            return False
