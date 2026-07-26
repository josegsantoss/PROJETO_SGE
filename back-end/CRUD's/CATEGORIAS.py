from CRUDS.connection import get_connection

def criar_produto(nome_produto, id_categoria, und_produto, preco_at, preco_vrj, preco_custo, marca=None, estoque_atual=0):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO produto (nome_produto, categoria_produto, marca, und_produto, preco_at, preco_vrj, preco_custo, `estoque-atual`)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(sql, (nome_produto, id_categoria, marca, und_produto, preco_at, preco_vrj, preco_custo, estoque_atual))
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return False

def listar_produtos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        p.id_produto,
        p.nome_produto,
        p.marca,
        p.und_produto,
        p.preco_at,
        p.preco_vrj,
        p.preco_custo,
        p.`estoque-atual`,
        c.id_categoria,
        c.nome_categoria
    FROM produto p
    LEFT JOIN categoria c ON p.categoria_produto = c.id_categoria
    ORDER BY p.nome_produto
    """

    try:
        cursor.execute(sql)
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        if produtos:
            return produtos
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()

def listar_produtos_por_categoria(id_categoria):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        p.id_produto,
        p.nome_produto,
        p.marca,
        p.und_produto,
        p.preco_at,
        p.preco_vrj,
        p.preco_custo,
        p.`estoque-atual`,
        c.id_categoria,
        c.nome_categoria
    FROM produto p
    LEFT JOIN categoria c ON p.categoria_produto = c.id_categoria
    WHERE p.categoria_produto = %s
    ORDER BY p.nome_produto
    """

    try:
        cursor.execute(sql, (id_categoria,))
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        if produtos:
            return produtos
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()

def buscar_produto(id_produto):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        p.id_produto,
        p.nome_produto,
        p.marca,
        p.und_produto,
        p.preco_at,
        p.preco_vrj,
        p.preco_custo,
        p.`estoque-atual`,
        c.id_categoria,
        c.nome_categoria
    FROM produto p
    LEFT JOIN categoria c ON p.categoria_produto = c.id_categoria
    WHERE p.id_produto = %s
    """

    try:
        cursor.execute(sql, (id_produto,))
        produto = cursor.fetchone()
        cursor.close()
        conn.close()
        if produto:
            return produto
        else:
            return None
        
    except Exception as e:
        print(e)
        conn.close()

def atualizar_produto(id_produto, nome_produto, id_categoria, und_produto, preco_at, preco_vrj, preco_custo, marca=None, estoque_atual=0):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT id_produto FROM produto WHERE id_produto = %s
    """

    try:
        cursor.execute(sql, (id_produto,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        sql_update = """
        UPDATE produto
        SET nome_produto = %s,
            categoria_produto = %s,
            marca = %s,
            und_produto = %s,
            preco_at = %s,
            preco_vrj = %s,
            preco_custo = %s,
            `estoque-atual` = %s
        WHERE id_produto = %s
        """

        cursor.execute(sql_update, (nome_produto, id_categoria, marca, und_produto, preco_at, preco_vrj, preco_custo, estoque_atual, id_produto))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return False

def deletar_produto(id_produto):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT id_produto FROM produto WHERE id_produto = %s
    """

    try:
        cursor.execute(sql, (id_produto,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        sql_delete = """
        DELETE FROM produto WHERE id_produto = %s
        """

        cursor.execute(sql_delete, (id_produto,))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return False

def atualizar_estoque(id_produto, quantidade):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT id_produto FROM produto WHERE id_produto = %s
    """

    try:
        cursor.execute(sql, (id_produto,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        sql_update = """
        UPDATE produto
        SET `estoque-atual` = `estoque-atual` + %s
        WHERE id_produto = %s
        """

        cursor.execute(sql_update, (quantidade, id_produto))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return False
