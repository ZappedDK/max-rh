import os
import uuid
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Candidato, ExperienciaProfissional, Observacao, Anexo, Configuracao
from init_db import inicializar_banco
from utils import validar_cpf, formatar_cpf, limpar_apenas_digitos, gerar_protocolo, gerar_qrcode_svg_data, allowed_file
from email_service import notificar_rh_novo_candidato

app = Flask(__name__)
app.config.from_object(Config)

# Garantir pastas de upload e imagens
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
IMG_FOLDER = os.path.join(app.root_path, 'static', 'img')
os.makedirs(IMG_FOLDER, exist_ok=True)

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Por favor, realize o login para acessar o painel administrativo.'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Inicializar o banco de dados na primeira execução
with app.app_context():
    inicializar_banco(app)

# Injetar variáveis globais para os templates
@app.context_processor
def inject_globals():
    logo_path = os.path.join(IMG_FOLDER, 'logo.png')
    tem_logo = os.path.exists(logo_path) and os.path.getsize(logo_path) > 500
    logo_version = int(os.path.getmtime(logo_path)) if tem_logo else 1
    return {
        'now': datetime.now(timezone.utc),
        'tem_logo': tem_logo,
        'logo_version': logo_version,
        'lojas_disponiveis': [
            '1 - Max - Santa Rita',
            '2 - Max - Vila Mutirão',
            '3 - Max - Residencial Rio Verde',
            '4 - Max - Independência Mansões',
            '5 - Max - Vila Brasília',
            '6 - Max - Tremendão',
            '7 - Max - Triunfo',
            '8 - Max - Tiradentes',
            '9 - Max - Cidade Jardim',
            '10 - Max - Jardim Nova Era'
        ]
    }

# ==========================================
# ROTAS DO CANDIDATO (MOBILE FIRST)
# ==========================================

@app.route('/')
def index():
    return redirect(url_for('candidatura'))

