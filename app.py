from flask import Flask, render_template, url_for, request, session, redirect, jsonify, make_response, flash
from functools import wraps
import random
import database
from database.connection import get_connection
from flask_apscheduler import APScheduler
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'uma_chave_super_secreta_e_dificil'

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# ===================== FUNÇÕES DE E-MAIL =====================

@scheduler.task('cron', id='enviar_relatorios', day_of_week='mon', hour=8, minute=0)
def job_enviar_relatorios():
    print("Iniciando verificação de envio de relatórios semanais...")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT email FROM usuario WHERE relatorios_ativos = 1")
        usuarios = cursor.fetchall()
        for usuario in usuarios:
            enviar_email_relatorio(usuario['email'])
    except Exception as e:
        print(f"Erro no agendamento: {e}")
    finally:
        cursor.close()
        conn.close()


def enviar_email_relatorio(destinatario):
    EMAIL_ADDRESS = 'tdsatcc@gmail.com'
    EMAIL_PASSWORD = 'fdvvxizyfqyersvg'

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        try:
            cursor.execute("""
                SELECT COUNT(*) as total_vendas, 
                       COALESCE(SUM(valor_total), 0) as faturamento
                FROM vendas 
                WHERE data_venda >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            """)
            vendas = cursor.fetchone() or {'total_vendas': 0, 'faturamento': 0}
        except:
            vendas = {'total_vendas': 0, 'faturamento': 0}

        try:
            cursor.execute("SELECT COUNT(*) as total_produtos FROM produtos")
            produtos = cursor.fetchone() or {'total_produtos': 0}
        except:
            produtos = {'total_produtos': 0}

        try:
            cursor.execute("""
                SELECT COUNT(*) as total_consertos 
                FROM conserto 
                WHERE data_fim >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND status = 'Finalizado'
            """)
            consertos = cursor.fetchone() or {'total_consertos': 0}
        except:
            consertos = {'total_consertos': 0}

        top_produtos_html = "<li>Nenhuma venda registrada esta semana.</li>"
        try:
            cursor.execute("""
                SELECT p.nome, SUM(iv.quantidade) as quantidade
                FROM item_venda iv
                JOIN produtos p ON iv.produto_id = p.id
                WHERE iv.data_venda >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY p.nome
                ORDER BY quantidade DESC
                LIMIT 5
            """)
            top_produtos = cursor.fetchall()
            if top_produtos:
                top_produtos_html = "".join([f"<li>{p['nome']} — {p['quantidade']} unidades</li>" for p in top_produtos])
        except:
            pass

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb; text-align: center;">📊 Relatório Semanal - TechManager</h2>
            <p style="text-align: center;">Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; border-left: 6px solid #2563eb;">
                <h3>Resumo Geral</h3>
                <ul style="list-style: none; padding: 0;">
                    <li>📈 <strong>Vendas Realizadas:</strong> {vendas['total_vendas']}</li>
                    <li>💰 <strong>Faturamento Total:</strong> R$ {float(vendas['faturamento']):.2f}</li>
                    <li>📦 <strong>Produtos Cadastrados:</strong> {produtos['total_produtos']}</li>
                    <li>🛠️ <strong>Consertos Finalizados:</strong> {consertos['total_consertos']}</li>
                </ul>
            </div>

            <div style="margin-top: 20px; background-color: #f8fafc; padding: 20px; border-radius: 12px;">
                <h3>🔥 Top 5 Produtos Mais Vendidos</h3>
                <ol style="padding-left: 20px;">
                    {top_produtos_html}
                </ol>
            </div>

            <p style="text-align: center; margin-top: 30px; color: #64748b; font-size: 14px;">
                Este é um relatório de teste.
            </p>
          </body>
        </html>
        """

        msg = EmailMessage()
        msg['Subject'] = '📊 Relatório Semanal - TechManager (Teste)'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = destinatario
        msg.add_alternative(html_content, subtype='html')

        print(f"Tentando enviar email para {destinatario}...")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print(f"✅ Email enviado com sucesso para: {destinatario}")

    except Exception as e:
        print(f"❌ ERRO AO ENVIAR EMAIL: {e}")
    finally:
        cursor.close()
        conn.close()


def enviar_email_codigo(destinatario, codigo):
    EMAIL_ADDRESS = 'tdsatcc@gmail.com'
    EMAIL_PASSWORD = 'fdvvxizyfqyersvg'

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Código de Verificação de Novo Dispositivo - SGE'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = destinatario
        msg.set_content(f"Olá!\n\nDetectamos um acesso ao SGE a partir de um novo dispositivo.\n\nSeu código de segurança é: {codigo}\n\nSe não foi você, altere sua senha imediatamente.")

        print(f"Tentando enviar código 2FA para {destinatario}...")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print(f"✅ Código 2FA enviado com sucesso para: {destinatario}")

    except Exception as e:
        print(f"❌ Erro ao enviar código 2FA: {e}")


# ===================== DECORADORES =====================

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_logado' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_logado' not in session or session.get('nivel') != 2:
            return redirect(url_for('menu'))
        return f(*args, **kwargs)
    return decorated_function


# ===================== ROTAS =====================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = database.verificarLogin(email, senha)

        if usuario is None:
            return render_template('login.html', erro="E-mail ou senha incorretos!")
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT two_factor_ativo FROM configuracoes WHERE id = 1")
            config = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if config and config.get('two_factor_ativo') == 1:
            dispositivo_salvo = request.cookies.get('dispositivo_confiavel')
            if dispositivo_salvo == usuario['email']:
                session['usuario_logado'] = usuario['email']
                session['cargo'] = usuario['cargo']
                session['nivel'] = usuario['nivel_de_permissao']
                return redirect(url_for('menu'))
            else:
                codigo_2fa = str(random.randint(100000, 999999))
                session['2fa_codigo'] = codigo_2fa
                session['temp_usuario'] = usuario 
                enviar_email_codigo(email, codigo_2fa)
                return redirect(url_for('verificar_2fa'))
        else:
            session['usuario_logado'] = usuario['email']
            session['cargo'] = usuario['cargo']
            session['nivel'] = usuario['nivel_de_permissao']
            return redirect(url_for('menu'))
    
    return render_template('login.html')


@app.route('/verificar_2fa', methods=['GET', 'POST'])
def verificar_2fa():
    if 'temp_usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form.get('codigo') == session.get('2fa_codigo'):
            usuario = session['temp_usuario']
            session['usuario_logado'] = usuario['email']
            session['cargo'] = usuario['cargo']
            session['nivel'] = usuario['nivel_de_permissao']
            session.pop('2fa_codigo', None)
            session.pop('temp_usuario', None)
            
            resposta = make_response(redirect(url_for('menu')))
            resposta.set_cookie('dispositivo_confiavel', usuario['email'], max_age=60*60*24*30)
            return resposta
        else:
            return render_template('verificar_2fa.html', erro="Código inválido.")
            
    return render_template('verificar_2fa.html')

@app.route('/menu')
@login_requerido
def menu():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        from datetime import datetime
        dia_atual = datetime.now().day

        # 1. SALDO TOTAL = Vendas + Orçamentos
        cursor.execute("SELECT COALESCE(SUM(total), 0) as saldo_vendas FROM vendas")
        saldo_vendas = float((cursor.fetchone() or {})['saldo_vendas'] or 0.0)
        
        cursor.execute("SELECT COALESCE(SUM(total_geral), 0) as saldo_orcamentos FROM orcamentos")
        saldo_orcamentos = float((cursor.fetchone() or {})['saldo_orcamentos'] or 0.0)
        
        saldo_atual = saldo_vendas + saldo_orcamentos

        # 2. RECEITA E VENDAS DE HOJE = Vendas de hoje + Orçamentos de hoje
        cursor.execute("SELECT COUNT(id_venda) as qtd_hoje, COALESCE(SUM(total), 0) as receita_hoje FROM vendas WHERE DATE(data_venda) = CURDATE()")
        res_vendas = cursor.fetchone() or {'qtd_hoje': 0, 'receita_hoje': 0}
        
        cursor.execute("SELECT COUNT(id) as qtd_hoje, COALESCE(SUM(total_geral), 0) as receita_hoje FROM orcamentos WHERE DATE(data_criacao) = CURDATE()")
        res_orcamentos = cursor.fetchone() or {'qtd_hoje': 0, 'receita_hoje': 0}
        
        receita_hoje = float(res_vendas['receita_hoje']) + float(res_orcamentos['receita_hoje'])
        vendas_hoje = int(res_vendas['qtd_hoje']) + int(res_orcamentos['qtd_hoje'])

        # 3. SERVIÇOS DE HOJE
        try:
            cursor.execute("SELECT COUNT(id) as qtd_servicos FROM conserto WHERE DATE(data_fim) = CURDATE() OR DATE(data_inicio) = CURDATE()")
            servicos_hoje = int((cursor.fetchone() or {})['qtd_servicos'] or 0)
        except:
            servicos_hoje = 0
            
        # 4. DESPESA DE HOJE
        try:
            cursor.execute("SELECT COALESCE(SUM(valor), 0) as despesa_hoje FROM despesas WHERE DATE(data_despesa) = CURDATE()")
            despesa_hoje = float((cursor.fetchone() or {})['despesa_hoje'] or 0.0)
        except:
            despesa_hoje = 0.0

        # 5. RECEITA DO MÊS = Vendas do mês + Orçamentos do mês
        cursor.execute("SELECT COALESCE(SUM(total), 0) as receita_mes FROM vendas WHERE MONTH(data_venda) = MONTH(CURDATE()) AND YEAR(data_venda) = YEAR(CURDATE())")
        rec_mes_vendas = float((cursor.fetchone() or {})['receita_mes'] or 0.0)
        
        cursor.execute("SELECT COALESCE(SUM(total_geral), 0) as receita_mes FROM orcamentos WHERE MONTH(data_criacao) = MONTH(CURDATE()) AND YEAR(data_criacao) = YEAR(CURDATE())")
        rec_mes_orcamentos = float((cursor.fetchone() or {})['receita_mes'] or 0.0)
        
        receita_mes = rec_mes_vendas + rec_mes_orcamentos

        # 6. DESPESA DO MÊS
        try:
            cursor.execute("SELECT COALESCE(SUM(valor), 0) as despesa_mes FROM despesas WHERE MONTH(data_despesa) = MONTH(CURDATE()) AND YEAR(data_despesa) = YEAR(CURDATE())")
            despesa_mes = float((cursor.fetchone() or {})['despesa_mes'] or 0.0)
        except:
            despesa_mes = 0.0

        # 7. META MENSAL
        try:
            cursor.execute("SELECT meta_mensal FROM configuracoes WHERE id = 1")
            meta = cursor.fetchone()
            meta_mensal = float(meta['meta_mensal']) if meta and meta.get('meta_mensal') else 30000.0
        except:
            meta_mensal = 30000.0

        # ======= CÁLCULOS DOS INDICADORES =======
        
        clientes_atendidos = vendas_hoje + servicos_hoje
        
        ticket_medio = (receita_hoje / vendas_hoje) if vendas_hoje > 0 else 0.0
        
        margem_lucro = ((receita_mes - despesa_mes) / receita_mes * 100) if receita_mes > 0 else 0.0
        
        projecao_mes = (receita_mes / dia_atual) * 30 if dia_atual > 0 else 0.0

        conversao = 100 if vendas_hoje > 0 else 0 
        
        def formata_br(valor):
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    except Exception as e:
        print(f"Erro ao buscar dados financeiros: {e}")
        saldo_atual = receita_hoje = despesa_hoje = vendas_hoje = servicos_hoje = clientes_atendidos = 0
        ticket_medio = margem_lucro = projecao_mes = conversao = meta_mensal = 0.0
        def formata_br(valor): return "0,00"
    finally:
        cursor.close()
        conn.close()

    return render_template('menu.html', 
                           saldo_numerico=saldo_atual,
                           meta_mensal=meta_mensal,
                           saldo_atual_fmt=formata_br(saldo_atual), 
                           receita_hoje_fmt=formata_br(receita_hoje),
                           despesa_hoje_fmt=formata_br(despesa_hoje),
                           vendas_hoje=vendas_hoje,
                           servicos_hoje=servicos_hoje,
                           clientes_atendidos=clientes_atendidos,
                           ticket_medio_fmt=formata_br(ticket_medio),
                           margem_lucro=int(margem_lucro),
                           projecao_mes_fmt=formata_br(projecao_mes),
                           conversao=conversao)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ===================== CONFIGURAÇÕES =====================

@app.route('/api/carregar-config', methods=['GET'])
@login_requerido
def carregar_config():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM configuracoes WHERE id = 1")
        config_global = cursor.fetchone() or {}

        cursor.execute("""
            SELECT notificacoes_ativas, relatorios_ativos, two_factor_ativo 
            FROM usuario WHERE email = %s
        """, (session['usuario_logado'],))
        user_prefs = cursor.fetchone() or {}

        return jsonify({**config_global, **user_prefs, 'status': 'sucesso'})
    finally:
        cursor.close()
        conn.close()


@app.route('/api/salvar-config', methods=['POST'])
@login_requerido
def salvar_config():
    dados = request.get_json()
    empresa = dados.get('empresa', {})
    preferencias = dados.get('preferencias', {})

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE configuracoes 
            SET empresa_nome=%s, empresa_cnpj=%s, empresa_telefone=%s,
                empresa_email=%s, empresa_endereco=%s
            WHERE id = 1
        ''', (empresa.get('nome',''), empresa.get('cnpj',''), 
              empresa.get('telefone',''), empresa.get('email',''), 
              empresa.get('endereco','')))

        cursor.execute('''
            UPDATE usuario 
            SET notificacoes_ativas=%s, relatorios_ativos=%s, two_factor_ativo=%s
            WHERE email = %s
        ''', (
            1 if preferencias.get('notificacoes') else 0,
            1 if preferencias.get('relatorios') else 0,
            1 if preferencias.get('twoFactor') else 0,
            session['usuario_logado']
        ))
        conn.commit()
        return jsonify({'status': 'sucesso', 'mensagem': 'Salvo com sucesso!'})
    finally:
        cursor.close()
        conn.close()

# ===================== API DE NOTIFICAÇÕES =====================

@app.route('/api/notificacoes', methods=['GET'])
@login_requerido
def api_notificacoes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM notificacoes WHERE lida = 0 ORDER BY id DESC")
        return jsonify(cursor.fetchall())
    except:
        return jsonify([])
    finally:
        cursor.close()
        conn.close()

@app.route('/api/marcar-lida/<int:id>', methods=['POST'])
@login_requerido
def marcar_lida(id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE notificacoes SET lida = 1 WHERE id = %s", (id,))
        conn.commit()
        return jsonify({'status': 'sucesso'})
    except:
        return jsonify({'status': 'erro'}), 500
    finally:
        cursor.close()
        conn.close()
        
# ===================== TESTE DE RELATÓRIO =====================

@app.route('/teste-relatorio', methods=['GET'])
@login_requerido
def teste_relatorio():
    email_destino = request.args.get('email', session.get('usuario_logado'))
    print(f"🚀 TESTE REAL: Enviando relatório para {email_destino}")
    enviar_email_relatorio(email_destino)
    
    return jsonify({
        "status": "sucesso",
        "mensagem": f"Relatório enviado para {email_destino}. Verifique sua caixa de entrada e spam."
    })


@app.route('/configuracao')
@login_requerido
def configuracao():
    return render_template('configuracao.html')


# ===================== OUTRAS ROTAS =====================

@app.route('/vendas', methods=['GET', 'POST'])
@login_requerido
def vendas():
    sucesso = None
    erro = None
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. PROCESSAR A VENDA (Quando o formulário é enviado)
    if request.method == 'POST':
        cliente_nome = request.form.get('cliente_nome', 'Cliente Não Identificado')
        cliente_documento = request.form.get('cliente_documento')
        cliente_telefone = request.form.get('cliente_telefone')
        cliente_email = request.form.get('cliente_email')
        cliente_endereco = request.form.get('cliente_endereco')
        forma_pagamento = request.form.get('forma_pagamento')

        # Conversão segura de valores
        desconto_str = request.form.get('desconto_reais')
        desconto = float(desconto_str) if desconto_str and desconto_str.strip() != '' else 0.0

        subtotal_str = request.form.get('subtotal_oculto')
        subtotal = float(subtotal_str) if subtotal_str and subtotal_str.strip() != '' else 0.0

        total_str = request.form.get('total_oculto')
        total = float(total_str) if total_str and total_str.strip() != '' else 0.0

        # Pegar os arrays de produtos gerados pelo JavaScript oculto
        produtos_ids = request.form.getlist('produto_id')
        quantidades = request.form.getlist('quantidade')
        precos = request.form.getlist('preco_produto')

        if not produtos_ids:
            erro = "O carrinho está vazio! Adicione produtos."
        else:
            try:
                id_usuario = session.get('usuario_id')

                # Salva os dados gerais na tabela VENDAS
                query_venda = """
                    INSERT INTO vendas 
                    (id_usuario, cliente_nome, cliente_documento, cliente_telefone, cliente_email, 
                     cliente_endereco, forma_pagamento, subtotal, desconto, total, data_venda) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(query_venda, (
                    id_usuario, cliente_nome, cliente_documento, cliente_telefone, cliente_email, 
                    cliente_endereco, forma_pagamento, subtotal, desconto, total
                ))
                id_venda = cursor.lastrowid

                # Salva cada produto na tabela ITENS_VENDA e atualiza o ESTOQUE
                query_item = """
                    INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario, total_item) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                query_estoque = "UPDATE produto SET estoque_atual = estoque_atual - %s WHERE id_produto = %s"

                for i in range(len(produtos_ids)):
                    p_id = produtos_ids[i]
                    qtd = int(quantidades[i])
                    preco_unit = float(precos[i])
                    total_item = preco_unit * qtd

                    cursor.execute(query_item, (id_venda, p_id, qtd, preco_unit, total_item))
                    cursor.execute(query_estoque, (qtd, p_id))

                conn.commit()
                sucesso = f"Venda #{id_venda} finalizada com sucesso!"
            except Exception as e:
                conn.rollback()
                erro = f"Erro ao finalizar venda: {e}"

    # 2. BUSCAR PRODUTOS (Para desenhar a vitrine de vendas)
    produtos_db = []
    try:
        # Adicionamos o WHERE estoque_atual > 0 para ocultar os zerados!
        cursor.execute("""
            SELECT 
                id_produto AS id, 
                id_produto AS codigo, 
                nome_produto AS nome, 
                categoria_produto AS categoria, 
                preço_vrj AS preco, 
                estoque_atual AS estoque 
            FROM produto
            WHERE estoque_atual > 0
        """)
        produtos_db = cursor.fetchall()
        for p in produtos_db:
            p['preco'] = float(p['preco'])
            p['icone'] = 'fa-box'
    except Exception as e:
        print("Erro ao buscar produtos:", e)

    # 3. BUSCAR HISTÓRICO (Para a tabela de baixo)
    historico = []
    try:
        cursor.execute("""
            SELECT v.id_venda, v.data_venda, v.cliente_nome, v.cliente_documento, v.total as valor_final,
                   (SELECT COALESCE(SUM(quantidade), 0) FROM itens_venda WHERE id_venda = v.id_venda) as total_itens
            FROM vendas v
            ORDER BY v.id_venda DESC
        """)
        historico = cursor.fetchall()
    except Exception as e:
        print("Erro ao buscar histórico:", e)

    cursor.close()
    conn.close()

    return render_template('vendas.html', produtos=produtos_db, historico=historico, sucesso=sucesso, erro=erro)

@app.route('/cadastro', methods=['GET', 'POST'])
@login_requerido
def cadastro():
    # Se o usuário enviou o formulário via POST
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf_cnpj = request.form.get('cpf')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        celular = request.form.get('celular')
        endereco = request.form.get('endereco')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        cep = request.form.get('cep')
        tipo = request.form.get('tipo')

        if not nome or not cpf_cnpj:
            flash("Nome e CPF/CNPJ são obrigatórios!", "erro")
        else:
            cpf = cpf_cnpj if tipo == 'Física' else None
            cnpj = cpf_cnpj if tipo == 'Jurídica' else None

            conn = get_connection()
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO cliente 
                    (nome_cliente, cpf, cnpj, email, telefone, celular, endereco, cidade, estado, cep, tipo) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (nome, cpf, cnpj, email, telefone, celular, endereco, cidade, estado, cep, tipo)
                cursor.execute(query, valores)
                conn.commit()
                flash("Cliente cadastrado com sucesso!", "sucesso")
            except Exception as e:
                conn.rollback()
                flash(f"Erro ao cadastrar cliente no banco de dados: {e}", "erro")
            finally:
                cursor.close()
                conn.close()

        # O REDIRECIONAMENTO É A CHAVE: Impede que o F5 duplique o cadastro
        return redirect(url_for('cadastro'))

    # Se for GET, busca os clientes normalmente para exibir na tabela
    clientes = []
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                id_cliente AS id, 
                nome_cliente AS nome, 
                COALESCE(cpf, cnpj) AS cpf, 
                email, 
                telefone, 
                celular, 
                endereco, 
                cidade, 
                estado, 
                cep, 
                tipo,
                data_cadastro
            FROM cliente 
            ORDER BY id_cliente DESC
        """)
        clientes = cursor.fetchall()

        for cliente in clientes:
            if cliente.get('data_cadastro'):
                if hasattr(cliente['data_cadastro'], 'strftime'):
                    cliente['data_cadastro'] = cliente['data_cadastro'].strftime('%d/%m/%Y %H:%M')

    except Exception as e:
        print(f"Erro ao buscar clientes: {e}")
    finally:
        cursor.close()
        conn.close()

    return render_template('cadastrocliente.html', clientes=clientes)

       #RECIBO DA VENDA
