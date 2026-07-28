from database.connection import get_connection
from datetime import datetime

def calcular_total_orcamento(
    itens_preco_quantidade: list,
    desconto_percent: float = 0,
    desconto_reais: float = 0,
    frete: float = 0,
    imposto_percent: float = 0,
) -> float:
    subtotal = sum(float(item.get("preco", 0)) * int(item.get("quantidade", 1)) for item in itens_preco_quantidade)
    desconto = (subtotal * float(desconto_percent) / 100) + float(desconto_reais)
    desconto = min(desconto, subtotal)
    valor_pos_desconto = subtotal - desconto
    imposto = valor_pos_desconto * float(imposto_percent) / 100
    return round(valor_pos_desconto + imposto + float(frete), 2)

def criar_orcamento(numero, data, validade, cliente, documento, contato, vendedor, desconto_percent, desconto_reais, frete, imposto, pagamento, condicao, garantia, observacoes):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO orcamento (numero, data, validade, cliente, documento, contato, vendedor, desconto_percent, desconto_reais, frete, imposto, pagamento, condicao, garantia, observacoes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(sql, (numero, data, validade, cliente, documento, contato, vendedor, desconto_percent, desconto_reais, frete, imposto, pagamento, condicao, garantia, observacoes))
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return False

def listar_orcamentos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT * FROM orcamento ORDER BY data DESC
    """

    try:
        cursor.execute(sql)
        orcamentos = cursor.fetchall()
        cursor.close()
        conn.close()
        if orcamentos:
            return orcamentos
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()

def buscar_orcamento(id_orcamento):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT * FROM orcamento WHERE id_orcamento = %s
    """

    try:
        cursor.execute(sql, (id_orcamento,))
        orcamento = cursor.fetchone()
        cursor.close()
        conn.close()
        if orcamento:
            return orcamento
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()

def buscar_orcamento_por_numero(numero):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT * FROM orcamento WHERE numero = %s
    """

    try:
        cursor.execute(sql, (numero,))
        orcamento = cursor.fetchone()
        cursor.close()
        conn.close()
        if orcamento:
            return orcamento
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()

def buscar_orcamento_por_cliente(cliente):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT * FROM orcamento WHERE cliente LIKE %s ORDER BY data DESC
    """

    try:
        cursor.execute(sql, (f"%{cliente}%",))
        orcamentos = cursor.fetchall()
        cursor.close()
        conn.close()
        if orcamentos:
            return orcamentos
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()

def atualizar_orcamento(id_orcamento, numero, data, validade, cliente, documento, contato, vendedor, desconto_percent, desconto_reais, frete, imposto, pagamento, condicao, garantia, observacoes):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT id_orcamento FROM orcamento WHERE id_orcamento = %s
    """

    try:
        cursor.execute(sql, (id_orcamento,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        sql_update = """
        UPDATE orcamento
        SET numero = %s, data = %s, validade = %s, cliente = %s, documento = %s, contato = %s, vendedor = %s, desconto_percent = %s, desconto_reais = %s, frete = %s, imposto = %s, pagamento = %s, condicao = %s, garantia = %s, observacoes = %s
        WHERE id_orcamento = %s
        """

        cursor.execute(sql_update, (numero, data, validade, cliente, documento, contato, vendedor, desconto_percent, desconto_reais, frete, imposto, pagamento, condicao, garantia, observacoes, id_orcamento))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return False

def excluir_orcamento(id_orcamento):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT id_orcamento FROM orcamento WHERE id_orcamento = %s
    """

    try:
        cursor.execute(sql, (id_orcamento,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        sql_delete = """
        DELETE FROM orcamento WHERE id_orcamento = %s
        """

        cursor.execute(sql_delete, (id_orcamento,))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return False