@app.route('/candidatura', methods=['GET', 'POST'])
def candidatura():
    if request.method == 'POST':
        cpf_raw = request.form.get('cpf', '').strip()
        cpf_formatado = formatar_cpf(cpf_raw)
        
        if not validar_cpf(cpf_raw):
            flash('O CPF informado é inválido. Por favor, revise os dígitos.', 'danger')
            return redirect(url_for('candidatura'))
            
        candidato_existente = Candidato.query.filter_by(cpf=cpf_formatado).first()
        if candidato_existente:
            flash(f'Já existe uma ficha cadastrada com o CPF {cpf_formatado} (Protocolo: {candidato_existente.protocolo}). É permitida apenas uma ficha por candidato.', 'warning')
            return redirect(url_for('candidatura'))
            
        try:
            protocolo = gerar_protocolo()
            idade_val = request.form.get('idade')
            idade = int(idade_val) if idade_val and idade_val.isdigit() else None
            
            qtd_filhos_val = request.form.get('qtd_filhos')
            qtd_filhos = int(qtd_filhos_val) if qtd_filhos_val and qtd_filhos_val.isdigit() else 0

            novo_candidato = Candidato(
                protocolo=protocolo,
                cargo_pretendido=request.form.get('cargo_pretendido', '').strip().upper(),
                pretensao_salarial=request.form.get('pretensao_salarial', '').strip(),
                loja_proxima=request.form.get('loja_proxima', '').strip(),
                
                # Dados Pessoais
                nome_completo=request.form.get('nome_completo', '').strip().upper(),
                idade=idade,
                sexo=request.form.get('sexo'),
                data_nascimento=request.form.get('data_nascimento', '').strip(),
                cidade_nascimento=request.form.get('cidade_nascimento', '').strip().upper(),
                estado_nascimento=request.form.get('estado_nascimento', '').strip().upper(),
                
                # Endereço
                endereco=request.form.get('endereco', '').strip(),
                numero=request.form.get('numero', '').strip(),
                complemento=request.form.get('complemento', '').strip(),
                quadra=request.form.get('quadra', '').strip(),
                lote=request.form.get('lote', '').strip(),
                bairro=request.form.get('bairro', '').strip(),
                cidade=request.form.get('cidade', '').strip(),
                uf=request.form.get('uf', '').strip().upper(),
                cep=request.form.get('cep', '').strip(),
                
                # Contatos
                celular=request.form.get('celular', '').strip(),
                telefone_recado=request.form.get('telefone_recado', '').strip(),
                email=request.form.get('email', '').strip().lower(),
                
                # Família
                nome_mae=request.form.get('nome_mae', '').strip().upper(),
                estado_civil=request.form.get('estado_civil'),
                companheiro=request.form.get('companheiro', '').strip().upper(),
                profissao=request.form.get('profissao', '').strip(),
                possui_filhos=request.form.get('possui_filhos', 'Não'),
                qtd_filhos=qtd_filhos,
                
                # Documentos
                rg=request.form.get('rg', '').strip(),
                orgao_expedicao=request.form.get('orgao_expedicao', '').strip().upper(),
                cpf=cpf_formatado,
                pis_pasep=request.form.get('pis_pasep', '').strip(),
                
                # Instrução e Características
                grau_escolaridade=request.form.get('grau_escolaridade'),
                nivel_ensino=request.form.get('nivel_ensino'),
                outros_cursos=request.form.get('outros_cursos', '').strip(),
                cor_pele=request.form.get('cor_pele'),
                deficiente_fisico=request.form.get('deficiente_fisico', 'Não'),
                deficiente_descricao=request.form.get('deficiente_descricao', '').strip(),
                
                # Medidas
                camisa=request.form.get('camisa'),
                calcado=request.form.get('calcado', '').strip(),
                
                # Saúde
                saude_problema=request.form.get('saude_problema', '').strip(),
                saude_medicacao=request.form.get('saude_medicacao', '').strip(),
                saude_acidente=request.form.get('saude_acidente', '').strip(),
                saude_cirurgia=request.form.get('saude_cirurgia', '').strip(),
                saude_internado=request.form.get('saude_internado', '').strip(),
                saude_ultimo_medico=request.form.get('saude_ultimo_medico', '').strip(),
                saude_pegar_peso=request.form.get('saude_pegar_peso', 'Sim'),
                saude_coluna=request.form.get('saude_coluna', 'Não'),
                
                # Informações Complementares
                comp_conhecimento_vaga=request.form.get('comp_conhecimento_vaga', '').strip(),
                comp_tem_conhecido=request.form.get('comp_tem_conhecido', 'Não tenho'),
                comp_nome_conhecido=request.form.get('comp_nome_conhecido', '').strip(),
                comp_horas_extras=request.form.get('comp_horas_extras', 'Sim'),
                comp_finais_semana=request.form.get('comp_finais_semana', 'Sim'),
                comp_disponibilidade=request.form.get('comp_disponibilidade', '').strip(),
                
                # Termo LGPD e Assinatura
                termo_aceite=True if request.form.get('termo_aceite') else False,
                assinatura_digital=request.form.get('assinatura_digital'),
                ip_origem=request.remote_addr,
                status='pendente'
            )
            
            db.session.add(novo_candidato)
            db.session.flush()
            
            for i in [1, 2, 3]:
                empresa = request.form.get(f'exp_empresa_{i}', '').strip()
                if empresa:
                    exp = ExperienciaProfissional(
                        candidato_id=novo_candidato.id,
                        ordem=i,
                        nome_empresa=empresa,
                        tempo_empresa=request.form.get(f'exp_tempo_{i}', '').strip(),
                        funcao=request.form.get(f'exp_funcao_{i}', '').strip(),
                        motivo_saida=request.form.get(f'exp_motivo_{i}', '').strip()
                    )
                    db.session.add(exp)
            
            db.session.commit()
            
            dados_email = {
                'id': novo_candidato.id,
                'protocolo': novo_candidato.protocolo,
                'nome_completo': novo_candidato.nome_completo,
                'cargo_pretendido': novo_candidato.cargo_pretendido,
                'loja_proxima': novo_candidato.loja_proxima,
                'cpf': novo_candidato.cpf,
                'celular': novo_candidato.celular,
                'email': novo_candidato.email,
                'grau_escolaridade': novo_candidato.grau_escolaridade
            }
            app_url = request.host_url.rstrip('/')
            notificar_rh_novo_candidato(app, dados_email, app_url)
            
            return redirect(url_for('candidatura_sucesso', protocolo=protocolo))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao salvar sua ficha: {str(e)}', 'danger')
            return redirect(url_for('candidatura'))

    return render_template('candidato/formulario.html')

