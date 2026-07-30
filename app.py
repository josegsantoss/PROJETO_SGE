from flask import Flask, render_template, url_for, request, session, redirect, jsonify, make_response
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

        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) as saldo_total FROM vendas")
        saldo_atual = float((cursor.fetchone() or {})['saldo_total'] or 0.0)

        cursor.execute("SELECT COUNT(id) as qtd_hoje, COALESCE(SUM(valor_total), 0) as receita_hoje FROM vendas WHERE DATE(data_venda) = CURDATE()")
        res_vendas_hoje = cursor.fetchone() or {'qtd_hoje': 0, 'receita_hoje': 0}
        receita_hoje = float(res_vendas_hoje['receita_hoje'])
        vendas_hoje = int(res_vendas_hoje['qtd_hoje'])

        try:
            cursor.execute("SELECT COALESCE(SUM(valor), 0) as despesa_hoje FROM despesas WHERE DATE(data_despesa) = CURDATE()")
            despesa_hoje = float((cursor.fetchone() or {})['despesa_hoje'] or 0.0)
        except:
            despesa_hoje = 0.0

        try:
            cursor.execute("SELECT COUNT(id) as qtd_servicos FROM conserto WHERE DATE(data_fim) = CURDATE() OR DATE(data_inicio) = CURDATE()")
            servicos_hoje = int((cursor.fetchone() or {})['qtd_servicos'] or 0)
        except:
            servicos_hoje = 0

        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) as receita_mes FROM vendas WHERE MONTH(data_venda) = MONTH(CURDATE()) AND YEAR(data_venda) = YEAR(CURDATE())")
        receita_mes = float((cursor.fetchone() or {})['receita_mes'] or 0.0)

        try:
            cursor.execute("SELECT COALESCE(SUM(valor), 0) as despesa_mes FROM despesas WHERE MONTH(data_despesa) = MONTH(CURDATE()) AND YEAR(data_despesa) = YEAR(CURDATE())")
            despesa_mes = float((cursor.fetchone() or {})['despesa_mes'] or 0.0)
        except:
            despesa_mes = 0.0

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

@app.route('/vendas')
@login_requerido
def vendas():
    return render_template('vendas.html')

@app.route('/cadastro')
@login_requerido
def cadastro():
    return render_template('cadastrocliente.html')

@app.route('/extrato')
@login_requerido
def extrato():
    return render_template('extrato.html')

@app.route('/orcamento')
@login_requerido
def orcamento():
    return render_template('orcamento.html')

@app.route('/cadastro_produtos')
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
