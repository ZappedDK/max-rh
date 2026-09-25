from models import db, User, Configuracao, Cargo

def inicializar_banco(app):
    with app.app_context():
        db.create_all()
        
        # Verificar se já existe usuário admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                nome='Administrador do RH',
                email='rh@supermercadomax.com.br',
                role='admin',
                ativo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("[INIT] Usuário 'admin' criado com sucesso com a senha temporária 'admin123'.")
            
        # Configurações padrão de E-mail (Serviço SMTP / Rede MAX)
        configs_padrao = {
            'email_ativo': ('0', 'Habilitar envio de e-mail ao RH (1=Ativo, 0=Desativado)'),
            'smtp_server': ('suitesmtp.penso.com.br', 'Servidor de Disparo SMTP'),
            'smtp_port': ('587', 'Porta SMTP (587 TLS ou 465 SSL)'),
            'smtp_criptografia': ('tls', 'Criptografia SMTP (tls ou ssl)'),
            'smtp_remetente_nome': ('MAX Supermercados RH', 'Nome de exibição do remetente'),
            'smtp_user': ('recrutamento@redemaxsup.com.br', 'Usuário / E-mail corporativo de envio'),
            'smtp_password': ('', 'Senha da conta corporativa de e-mail'),
            'email_destinatario_rh': ('rh@redemaxsup.com.br', 'E-mails de destino do RH')
        }
        
        for chave, (valor, desc) in configs_padrao.items():
            if not Configuracao.query.filter_by(chave=chave).first():
                cfg = Configuracao(chave=chave, valor=valor, descricao=desc)
                db.session.add(cfg)
                
        # Semear cargos padrão se tabela vazia
        CARGOS_PADRAO = [
            ("AÇOUGUEIRO", "Responsável pelo corte, preparo e exposição de carnes bovinas, suínas e aves. Realiza o atendimento no balcão do açougue, orienta clientes sobre cortes e mantém a higiene e organização do setor."),
            ("ANALISTA COMERCIAL", "Analisa indicadores de vendas, acompanha o desempenho comercial das lojas e apoia estratégias de precificação e promoções. Elabora relatórios e apresenta resultados à gestão."),
            ("ANALISTA DE CADASTRO", "Responsável pelo cadastro e manutenção de fornecedores, produtos e clientes nos sistemas da empresa. Verifica dados, corrige inconsistências e garante a integridade das informações."),
            ("ANALISTA DE COMPRAS", "Realiza cotações, negocia condições com fornecedores e efetua a compra de mercadorias para as lojas. Acompanha pedidos, prazos de entrega e disponibilidade de produtos."),
            ("ANALISTA DE CREDITO", "Avalia solicitações de crédito de clientes e parceiros, analisa histórico financeiro e define limites. Monitora inadimplência e apoia a gestão de risco de crédito."),
            ("ANALISTA DE DEPARTAMENTO PESSOAL", "Executa rotinas de admissão, demissão, folha de pagamento, controle de ponto e benefícios. Garante o cumprimento da legislação trabalhista e suporte aos colaboradores."),
            ("ANALISTA DE ESTOQUE", "Monitora entradas e saídas de mercadorias, realiza inventários, identifica divergências e propõe melhorias nos processos de armazenagem e controle de estoque."),
            ("ANALISTA DE RECURSOS HUMANOS", "Apoia processos de recrutamento e seleção, treinamento, avaliação de desempenho e clima organizacional. Auxilia na gestão de talentos e desenvolvimento de pessoas."),
            ("ANALISTA FINANCEIRO", "Acompanha o fluxo de caixa, contas a pagar e receber, conciliações bancárias e relatórios financeiros. Apoia a tomada de decisões com base em indicadores e análises."),
            ("ANALISTA FISCAL", "Verifica e apura obrigações fiscais e tributárias, emite e valida notas fiscais, e garante o cumprimento das legislações tributárias aplicáveis ao negócio."),
            ("ASSISTENTE DE ESTOQUE", "Auxilia no controle de entrada e saída de mercadorias, organiza o estoque, separa produtos para as lojas e apoia na realização de inventários."),
            ("ASSISTENTE DE MONITORAMENTO", "Opera sistemas de câmeras e monitoramento das lojas. Registra ocorrências, alerta sobre situações suspeitas e apoia a equipe de prevenção de perdas."),
            ("ASSISTENTE FINANCEIRO", "Auxilia nas rotinas financeiras como lançamentos, conciliações, controle de pagamentos e recebimentos. Organiza documentos e apoia o analista financeiro."),
            ("ASSISTENTE FISCAL", "Apoia na conferência de notas fiscais, escrituração de documentos e geração de arquivos fiscais. Auxilia no cumprimento das obrigações acessórias."),
            ("ASSISTENTE JURIDICO", "Apoia a área jurídica na elaboração de documentos, acompanhamento de processos, pesquisa de legislação e organização de contratos e arquivos legais."),
            ("ASSISTENTE DE PREVENCAO DE PERDAS", "Auxilia na identificação e prevenção de perdas operacionais e de mercadorias. Apoia os processos de inventário e monitora indicadores de quebra."),
            ("ATENDENTE DE PADARIA", "Atende clientes no setor de padaria, organiza o espaço, embala produtos, repõe itens no balcão e garante a qualidade e apresentação dos produtos oferecidos."),
            ("AUXILIAR ADMINISTRATIVO", "Realiza atividades de apoio administrativo como digitação, arquivo de documentos, atendimento interno e organização de processos do setor."),
            ("AUXILIAR DE COMPRAS", "Apoia o processo de compras com cotações, organização de pedidos, controle de prazos e comunicação com fornecedores."),
            ("AUXILIAR DE CONFEITEIRO", "Auxilia na produção de bolos, doces, tortas e demais produtos de confeitaria, seguindo receitas e padrões de qualidade estabelecidos."),
            ("AUXILIAR DE DEPOSITO", "Realiza o recebimento, conferência, organização e movimentação de mercadorias no depósito da loja. Apoia nas atividades de carga e descarga."),
            ("AUXILIAR DE PADARIA", "Auxilia o padeiro na produção de pães e produtos de panificação, prepara insumos, limpa e organiza o ambiente de trabalho."),
            ("AUXILIAR FINANCEIRO", "Apoia as rotinas financeiras com lançamentos, controle de documentos e organização de processos. Auxilia na gestão de contas e relatórios básicos."),
            ("BALCONISTA DE AÇOUGUE", "Atende clientes no balcão do açougue, orienta sobre os cortes disponíveis, pesa e embala produtos, mantém a organização e higiene do setor."),
            ("CAPTADOR DE CLIENTE", "Aborda clientes nas proximidades das lojas, divulga promoções e produtos, incentiva o ingresso à loja e apoia ações de marketing e fidelização."),
            ("CONFEITEIRO", "Produz bolos, doces, tortas e sobremesas com criatividade e técnica. Garante a qualidade, apresentação e sabor dos produtos de confeitaria."),
            ("CONFERENTE", "Confere a entrada e saída de mercadorias, verifica quantidades e condições dos produtos recebidos e emite relatórios de divergências."),
            ("DESOSSADOR", "Especializado em separar a carne dos ossos de maneira eficiente, garantindo o aproveitamento máximo das peças e a qualidade dos cortes."),
            ("ENCARREGADO DE AÇOUGUE", "Gerencia as atividades do setor de açougue, coordena a equipe, controla estoque, garante a qualidade dos produtos e o atendimento ao cliente."),
            ("ENCARREGADO DE CHECK-OUT", "Supervisiona os caixas da loja, apoia operadores, resolve situações de atendimento, controla filas e garante a eficiência no check-out."),
            ("ENCARREGADO DE DEPOSITO", "Coordena as atividades do depósito, organiza o recebimento e armazenagem de mercadorias, gerencia a equipe e controla o fluxo de estoque."),
            ("ENCARREGADO DE FRIOS", "Responsável pela gestão do setor de frios, controla temperatura, validade e apresentação dos produtos, coordena a equipe e garante a qualidade."),
            ("ENCARREGADO DE HORTIFRUTI", "Gerencia o setor de frutas, verduras e legumes, controla qualidade, organiza exposição, coordena a equipe e garante o abastecimento adequado."),
            ("ENCARREGADO DE LOJA", "Apoia a gestão geral da loja, supervisiona setores, resolve problemas operacionais do dia a dia e garante o padrão de atendimento e organização."),
            ("ENCARREGADO DE PADARIA", "Coordena as atividades da padaria, escala a equipe, controla a produção, garante a qualidade dos produtos e o abastecimento do setor."),
            ("ENCARREGADO DE TESOURARIA", "Gerencia as atividades de tesouraria da loja, supervisiona o fechamento de caixa, controla sangrias, depósitos e a movimentação financeira."),
            ("ENCARREGADO FINANCEIRO", "Supervisiona as rotinas financeiras de uma unidade ou setor, controla fluxo de caixa, apoia conciliações e garante o cumprimento de metas."),
            ("ENCARREGADO DE PREVENCAO DE PERDAS", "Lidera a equipe de prevenção de perdas, coordena processos de inventário, monitora indicadores e implementa ações para redução de quebras e furtos."),
            ("ESTAGIARIO - ADMINISTRATIVO", "Apoia setores administrativos da empresa como RH, financeiro, compras ou marketing. Realiza atividades práticas vinculadas ao curso de graduação."),
            ("ESTAGIÁRIO - CAIXA", "Aprende e apoia as rotinas do setor de caixa, como atendimento ao cliente, operação de equipamentos e procedimentos de pagamento."),
            ("ESTAGIÁRIO - LOJA", "Apoia setores operacionais da loja como repositor, atendimento e organização, integrando teoria acadêmica à prática do varejo supermercadista."),
            ("FISCAL DE CAIXA", "Supervisiona os caixas em operação, autoriza descontos e cancelamentos, apoia operadores, garante a integridade dos valores e resolve ocorrências."),
            ("GERENTE DE LOJA", "Responsável pela gestão completa de uma unidade: pessoas, resultados, atendimento, abastecimento, prevenção de perdas e cumprimento de metas."),
            ("GERENTE DE MANUTENÇÃO", "Coordena a equipe de manutenção, gerencia contratos de serviços, planeja manutenções preventivas e corretivas e controla o patrimônio das lojas."),
            ("MOTORISTA", "Realiza transporte de mercadorias, colaboradores ou documentos com segurança. Cuida da conservação do veículo e cumpre prazos e rotas definidos."),
            ("MOTORISTA CARRETEIRO", "Conduz carretas para transporte de grandes volumes de mercadorias entre centros de distribuição e lojas, cumprindo normas de trânsito e segurança."),
            ("OPERADOR DE CAIXA", "Realiza o atendimento no caixa, processa pagamentos em dinheiro, cartão e outros meios, efetua sangrias e mantém a organização do posto de trabalho."),
            ("OPERADOR DE CARTAO", "Apoia nas operações com cartão de crédito e débito, administra máquinas POS, confere transações e oferece suporte ao cliente em dúvidas sobre pagamentos."),
            ("OPERADOR DE EMPILHADEIRA", "Opera empilhadeiras para movimentação de paletes e mercadorias no depósito, garantindo segurança, organização e agilidade nas operações."),
            ("PADEIRO", "Produz pães, roscas e produtos de panificação, controla fermentação e forno, garante sabor, textura e apresentação adequados aos padrões da loja."),
            ("PRECIFICADOR", "Realiza a etiquetagem e precificação de produtos nas gôndolas, confere preços no sistema, corrige divergências e mantém a loja organizada e sinalizada."),
            ("RECEPCIONISTA", "Recebe e direciona visitantes, atende telefone, organiza agendamentos e presta informações gerais. Representa a empresa no primeiro contato presencial."),
            ("REPOSITOR", "Abastece as gôndolas com mercadorias, organiza e rotaciona produtos, verifica validades e mantém a loja apresentável e com estoque adequado."),
            ("REPOSITOR DE FRIOS", "Responsável pelo abastecimento e organização do setor de frios, verifica validade e temperatura dos produtos, garantindo qualidade e apresentação."),
            ("REPOSITOR DE HORTIFRUTI", "Abastece e organiza o setor de frutas, verduras e legumes, seleciona produtos em bom estado, descarta avariados e mantém o setor sempre atrativo."),
            ("SUBGERENTE", "Apoia o gerente de loja na gestão das operações, lidera equipes na ausência do gerente, resolve ocorrências e garante o padrão de atendimento."),
            ("SUPERVISOR DE ESTOQUE", "Supervisiona o controle e a gestão do estoque das lojas, coordena inventários, analisa divergências e propõe melhorias nos processos de armazenagem."),
        ]
        
        if Cargo.query.count() == 0:
            for nome, desc in CARGOS_PADRAO:
                db.session.add(Cargo(nome=nome, descricao=desc, ativo=True))
            print(f"[INIT] {len(CARGOS_PADRAO)} cargos padrão inseridos.")
                
        db.session.commit()
        print("[INIT] Banco de dados e configurações iniciais verificados.")

if __name__ == '__main__':
    from flask import Flask
    from config import Config
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    inicializar_banco(app)