@app.route('/candidatura/sucesso/<protocolo>')
def candidatura_sucesso(protocolo):
    candidato = Candidato.query.filter_by(protocolo=protocolo).first_or_404()
    return render_template('candidato/sucesso.html', candidato=candidato)

@app.route('/api/validar-cpf', methods=['POST'])
def api_validar_cpf():
    data = request.get_json() or {}
    cpf_raw = data.get('cpf', '')
    
    if not validar_cpf(cpf_raw):
        return jsonify({'valido': False, 'existe': False, 'mensagem': 'CPF com formato ou dígitos inválidos.'})
        
    cpf_fmt = formatar_cpf(cpf_raw)
    ja_existe = Candidato.query.filter_by(cpf=cpf_fmt).first()
    if ja_existe:
        return jsonify({'valido': True, 'existe': True, 'mensagem': f'Este CPF já possui cadastro (Protocolo: {ja_existe.protocolo}).'})
        
    return jsonify({'valido': True, 'existe': False, 'mensagem': 'CPF válido e liberado para cadastro.'})

# ==========================================
# ROTAS DO PAINEL RH (ADMIN DESKTOP)
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.ativo:
                flash('Este usuário está desativado pelo administrador.', 'danger')
                return render_template('admin/login.html')
                
            login_user(user)
            flash(f'Bem-vindo(a), {user.nome}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    status_filtro = request.args.get('status', '')
    loja_filtro = request.args.get('loja', '')
    busca = request.args.get('q', '').strip()
    
    query = Candidato.query
    
    if status_filtro:
        query = query.filter(Candidato.status == status_filtro)
    if loja_filtro:
        query = query.filter(Candidato.loja_proxima.ilike(f'%{loja_filtro}%'))
    if busca:
        busca_limpa = limpar_apenas_digitos(busca)
        if busca_limpa:
            query = query.filter(
                (Candidato.nome_completo.ilike(f'%{busca}%')) |
                (Candidato.cpf.ilike(f'%{busca_limpa}%')) |
                (Candidato.protocolo.ilike(f'%{busca}%')) |
                (Candidato.cargo_pretendido.ilike(f'%{busca}%'))
            )
        else:
            query = query.filter(
                (Candidato.nome_completo.ilike(f'%{busca}%')) |
                (Candidato.cargo_pretendido.ilike(f'%{busca}%')) |
                (Candidato.protocolo.ilike(f'%{busca}%'))
            )
            
    candidatos = query.order_by(Candidato.data_cadastro.desc()).all()
    
    metricas = {
        'total': Candidato.query.count(),
        'pendente': Candidato.query.filter_by(status='pendente').count(),
        'em_analise': Candidato.query.filter_by(status='em_analise').count(),
        'contratar': Candidato.query.filter_by(status='contratar').count(),
        'nao_contratar': Candidato.query.filter_by(status='nao_contratar').count(),
        'banco_talentos': Candidato.query.filter_by(status='banco_talentos').count(),
    }
    
    return render_template(
        'admin/dashboard.html',
        candidatos=candidatos,
        metricas=metricas,
        status_atual=status_filtro,
        loja_atual=loja_filtro,
        busca_atual=busca
    )

@app.route('/admin/candidato/<int:id>')
@login_required
def admin_candidato_detalhe(id):
    candidato = Candidato.query.get_or_404(id)
    return render_template('admin/detalhe.html', candidato=candidato)

@app.route('/admin/candidato/<int:id>/status', methods=['POST'])
@login_required
def admin_alterar_status(id):
    candidato = Candidato.query.get_or_404(id)
    novo_status = request.form.get('status')
    
    status_validos = ['pendente', 'em_analise', 'contratar', 'nao_contratar', 'banco_talentos']
    if novo_status in status_validos:
        candidato.status = novo_status
        candidato.data_atualizacao = datetime.now(timezone.utc)
        
        obs = Observacao(
            candidato_id=candidato.id,
            usuario_id=current_user.id,
            texto=f'Alterou o status para: {novo_status.replace("_", " ").upper()}'
        )
        db.session.add(obs)
        db.session.commit()
        flash(f'Status atualizado para: {novo_status.replace("_", " ").upper()}', 'success')
    else:
        flash('Status inválido.', 'danger')
        
    return redirect(url_for('admin_candidato_detalhe', id=id))

@app.route('/admin/candidato/<int:id>/observacao', methods=['POST'])
@login_required
def admin_adicionar_observacao(id):
    candidato = Candidato.query.get_or_404(id)
    texto = request.form.get('texto', '').strip()
    
    if texto:
        obs = Observacao(
            candidato_id=candidato.id,
            usuario_id=current_user.id,
            texto=texto
        )
        db.session.add(obs)
        db.session.commit()
        flash('Observação registrada com sucesso!', 'success')
        
    return redirect(url_for('admin_candidato_detalhe', id=id))

@app.route('/admin/candidato/<int:id>/anexo', methods=['POST'])
@login_required
def admin_upload_anexo(id):
    candidato = Candidato.query.get_or_404(id)
    tipo = request.form.get('tipo', 'documento')
    
    if 'arquivo' not in request.files:
        flash('Nenhum arquivo enviado.', 'warning')
        return redirect(url_for('admin_candidato_detalhe', id=id))
        
    file = request.files['arquivo']
    if file.filename == '':
        flash('Selecione um arquivo válido.', 'warning')
        return redirect(url_for('admin_candidato_detalhe', id=id))
        
    if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
        ext = file.filename.rsplit('.', 1)[1].lower()
        nome_original = secure_filename(file.filename)
        nome_salvo = f'{candidato.protocolo}_{uuid.uuid4().hex[:8]}.{ext}'
        
        caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_salvo)
        file.save(caminho_salvar)
        
        anexo = Anexo(
            candidato_id=candidato.id,
            tipo=tipo,
            nome_original=nome_original,
            nome_salvo=nome_salvo
        )
        db.session.add(anexo)
        db.session.commit()
        flash('Arquivo anexado com sucesso!', 'success')
    else:
        flash('Formato de arquivo não suportado. Use PNG, JPG, JPEG ou PDF.', 'danger')
        
    return redirect(url_for('admin_candidato_detalhe', id=id))