@app.route('/recibo/<int:id_venda>')
@login_requerido
def recibo(id_venda):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Busca os dados gerais da venda
        cursor.execute("SELECT * FROM vendas WHERE id_venda = %s", (id_venda,))
        venda = cursor.fetchone()

        if not venda:
            return "Venda não encontrada!", 404

        # 2. Busca os itens detalhados dessa venda, juntando com o nome do produto
        cursor.execute("""
            SELECT i.*, p.nome_produto 
            FROM itens_venda i
            JOIN produto p ON i.id_produto = p.id_produto
            WHERE i.id_venda = %s
        """, (id_venda,))
        itens = cursor.fetchall()

        return render_template('recibo.html', venda=venda, itens=itens)
    except Exception as e:
        return f"Erro ao gerar recibo: {e}"
    finally:
        cursor.close()
        conn.close()

@app.route('/extrato')
@login_requerido
def extrato():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    transacoes = []
    total_vendas = 0.0
    total_servicos = 0.0

    # 1. Busca as Vendas reais
    try:
        cursor.execute(
            "SELECT 'Vendas' AS categoria, CONCAT('Venda #', id_venda) AS descricao, total AS valor, DATE_FORMAT(data_venda, '%H:%i') AS hora, 'Concluído' AS status, data_venda AS data_ordenacao FROM vendas"
        )
        vendas = cursor.fetchall()
        for v in vendas:
            v['valor'] = float(v['valor']) if v['valor'] else 0.0
            total_vendas += v['valor']
            transacoes.append(v)
    except Exception as e:
        print(f"Erro ao buscar vendas: {e}")

    # 2. Busca os Consertos reais
    try:
        cursor.execute(
            "SELECT 'Serviços' AS categoria, CONCAT('Conserto: ', COALESCE(equipamento, 'Geral')) AS descricao, valor_estimado AS valor, DATE_FORMAT(data_entrada, '%H:%i') AS hora, COALESCE(status_servico, 'Pendente') AS status, data_entrada AS data_ordenacao FROM conserto"
        )
        consertos = cursor.fetchall()
        for c in consertos:
            c['valor'] = float(c['valor']) if c['valor'] else 0.0
            total_servicos += c['valor']
            transacoes.append(c)
    except Exception as e:
        print(f"Erro ao buscar consertos: {e}")

    # 3. Busca os ORÇAMENTOS reais (Lendo direto da tabela certa!)
    try:
        cursor.execute(
            "SELECT 'Orçamento' AS categoria, CONCAT('Orçamento: ', cliente_nome) AS descricao, total_geral AS valor, DATE_FORMAT(data_criacao, '%H:%i') AS hora, 'Salvo' AS status, data_criacao AS data_ordenacao FROM orcamentos"
        )
        orcamentos = cursor.fetchall()
        for o in orcamentos:
            o['valor'] = float(o['valor']) if o['valor'] else 0.0
            # Adicionamos ao total de vendas para que os orçamentos aumentem o seu saldo do dia
            total_vendas += o['valor']
            transacoes.append(o)
    except Exception as e:
        print(f"Erro ao buscar orçamentos para o extrato: {e}")

    # 4. Busca o histórico dos últimos 7 dias para o gráfico (Agora inclui os Orçamentos também!)
    labels_dias = []
    valores_dias = []
    try:
        cursor.execute("""
            SELECT DATE_FORMAT(data_transacao, '%d/%m') AS dia, SUM(valor) AS total_dia
            FROM (
                SELECT data_venda AS data_transacao, total AS valor FROM vendas WHERE data_venda >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                UNION ALL
                SELECT data_entrada AS data_transacao, valor_estimado AS valor FROM conserto WHERE data_entrada >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                UNION ALL
                SELECT data_criacao AS data_transacao, total_geral AS valor FROM orcamentos WHERE data_criacao >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            ) AS resumo
            GROUP BY DATE(data_transacao), dia
            ORDER BY DATE(data_transacao) ASC
        """)
        evolucao = cursor.fetchall()
        for item in evolucao:
            labels_dias.append(item['dia'])
            valores_dias.append(float(item['total_dia']) if item['total_dia'] else 0.0)
    except Exception as e:
        print(f"Erro ao buscar evolução diária: {e}")

    # Ordena as transações da tabela da mais recente para a mais antiga
    transacoes.sort(key=lambda x: str(x.get('data_ordenacao') or ''), reverse=True)

    cursor.close()
    conn.close()

    total_geral = total_vendas + total_servicos
    qtd_transacoes = len(transacoes)

    return render_template(
        'extrato.html', 
        transacoes=transacoes,
        total_vendas=total_vendas,
        total_servicos=total_servicos,
        total_geral=total_geral,
        qtd_transacoes=qtd_transacoes,
        labels_dias=labels_dias,
        valores_dias=valores_dias
    )


