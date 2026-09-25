"""
Script utilitário: limpa o banco e insere 3 candidatos de teste.
Execute com: python seed_test.py
"""
import os, sys

# Garante que usa o banco local (não o de produção)
from config import Config
db_url = os.getenv('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
print(f"[seed] Usando banco: {db_url}")

from app import app, db
from models import Candidato, ExperienciaProfissional, User
from utils import gerar_protocolo, formatar_cpf
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

CANDIDATOS = [
    {
        "nome_completo": "Wanderson Ferreira Dos Santos",
        "cpf": "529.982.247-25",
        "rg": "2456789",
        "orgao_expedicao": "SSP/GO",
        "data_nascimento": "15/03/1995",
        "idade": 31,
        "sexo": "Masculino",
        "estado_civil": "Solteiro",
        "possui_filhos": "Não",
        "qtd_filhos": 0,
        "nome_mae": "Maria Ferreira Dos Santos",
        "celular": "(62) 99123-4567",
        "telefone_recado": "(62) 3312-9900",
        "email": "wanderson.ferreira@email.com",
        "endereco": "Rua das Flores",
        "numero": "142",
        "complemento": "Ap 302",
        "bairro": "Setor Santa Rita",
        "cidade": "Goiânia",
        "uf": "GO",
        "cep": "74920-190",
        "cidade_nascimento": "GOIÂNIA",
        "estado_nascimento": "GO",
        "cargo_pretendido": "OPERADOR DE CAIXA",
        "pretensao_salarial": "R$ 1.800,00",
        "loja_proxima": "01 - Santa Rita",
        "grau_escolaridade": "Médio Completo",
        "camisa": "M",
        "calcado": "41",
        "saude_problema": "Não",
        "saude_medicacao": "Não",
        "saude_acidente": "Não",
        "saude_cirurgia": "Não",
        "saude_internado": "Não",
        "saude_pegar_peso": "Sim",
        "saude_coluna": "Não",
        "comp_conhecimento_vaga": "Indicação de amigo",
        "comp_tem_conhecido": "Não tenho",
        "comp_horas_extras": "Sim",
        "comp_finais_semana": "Sim",
        "comp_disponibilidade": "Todas",
        "status": "pendente",
        "experiencias": [
            {"nome_empresa": "Supermercado Central", "tempo_empresa": "2 anos", "funcao": "Operador de Caixa", "motivo_saida": "Oportunidade de crescimento"},
        ],
    },
    {
        "nome_completo": "Ana Paula Rodrigues Lima",
        "cpf": "074.481.906-87",
        "rg": "3567890",
        "orgao_expedicao": "SSP/GO",
        "data_nascimento": "22/07/1998",
        "idade": 28,
        "sexo": "Feminino",
        "estado_civil": "Casado",
        "companheiro": "Carlos Eduardo Lima",
        "possui_filhos": "Sim",
        "qtd_filhos": 1,
        "nome_mae": "Rosa Rodrigues Alves",
        "celular": "(62) 98765-3210",
        "telefone_recado": "(62) 3400-1122",
        "email": "ana.paula.lima@email.com",
        "endereco": "Avenida Mutirão",
        "numero": "800",
        "complemento": "Casa 3",
        "bairro": "Vila Mutirão",
        "cidade": "Goiânia",
        "uf": "GO",
        "cep": "74415-060",
        "cidade_nascimento": "APARECIDA DE GOIÂNIA",
        "estado_nascimento": "GO",
        "cargo_pretendido": "REPOSITOR DE MERCADORIA",
        "pretensao_salarial": "R$ 1.600,00",
        "loja_proxima": "02 - Vila Mutirão",
        "grau_escolaridade": "Fundamental Completo",
        "camisa": "P",
        "calcado": "36",
        "saude_problema": "Não",
        "saude_medicacao": "Sim: Metformina - diabetes controlada",
        "saude_acidente": "Não",
        "saude_cirurgia": "Não",
        "saude_internado": "Não",
        "saude_pegar_peso": "Sim",
        "saude_coluna": "Não",
        "comp_conhecimento_vaga": "Placa na frente da loja",
        "comp_tem_conhecido": "Parente",
        "comp_nome_conhecido": "Fernanda Lima",
        "comp_horas_extras": "Não",
        "comp_finais_semana": "Sim",
        "comp_disponibilidade": "Manhã",
        "status": "em_analise",
        "experiencias": [
            {"nome_empresa": "Panificadora Bom Pão", "tempo_empresa": "1 ano e 4 meses", "funcao": "Atendente", "motivo_saida": "Fechamento da empresa"},
            {"nome_empresa": "Loja Riachuelo", "tempo_empresa": "8 meses", "funcao": "Vendedora", "motivo_saida": "Salário baixo"},
        ],
    },
    {
        "nome_completo": "Fernando Henrique Costa Alves",
        "cpf": "003.445.982-06",
        "rg": "4123456",
        "orgao_expedicao": "SSP/GO",
        "data_nascimento": "05/11/1990",
        "idade": 35,
        "sexo": "Masculino",
        "estado_civil": "Solteiro",
        "possui_filhos": "Não",
        "qtd_filhos": 0,
        "nome_mae": "Conceição Alves Costa",
        "celular": "(62) 99555-7788",
        "telefone_recado": "(62) 3500-6643",
        "email": "fernando.costa@email.com",
        "endereco": "Rua Triunfo",
        "numero": "33",
        "complemento": "",
        "bairro": "Bairro Triunfo",
        "cidade": "Goiânia",
        "uf": "GO",
        "cep": "74660-080",
        "cidade_nascimento": "ANÁPOLIS",
        "estado_nascimento": "GO",
        "cargo_pretendido": "AUXILIAR DE LIMPEZA",
        "pretensao_salarial": "R$ 1.518,00",
        "loja_proxima": "07 - Triunfo",
        "grau_escolaridade": "Médio Incompleto",
        "camisa": "G",
        "calcado": "43",
        "saude_problema": "Não",
        "saude_medicacao": "Não",
        "saude_acidente": "Sim: Fratura no braço esquerdo em 2019 - já recuperado",
        "saude_cirurgia": "Não",
        "saude_internado": "Não",
        "saude_pegar_peso": "Sim",
        "saude_coluna": "Não",
        "comp_conhecimento_vaga": "Redes sociais",
        "comp_tem_conhecido": "Amigo",
        "comp_nome_conhecido": "João Batista Pereira",
        "comp_horas_extras": "Sim",
        "comp_finais_semana": "Sim",
        "comp_disponibilidade": "Todas",
        "status": "contratar",
        "experiencias": [
            {"nome_empresa": "Hipermercado Pão de Açúcar", "tempo_empresa": "3 anos", "funcao": "Auxiliar de Limpeza", "motivo_saida": "Redução de quadro"},
        ],
    },
]

with app.app_context():
    print("[seed] Limpando todas as tabelas...")
    db.drop_all()
    db.create_all()

    # Recriar usuário admin
    admin = User(
        username='admin',
        nome='Administrador',
        email='admin@maxsupermercados.com.br',
        role='admin',
        ativo=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.flush()
    print("[seed] Usuário admin recriado.")

    for dados in CANDIDATOS:
        proto = gerar_protocolo()

        c = Candidato(
            protocolo=proto,
            nome_completo=dados["nome_completo"],
            cpf=dados["cpf"],
            rg=dados["rg"],
            orgao_expedicao=dados["orgao_expedicao"],
            data_nascimento=dados["data_nascimento"],
            idade=dados["idade"],
            sexo=dados["sexo"],
            estado_civil=dados["estado_civil"],
            companheiro=dados.get("companheiro", ""),
            possui_filhos=dados["possui_filhos"],
            qtd_filhos=dados["qtd_filhos"],
            nome_mae=dados["nome_mae"],
            celular=dados["celular"],
            telefone_recado=dados["telefone_recado"],
            email=dados["email"],
            endereco=dados["endereco"],
            numero=dados["numero"],
            complemento=dados.get("complemento", ""),
            bairro=dados["bairro"],
            cidade=dados["cidade"],
            uf=dados["uf"],
            cep=dados["cep"],
            cidade_nascimento=dados["cidade_nascimento"],
            estado_nascimento=dados["estado_nascimento"],
            cargo_pretendido=dados["cargo_pretendido"],
            pretensao_salarial=dados["pretensao_salarial"],
            loja_proxima=dados["loja_proxima"],
            grau_escolaridade=dados["grau_escolaridade"],
            camisa=dados["camisa"],
            calcado=dados["calcado"],
            saude_problema=dados["saude_problema"],
            saude_medicacao=dados["saude_medicacao"],
            saude_acidente=dados["saude_acidente"],
            saude_cirurgia=dados["saude_cirurgia"],
            saude_internado=dados["saude_internado"],
            saude_pegar_peso=dados["saude_pegar_peso"],
            saude_coluna=dados["saude_coluna"],
            comp_conhecimento_vaga=dados["comp_conhecimento_vaga"],
            comp_tem_conhecido=dados["comp_tem_conhecido"],
            comp_nome_conhecido=dados.get("comp_nome_conhecido", ""),
            comp_horas_extras=dados["comp_horas_extras"],
            comp_finais_semana=dados["comp_finais_semana"],
            comp_disponibilidade=dados["comp_disponibilidade"],
            termo_aceite=True,
            assinatura_digital="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            ip_origem="127.0.0.1",
            status=dados["status"],
            data_cadastro=utc_now(),
        )
        db.session.add(c)
        db.session.flush()

        for i, exp in enumerate(dados.get("experiencias", []), start=1):
            e = ExperienciaProfissional(
                candidato_id=c.id,
                ordem=i,
                nome_empresa=exp["nome_empresa"],
                tempo_empresa=exp["tempo_empresa"],
                funcao=exp["funcao"],
                motivo_saida=exp["motivo_saida"],
            )
            db.session.add(e)

        print(f"  [+] {c.nome_completo} | {proto} | status: {c.status}")

    db.session.commit()
    print("\n[seed] Concluído! 3 candidatos inseridos com sucesso.")