@app.route('/admin/candidato/<int:id>/imprimir')
@login_required
def admin_candidato_imprimir(id):
    candidato = Candidato.query.get_or_404(id)
    return render_template('admin/imprimir.html', candidato=candidato)

@app.route('/admin/qrcode')
@login_required
def admin_qrcode():
    url_candidatura = request.host_url.rstrip('/') + url_for('candidatura')
    qrcode_svg = gerar_qrcode_svg_data(url_candidatura)
    return render_template('admin/qrcode.html', url_candidatura=url_candidatura, qrcode_svg=qrcode_svg)

@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
def admin_usuarios():
    if current_user.role != 'admin':
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'criar':
            username = request.form.get('username', '').strip()
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role', 'recrutador')
            
            if User.query.filter_by(username=username).first():
                flash('Nome de usuário já cadastrado.', 'warning')
            elif User.query.filter_by(email=email).first():
                flash('E-mail já cadastrado para outro usuário.', 'warning')
            else:
                novo_u = User(username=username, nome=nome, email=email, role=role, ativo=True)
                novo_u.set_password(password)
                db.session.add(novo_u)
                db.session.commit()
                flash(f'Usuário {username} criado com sucesso!', 'success')
                
        elif action == 'toggle_status':
            uid = request.form.get('user_id')
            user_alvo = db.session.get(User, int(uid)) if uid else None
            if user_alvo and user_alvo.id != current_user.id:
                user_alvo.ativo = not user_alvo.ativo
                db.session.commit()
                flash(f'Status de {user_alvo.username} alterado para {"Ativo" if user_alvo.ativo else "Inativo"}.', 'info')
                
        elif action == 'alterar_senha':
            uid = request.form.get('user_id')
            nova_senha = request.form.get('nova_senha')
            user_alvo = db.session.get(User, int(uid)) if uid else None
            if user_alvo and nova_senha:
                user_alvo.set_password(nova_senha)
                db.session.commit()
                flash(f'Senha do usuário {user_alvo.username} atualizada.', 'success')

    # Filtros de busca de usuários
    q = request.args.get('q', '').strip()
    role_filtro = request.args.get('role', '').strip()
    status_filtro = request.args.get('status', '').strip()

    query = User.query
    if q:
        query = query.filter(
            (User.nome.ilike(f'%{q}%')) | 
            (User.username.ilike(f'%{q}%')) | 
            (User.email.ilike(f'%{q}%'))
        )
    if role_filtro:
        query = query.filter(User.role == role_filtro)
    if status_filtro:
        if status_filtro == 'ativo':
            query = query.filter(User.ativo == True)
        elif status_filtro == 'inativo':
            query = query.filter(User.ativo == False)

    usuarios = query.order_by(User.id.asc()).all()
    return render_template(
        'admin/usuarios.html', 
        usuarios=usuarios, 
        busca_atual=q, 
        role_atual=role_filtro, 
        status_atual=status_filtro
    )