@app.route('/orcamento')
@login_requerido
def orcamento():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    produtos_estoque = []
    
    try:
        # Consulta atualizada com os nomes exatos da sua tabela!
        # Estou a puxar o 'preço_vrj' como o preço padrão do orçamento.
        cursor.execute("""
            SELECT 
                id_produto AS codigo, 
                nome_produto AS nome, 
                categoria_produto AS categoria, 
                preço_vrj AS preco 
            FROM produto
        """)
        resultados = cursor.fetchall()
        
        for p in resultados:
            # Converte os valores para o formato que o JavaScript consegue ler sem quebrar
            p['codigo'] = str(p['codigo'])
            p['preco'] = float(p['preco']) if p['preco'] else 0.0
            
            # Garante que a categoria não vai vazia
            if not p['categoria']:
                p['categoria'] = 'outros'
            else:
                p['categoria'] = str(p['categoria']).lower()
                
            produtos_estoque.append(p)
            
    except Exception as e:
        print(f"Erro ao buscar produtos do estoque para o orçamento: {e}")
    finally:
        cursor.close()
        conn.close()

    # Envia os produtos formatados para o HTML
    return render_template('orcamento.html', produtos=produtos_estoque)

@app.route('/api/salvar-orcamento', methods=['POST'])
@login_requerido
def salvar_orcamento():
    try:
        # Recolhe os dados com segurança (o "or 0.0" impede que o sistema quebre se o campo vier vazio)
        numero = request.form.get('numero', 'TECH-000000')
        data_orc = request.form.get('data') or None
        validade = request.form.get('validade') or None
        cliente = request.form.get('cliente', 'Cliente não informado')
        documento = request.form.get('documento', '')
        contato = request.form.get('contato', '')
        vendedor = request.form.get('vendedor', 'Não informado')
        
        subtotal = float(request.form.get('subtotal') or 0.0)
        desconto_percent = float(request.form.get('descontoPercent') or 0.0)
        desconto_reais = float(request.form.get('descontoReais') or 0.0)
        frete = float(request.form.get('frete') or 0.0)
        imposto_percent = float(request.form.get('impostoPercent') or 0.0)
        total_geral = float(request.form.get('totalGeral') or 0.0)
        
        metodo_pagamento = request.form.get('pagamento', 'PIX')
        condicao_pagamento = request.form.get('condicao', 'À vista')
        garantia = request.form.get('garantia', '90 dias')
        observacoes = request.form.get('obs', '')
        
        # Recebe a string de itens estruturada pelo JavaScript
        itens_json_str = request.form.get('itens_data', '[]')
        import json
        lista_itens = json.loads(itens_json_str)

        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Salva o cabeçalho na tabela 'orcamentos'
        cursor.execute("""
            INSERT INTO orcamentos (
                numero_orcamento, data_orcamento, validade, cliente_nome, 
                cliente_doc, cliente_contato, vendedor, subtotal, 
                desconto_percent, desconto_reais, frete, imposto_percent, 
                total_geral, metodo_pagamento, condicao_pagamento, garantia, observacoes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            numero, data_orc, validade, cliente, documento, contato, vendedor,
            subtotal, desconto_percent, desconto_reais, frete, imposto_percent,
            total_geral, metodo_pagamento, condicao_pagamento, garantia, observacoes
        ))
        
        orcamento_id = cursor.lastrowid # Pega o ID do orçamento recém-criado
        
        # 2. Salva cada item na tabela 'itens_orcamento'
        for item in lista_itens:
            codigo = item.get('codigo')
            nome = item.get('nome')
            categoria = item.get('categoria')
            qtd = int(item.get('quantidade') or 1)
            preco = float(item.get('preco') or 0.0)
            total_item = qtd * preco
            
            cursor.execute("""
                INSERT INTO itens_orcamento (
                    orcamento_id, codigo_produto, nome_produto, categoria, quantidade, preco_unitario, total_item
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (orcamento_id, codigo, nome, categoria, qtd, preco, total_item))

        # Confirma e GRAVA o orçamento no banco de dados IMEDIATAMENTE
        conn.commit()

        # 3. Tenta inserir na tabela 'vendas' (Separado para não cancelar o orçamento se der erro)
        try:
            cursor.execute(
                "INSERT INTO vendas (cliente, total, data_venda) VALUES (%s, %s, NOW())",
                (f"{cliente} (Orçamento #{numero})", total_geral)
            )
            conn.commit()
        except Exception as e_venda:
            print(f"⚠️ Orçamento SALVO, mas falhou ao enviar para a tabela vendas (Extrato): {e_venda}")

        cursor.close()
        conn.close()
        
        return redirect(url_for('extrato'))
        
    except Exception as e:
        print(f"❌ ERRO GRAVE AO SALVAR ORÇAMENTO NO BANCO: {e}")
        return redirect(url_for('orcamento'))

@app.route('/cadastro_produtos', methods=['GET', 'POST'])
@login_requerido
def cadastro_produtos():
    sucesso = None
    erro = None

    if request.method == 'POST':
        # 1. Pegando os dados do HTML pelos novos names
        nome_produto = request.form.get('nome_produto')
        categoria_produto = request.form.get('categoria_produto')
        marca = request.form.get('marca')
        preco_custo = request.form.get('preco_custo')
        preco_at = request.form.get('preco_at')
        preco_vrj = request.form.get('preco_vrj')
        estoque_atual = request.form.get('estoque_atual')

        if not nome_produto or not preco_vrj:
            erro = "Nome do produto e Preço de Varejo são obrigatórios!"
        else:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                # 2. Inserindo no banco de dados usando exatamente as colunas com "ç"
                query = """
                    INSERT INTO produto 
                    (nome_produto, categoria_produto, marca, preço_custo, preço_at, preço_vrj, estoque_atual) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    nome_produto, 
                    categoria_produto, 
                    marca, 
                    float(preco_custo) if preco_custo else 0.0,
                    float(preco_at) if preco_at else 0.0,
                    float(preco_vrj),
                    int(estoque_atual) if estoque_atual else 0
                )
                
                cursor.execute(query, valores)
                conn.commit()
                sucesso = "Produto cadastrado com sucesso!"
            except Exception as e:
                conn.rollback()
                erro = f"Erro ao cadastrar: {e}"
            finally:
                cursor.close()
                conn.close()

    # 3. Buscar os produtos no banco para exibir na tela
    produtos = []
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Usando 'AS' para renomear colunas e o JS continuar funcionando sozinho!
        # Estou usando o id_produto como o 'codigo' visual na tabela.
        cursor.execute("""
            SELECT 
                id_produto AS id, 
                id_produto AS codigo, 
                nome_produto AS nome, 
                categoria_produto AS categoria, 
                preço_vrj AS preco, 
                estoque_atual AS estoque 
            FROM produto 
            ORDER BY id_produto DESC
        """)
        produtos = cursor.fetchall()
        
        # Converte o float do MySQL para o JSON do JavaScript não dar erro
        for prod in produtos:
            prod['preco'] = float(prod['preco'])
            
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
    finally:
        cursor.close()
        conn.close()

    return render_template('cadastroproduto.html', produtos=produtos, sucesso=sucesso, erro=erro)

@app.route('/conserto', methods=['GET', 'POST'])
@login_requerido
def conserto():
    erro = None

    if request.method == 'POST':
        cliente = request.form.get('cliente')
        equipamento = request.form.get('equipamento')
        tipo = request.form.get('tipo')
        defeito = request.form.get('defeito')
        prioridade = request.form.get('prioridade')
        status = request.form.get('status')
        valor = request.form.get('valor')
        observacoes = request.form.get('observacoes')

        if not cliente or not equipamento or not defeito:
            erro = "Cliente, Equipamento e Defeito são obrigatórios!"
        else:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO conserto 
                    (nome_cliente, equipamento, tipo, defeito, prioridade, status_servico, valor_estimado, observacoes) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    cliente, 
                    equipamento, 
                    tipo, 
                    defeito, 
                    prioridade, 
                    status, 
                    float(valor) if valor else 0.0, 
                    observacoes
                )
                
                cursor.execute(query, valores)
                conn.commit()
                
                # O PULO DO GATO: Em vez de renderizar direto, enviamos uma mensagem flash e redirecionamos
                flash("Ordem de serviço cadastrada com sucesso!", "sucesso")
                return redirect(url_for('conserto'))
                
            except Exception as e:
                conn.rollback()
                erro = f"Erro ao cadastrar ordem: {e}"
            finally:
                cursor.close()
                conn.close()

    # Buscar todas as ordens de serviço para exibir na tela (Executado no GET)
    servicos = []
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                id_conserto AS id,
                nome_cliente AS cliente,
                equipamento,
                tipo,
                defeito,
                prioridade,
                status_servico AS status,
                valor_estimado AS valor,
                observacoes
            FROM conserto
            ORDER BY id_conserto DESC
        """)
        servicos = cursor.fetchall()
        
        for serv in servicos:
            serv['valor'] = float(serv['valor'])
            
    except Exception as e:
        print(f"Erro ao buscar consertos: {e}")
    finally:
        cursor.close()
        conn.close()

    return render_template('conserto.html', servicos=servicos, erro=erro)

@app.route('/suporte')
@login_requerido
def suporte():
    return render_template('suporte.html')

@app.route('/cadastro_funcionario')
@admin_requerido
def cadastro_funcionario():
    return render_template('cadastrofuncionario.html')

@app.route('/status-agendamento')
def status_agendamento():
    jobs = scheduler.get_jobs()
    return jsonify({
        "status": "ok",
        "jobs": [
            {
                "id": job.id,
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger)
            } for job in jobs
        ]
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
