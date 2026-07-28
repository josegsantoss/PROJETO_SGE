from database.db import get_db_connection
from datetime import datetime
from typing import Any, Dict, List, Optional, cast


def obter_venda_por_id(id_venda) -> Optional[Dict[str, Any]]:
    """
    Obtém os detalhes de uma venda pelo ID
    
    Args:
        id_venda: ID da venda
    
    Returns:
        dict com os dados da venda, ou None se não encontrada
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore
    
    cursor.execute(
        """
        SELECT id_venda, id_usuario, valor_inicial, valor_final, data_venda
        FROM vendas
        WHERE id_venda = %s
        """,
        (id_venda,)
    )
    
    venda = cast(Optional[Dict[str, Any]], cursor.fetchone())
    conn.close()
    
    return venda


def obter_itens_venda(id_venda):
    """
    Obtém todos os itens de uma venda
    
    Args:
        id_venda: ID da venda
    
    Returns:
        Lista com os itens da venda
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore
    
    cursor.execute(
        """
        SELECT id_item, id_venda, id_produto, qnt_item
        FROM itens_vendas
        WHERE id_venda = %s
        """,
        (id_venda,)
    )
    
    itens = cast(List[Dict[str, Any]], cursor.fetchall())
    conn.close()
    
    return itens if itens else []


def cancelar_venda(id_venda):
    """
    Cancela uma venda, remove todos os seus itens e retorna ao estoque
    
    Args:
        id_venda: ID da venda a cancelar
    
    Returns:
        dict com status, mensagem e dados da venda cancelada, ou None se erro
    """
    
    # Verifica se a venda existe
    venda = obter_venda_por_id(id_venda)
    
    if venda is None:
        return {
            "sucesso": False,
            "mensagem": f"Venda com ID {id_venda} não encontrada"
        }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) #type: ignore
        
        # Obtém os itens antes de deletar
        itens = cast(List[Dict[str, Any]], obter_itens_venda(id_venda))
        
        # Retorna cada item ao estoque
        for item in itens:
            item_dict = cast(Dict[str, Any], item)
            cursor.execute(
                """
                UPDATE produto 
                SET `estoque-atual` = `estoque-atual` + %s
                WHERE id_produto = %s
                """,
                (item_dict["qnt_item"], item_dict["id_produto"])
            )
        
        # Deleta todos os itens da venda
        cursor.execute(
            "DELETE FROM itens_vendas WHERE id_venda = %s",
            (id_venda,)
        )
        
        itens_deletados = cursor.rowcount
        
        # Deleta a venda
        cursor.execute(
            "DELETE FROM vendas WHERE id_venda = %s",
            (id_venda,)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "sucesso": True,
            "mensagem": f"Venda {id_venda} cancelada com sucesso",
            "id_venda": id_venda,
            "itens_retornados": len(itens),
            "valor_venda": venda["valor_final"],
            "data_cancelamento": datetime.now().isoformat(),
            "detalhes_itens": [
                {
                    "id_produto": item["id_produto"],
                    "quantidade_retornada": item["qnt_item"]
                }
                for item in itens
            ]
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao cancelar venda: {str(e)}"
        }


def listar_vendas():
    """
    Lista todas as vendas do sistema
    
    Returns:
        Lista com todas as vendas
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore
    
    cursor.execute(
        """
        SELECT id_venda, id_usuario, valor_inicial, valor_final, data_venda
        FROM vendas
        ORDER BY data_venda DESC
        """
    )
    
    vendas = cursor.fetchall()
    conn.close()
    
    return vendas if vendas else []


def listar_vendas_por_usuario(id_usuario):
    """
    Lista todas as vendas de um usuário específico
    
    Args:
        id_usuario: ID do usuário
    
    Returns:
        Lista com as vendas do usuário
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) #type: ignore
    
    cursor.execute(
        """
        SELECT id_venda, id_usuario, valor_inicial, valor_final, data_venda
        FROM vendas
        WHERE id_usuario = %s
        ORDER BY data_venda DESC
        """,
        (id_usuario,)
    )
    
    vendas = cursor.fetchall()
    conn.close()
    
    return vendas if vendas else []
