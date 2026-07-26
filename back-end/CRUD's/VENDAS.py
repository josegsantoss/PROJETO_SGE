from database.db import get_db_connection
from datetime import datetime
from typing import Any, Dict, cast


def realizar_venda_de_produtos(produtos, id_usuario):
    """
    Realiza venda de múltiplos produtos
    
    Args:
        produtos: Lista de dicts com {'id_produto': int, 'quantidade': int}
        id_usuario: ID do usuário realizando a venda
    
    Returns:
        dict com id_venda e valor_total, ou None se erro
    """
    
    if not produtos:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore
    
    valor_total = 0
    
    # Calcula o total dos produtos
    for item in produtos:
        cursor.execute(
            "SELECT preço_vrj FROM produto WHERE id_produto = %s",
            (item["id_produto"],)
        )
        produto = cursor.fetchone()
        
        if produto is None:
            conn.close()
            return None

        produto_dict = cast(Dict[str, Any], produto)
        preco = float(produto_dict.get("preço_vrj", 0))
        quantidade = item["quantidade"]
        valor_total += preco * quantidade
    
    # Insere a venda
    cursor.execute(
        """
        INSERT INTO vendas (id_usuario, valor_inicial, valor_final, data_venda)
        VALUES (%s, %s, %s, NOW())
        """,
        (id_usuario, valor_total, valor_total)
    )
    
    id_venda = cursor.lastrowid
    
    # Insere cada item da venda
    for item in produtos:
        cursor.execute(
            "SELECT preço_vrj FROM produto WHERE id_produto = %s",
            (item["id_produto"],)
        )
        produto = cursor.fetchone()
        
        if produto is None:
            conn.close()
            return None

        produto_dict = cast(Dict[str, Any], produto)
        preco = float(produto_dict.get("preço_vrj", 0))

        cursor.execute(
            """
            INSERT INTO itens_vendas (id_venda, id_produto, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s)
            """,
            (id_venda, item["id_produto"], item["quantidade"], preco)
        )
    
    conn.commit()
    conn.close()
    
    return {
        "id_venda": id_venda,
        "valor_total": valor_total
    }