@app.route('/admin/configuracoes', methods=['GET', 'POST'])
@login_required
def admin_configuracoes():
    if current_user.role != 'admin':
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Upload de Logo PNG
        if action == 'upload_logo':
            if 'logo_file' not in request.files:
                flash('Nenhum arquivo de logo selecionado.', 'warning')
            else:
                file = request.files['logo_file']
                if file.filename == '':
                    flash('Selecione uma imagem PNG válida.', 'warning')
                elif file and file.filename.lower().endswith('.png'):
                    caminho_logo = os.path.join(IMG_FOLDER, 'logo.png')
                    try:
                        from PIL import Image
                        img_uploaded = Image.open(file.stream).convert('RGBA')
                        bbox = img_uploaded.getbbox()
                        if bbox:
                            img_uploaded = img_uploaded.crop(bbox)
                        img_uploaded.save(caminho_logo, 'PNG', optimize=True)
                    except Exception:
                        file.seek(0)
                        file.save(caminho_logo)
                    flash('Logotipo corporativo em PNG atualizado com sucesso!', 'success')
                else:
                    flash('Formato inválido! Envie uma imagem com extensão .png para garantir transparência e nitidez.', 'danger')
            return redirect(url_for('admin_configuracoes'))
            
        elif action == 'remover_logo':
            caminho_logo = os.path.join(IMG_FOLDER, 'logo.png')
            if os.path.exists(caminho_logo):
                os.remove(caminho_logo)
                flash('Logotipo removido com sucesso.', 'info')
            return redirect(url_for('admin_configuracoes'))

        # Configurações de E-mail
        for chave in ['email_ativo', 'smtp_server', 'smtp_port', 'smtp_user', 'smtp_password', 'email_destinatario_rh']:
            valor = request.form.get(chave, '').strip()
            cfg = Configuracao.query.filter_by(chave=chave).first()
            if cfg:
                cfg.valor = valor
            else:
                cfg = Configuracao(chave=chave, valor=valor)
                db.session.add(cfg)
                
        db.session.commit()
        flash('Configurações salvas com sucesso!', 'success')
        
    configs_list = Configuracao.query.all()
    cfg_dict = {c.chave: c.valor for c in configs_list}
    return render_template('admin/configuracoes.html', configs=cfg_dict)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
