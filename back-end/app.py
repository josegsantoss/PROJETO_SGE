from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from functools import wraps
from datetime import datetime
import random
import database

app = Flask(__name__)
app.secret_key = 'uma_chave_super_secreta_e_dificil'

# Lista para armazenar as vendas na memória enquanto não usa um BD real
vendas_registradas = []

# --- DECORADORES DE CONTROLE DE ACESSO ---

# 1. Verifica apenas se o usuário está logado (qualquer cargo)
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_logado' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 2. Verifica se o usuário logado é um Administrador
def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_logado' not in session:
            return redirect(url_for('login'))
        if session.get('nivel') != 2:
            # return "Erro: Acesso negado! Esta área é exclusiva para Administradores.", 403
            return redirect(url_for('menu'),)
        return f(*args, **kwargs)
    return decorated_function


# --- ROTAS DE PÁGINAS ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = database.verificarLogin(email, senha)

        # Validação do ADM
        if usuario == None:
            return render_template('login.html', erro="E-mail ou senha incorretos!")
        # Validação do Funcionário
        else:
            session['usuario_logado'] = usuario['email']
            session['cargo'] = usuario['cargo']
            session['nivel'] = usuario['nivel_de_permissao']
            return redirect(url_for('menu'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Limpa toda a sessão
    return redirect(url_for('login'))

@app.route('/menu')
@login_requerido
def menu():
    return render_template('menu.html')

@app.route('/vendas')
@login_requerido
def vendas():
    return render_template('vendas.html')

@app.route('/cadastro', methods=['GET', 'POST'])
@login_requerido
def cadastro():
    if request.method == 'POST':
        # A validação do CPF foi removida daqui. 
        # O sistema agora aceita o envio direto do formulário.
        return "Cliente cadastrado com sucesso!", 200
        
    return render_template('cadastrocliente.html')

@app.route('/extrato')
@login_requerido
def extrato():
    return render_template('extrato.html')

@app.route('/orcamento')
@login_requerido
def orcamento():
    return render_template('orcamento.html')

@app.route('/cadastroproduto')
@login_requerido
def cadastro_produtos():
    return render_template('cadastroproduto.html')

@app.route('/conserto')
@login_requerido
def conserto():
    return render_template('conserto.html')

@app.route('/suporte')
@login_requerido
def suporte():
    return render_template('suporte.html')

@app.route('/cadastrofuncionario')
@admin_requerido
def cadastro_funcionario():
    return render_template('cadastrofuncionario.html')

@app.route('/configuracao')
@login_requerido
def configuracao():
    return render_template('configuracao.html')


# --- ROTAS DE API (USADAS PELO JAVASCRIPT EM VENDAS.HTML) ---

@app.route('/api/dashboard', methods=['GET'])
@login_requerido
def api_dashboard():
    # Retorna o email do usuário logado para aparecer no topo da tela
    usuario = session.get('usuario_logado', 'Usuário')
    return jsonify({"usuario_email": usuario})

@app.route('/api/clientes', methods=['GET'])
@login_requerido
def api_clientes():
    # Lista de clientes fictícios para a barra de pesquisa
    clientes_mock = [
        {"nome_cliente": "João Silva", "documento": "111.111.111-11"},
        {"nome_cliente": "Maria Oliveira", "documento": "222.222.222-22"},
        {"nome_cliente": "Empresa Tech LTDA", "documento": "33.333.333/0001-33"}
    ]
    return jsonify(clientes_mock)

@app.route('/api/vendas', methods=['GET', 'POST'])
@login_requerido
def api_vendas():
    if request.method == 'POST':
        # Recebe os dados do carrinho via JSON
        dados_venda = request.get_json()
        
        # Gera ID de venda e anota a data
        id_venda = random.randint(1000, 9999)
        dados_venda['id_venda'] = id_venda
        dados_venda['data_venda'] = datetime.now().isoformat()
        
        # Soma o total de itens comprados
        total_itens = sum(item['quantidade'] for item in dados_venda.get('itens', []))
        dados_venda['total_itens'] = total_itens
        
        # Salva a venda na lista temporária
        vendas_registradas.append(dados_venda)
        
        return jsonify({
            "mensagem": "Venda registrada com sucesso",
            "id_venda": id_venda
        }), 201

    else:
        # Quando o JS pedir (GET), envia o histórico formatado
        historico_formatado = []
        for v in vendas_registradas:
            historico_formatado.append({
                "id_venda": v.get("id_venda"),
                "data_venda": v.get("data_venda"),
                "cliente_nome": v.get("cliente_nome"),
                "cliente_documento": v.get("cliente_documento"),
                "total_itens": v.get("total_itens"),
                "valor_final": v.get("total")
            })
            
        # O [::-1] inverte a lista para mostrar a venda mais recente no topo
        return jsonify(historico_formatado[::-1])

if __name__ == '__main__':
    app.run(debug=True)
