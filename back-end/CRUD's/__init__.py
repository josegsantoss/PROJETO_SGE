from CRUDS.CADASTRO_USUARIOS import *

from CRUDS.CADASTRO_PRODUTOS import *

from CRUDS.CLIENTES import * 

from CRUDS.CADASTRO_EQUIPAMENTOS import *

from CRUDS.ORCAMENTO import *

__all__ = [
    'verificarLogin',
    'cadastrarLogin',
    'listarLogin',
    'listar_categorias',
    'criar_categoria',
    'listar_produtos',
    'listar_produtos_por_categoria',
    'buscar_produto',
    'criar_produto',
    'atualizar_produto',
    'deletar_produto',
    'atualizar_estoque',
    'listar_clientes',
    'buscar_cliente',
    'buscar_cliente_por_cpf',
    'buscar_cliente_por_cnpj',
    'buscar_cliente_por_celular',
    'buscar_clientes_por_nome',
    'buscar_clientes_por_cep',
    'cadastrar_cliente',
    'atualizar_cliente',
    'deletar_cliente',
    'listar_equipamentos',
    'buscar_equipamento',
    'cadastrar_equipamento',
    'atualizar_equipamento',
    'excluir_equipamento',
    'listar_orcamentos',
    'buscar_orcamento',
    'buscar_orcamento_por_numero',
    'buscar_orcamento_por_cliente',
    'criar_orcamento',
    'atualizar_orcamento',
    'excluir_orcamento',
    'calcular_total_orcamento'
]
