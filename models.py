from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='recrutador') # 'admin' ou 'recrutador'
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=utc_now)
    
    observacoes = db.relationship('Observacao', backref='autor', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Candidato(db.Model):
    __tablename__ = 'candidatos'
    
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(30), unique=True, nullable=False, index=True)
    data_cadastro = db.Column(db.DateTime, default=utc_now, index=True)
    data_atualizacao = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    # 0. Cabeçalho / Vaga
    cargo_pretendido = db.Column(db.String(120), nullable=False)
    pretensao_salarial = db.Column(db.String(50))
    loja_proxima = db.Column(db.String(150), nullable=False)
    
    # 1. Dados Pessoais
    nome_completo = db.Column(db.String(200), nullable=False, index=True)
    idade = db.Column(db.Integer)
    sexo = db.Column(db.String(20))
    data_nascimento = db.Column(db.String(20), nullable=False)
    cidade_nascimento = db.Column(db.String(100))
    estado_nascimento = db.Column(db.String(10))
    
    # Endereço
    endereco = db.Column(db.String(200))
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))
    quadra = db.Column(db.String(50))
    lote = db.Column(db.String(50))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(5))
    cep = db.Column(db.String(15))
    
    # Contatos
    celular = db.Column(db.String(30), nullable=False)
    telefone_recado = db.Column(db.String(30))
    email = db.Column(db.String(150))
    
    # Filiação e Família
    nome_mae = db.Column(db.String(200))
    estado_civil = db.Column(db.String(50))
    companheiro = db.Column(db.String(200))
    profissao = db.Column(db.String(120))
    possui_filhos = db.Column(db.String(10), default='Não')
    qtd_filhos = db.Column(db.Integer, default=0)
    
    # 2. Documentos
    rg = db.Column(db.String(30))
    orgao_expedicao = db.Column(db.String(30))
    cpf = db.Column(db.String(20), unique=True, nullable=False, index=True)
    pis_pasep = db.Column(db.String(30))
    
    # 3. Nível de Instrução
    grau_escolaridade = db.Column(db.String(50)) # Fundamental, Médio, Superior, Pós Graduação
    nivel_ensino = db.Column(db.String(50)) # Concluído, Em Curso, Não Concluiu
    outros_cursos = db.Column(db.Text)
    
    # 4. Características
    cor_pele = db.Column(db.String(30)) # Branca, Parda, Negra, Indígena, Amarela, Outros
    deficiente_fisico = db.Column(db.String(10), default='Não') # Sim, Não
    deficiente_descricao = db.Column(db.String(255))
    
    # 5. Medidas
    camisa = db.Column(db.String(10)) # P, M, G, GG
    calcado = db.Column(db.String(10))
    
    # 7. Saúde
    saude_problema = db.Column(db.Text)
    saude_medicacao = db.Column(db.Text)
    saude_acidente = db.Column(db.Text)
    saude_cirurgia = db.Column(db.Text)
    saude_internado = db.Column(db.Text)
    saude_ultimo_medico = db.Column(db.Text)
    saude_pegar_peso = db.Column(db.String(10)) # Sim, Não
    saude_coluna = db.Column(db.String(10)) # Sim, Não
    
    # 8. Informações Complementares
    comp_conhecimento_vaga = db.Column(db.String(100))
    comp_tem_conhecido = db.Column(db.String(50)) # Não tenho, Parente, Amigo, Conhecido
    comp_nome_conhecido = db.Column(db.String(150))
    comp_horas_extras = db.Column(db.String(10)) # Sim, Não
    comp_finais_semana = db.Column(db.String(10)) # Sim, Não
    comp_disponibilidade = db.Column(db.String(150))
    
    # Termo e Assinatura
    termo_aceite = db.Column(db.Boolean, default=True)
    assinatura_digital = db.Column(db.Text) # Imagem base64 do canvas
    ip_origem = db.Column(db.String(50))
    
    # Gestão do RH
    status = db.Column(db.String(30), default='pendente', index=True) # pendente, em_analise, contratar, nao_contratar, banco_talentos
    
    # Relacionamentos
    experiencias = db.relationship('ExperienciaProfissional', backref='candidato', cascade='all, delete-orphan', lazy=True, order_by='ExperienciaProfissional.ordem')
    observacoes = db.relationship('Observacao', backref='candidato', cascade='all, delete-orphan', lazy=True, order_by='Observacao.data_criacao.desc()')
    anexos = db.relationship('Anexo', backref='candidato', cascade='all, delete-orphan', lazy=True, order_by='Anexo.data_criacao.desc()')

class ExperienciaProfissional(db.Model):
    __tablename__ = 'experiencias_profissionais'
    
    id = db.Column(db.Integer, primary_key=True)
    candidato_id = db.Column(db.Integer, db.ForeignKey('candidatos.id'), nullable=False)
    ordem = db.Column(db.Integer, default=1) # 1=Último, 2=Penúltimo, 3=Antepenúltimo
    nome_empresa = db.Column(db.String(150))
    tempo_empresa = db.Column(db.String(100))
    funcao = db.Column(db.String(120))
    motivo_saida = db.Column(db.String(255))

class Observacao(db.Model):
    __tablename__ = 'observacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    candidato_id = db.Column(db.Integer, db.ForeignKey('candidatos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=utc_now)

class Anexo(db.Model):
    __tablename__ = 'anexos'
    
    id = db.Column(db.Integer, primary_key=True)
    candidato_id = db.Column(db.Integer, db.ForeignKey('candidatos.id'), nullable=False)
    tipo = db.Column(db.String(50), default='documento') # foto_candidato, documento, outro
    nome_original = db.Column(db.String(255), nullable=False)
    nome_salvo = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=utc_now)

class Configuracao(db.Model):
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text)
    descricao = db.Column(db.String(255))
