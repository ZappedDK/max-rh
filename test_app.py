import unittest
import io
from app import app, db
from models import User, Candidato, ExperienciaProfissional, Observacao
from utils import validar_cpf, formatar_cpf

class SistemaRecrutamentoTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    nome='Administrador Teste',
                    email='admin@teste.com',
                    role='admin',
                    ativo=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
            else:
                admin.set_password('admin123')
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_validador_cpf(self):
        self.assertFalse(validar_cpf('111.111.111-11'))
        self.assertFalse(validar_cpf('000.000.000-00'))
        self.assertFalse(validar_cpf('12345678900'))
        self.assertTrue(validar_cpf('52998224725'))

    def test_submissao_candidato_e_bloqueio_duplicidade(self):
        payload = {
            'cargo_pretendido': 'Operador de Caixa',
            'pretensao_salarial': 'R$ 1.800,00',
            'loja_proxima': '1 - Max - Setor Santa Rita',
            'nome_completo': 'João da Silva Sauro',
            'cpf': '529.982.247-25',
            'data_nascimento': '15/05/1995',
            'idade': '31',
            'sexo': 'Masculino',
            'cidade_nascimento': 'Goiânia',
            'estado_nascimento': 'GO',
            'celular': '(62) 98888-7777',
            'email': 'joao@teste.com',
            'cep': '74000-000',
            'endereco': 'Rua das Flores',
            'numero': '123',
            'bairro': 'Centro',
            'cidade': 'Goiânia',
            'uf': 'GO',
            'grau_escolaridade': 'Médio',
            'nivel_ensino': 'Concluído',
            'camisa': 'M',
            'calcado': '41',
            'exp_empresa_1': 'Supermercado Antigo',
            'exp_tempo_1': '2 anos',
            'exp_funcao_1': 'Repositor',
            'exp_motivo_1': 'Fim de contrato',
            'termo_aceite': '1',
            'assinatura_digital': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        }
        
        res = self.client.post('/candidatura', data=payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Ficha Enviada com Sucesso'.encode('utf-8'), res.data)
        
        with app.app_context():
            cand = Candidato.query.filter_by(cpf='529.982.247-25').first()
            self.assertIsNotNone(cand)
            self.assertEqual(cand.nome_completo, 'JOÃO DA SILVA SAURO')
            self.assertEqual(cand.loja_proxima, '1 - Max - Setor Santa Rita')
            self.assertEqual(len(cand.experiencias), 1)
            self.assertEqual(cand.experiencias[0].nome_empresa, 'Supermercado Antigo')
            
        res_dup = self.client.post('/candidatura', data=payload, follow_redirects=True)
        self.assertIn('permitida apenas uma ficha por candidato'.encode('utf-8'), res_dup.data)

    def test_fluxo_admin_e_upload_logo(self):
        # 1. Login
        res_login = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn('Banco de Candidatos'.encode('utf-8'), res_login.data)
        
        # 2. Testar upload de logo em PNG
        import os, shutil
        logo_path = os.path.join(app.root_path, 'static', 'img', 'logo.png')
        logo_backup = None
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_backup = f.read()

        try:
            logo_bytes = io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82')
            res_logo = self.client.post('/admin/configuracoes', data={
                'action': 'upload_logo',
                'logo_file': (logo_bytes, 'logo_teste.png')
            }, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(res_logo.status_code, 200)
            self.assertIn('Logotipo corporativo em PNG atualizado'.encode('utf-8'), res_logo.data)
        finally:
            if logo_backup is not None:
                with open(logo_path, 'wb') as f:
                    f.write(logo_backup)
        
        # 3. Criar candidato no banco
        with app.app_context():
            c = Candidato(
                protocolo='MAX-TESTE-01',
                cargo_pretendido='AÇOUGUEIRO',
                loja_proxima='2 - Max - Vila Mutirão',
                nome_completo='MARCOS PEREIRA',
                cpf='529.982.247-25',
                celular='(62) 99999-8888',
                data_nascimento='01/01/1990',
                status='pendente'
            )
            db.session.add(c)
            db.session.commit()
            cand_id = c.id
            
        res_status = self.client.post(f'/admin/candidato/{cand_id}/status', data={
            'status': 'contratar'
        }, follow_redirects=True)
        self.assertEqual(res_status.status_code, 200)
        
        res_obs = self.client.post(f'/admin/candidato/{cand_id}/observacao', data={
            'texto': 'Candidato excelente na entrevista técnica.'
        }, follow_redirects=True)
        self.assertEqual(res_obs.status_code, 200)
        self.assertIn('Candidato excelente na entrevista técnica.'.encode('utf-8'), res_obs.data)
        
        res_print = self.client.get(f'/admin/candidato/{cand_id}/imprimir')
        self.assertEqual(res_print.status_code, 200)
        self.assertIn('FICHA DE CADASTRO E SOLICITAÇÃO DE EMPREGO'.encode('utf-8'), res_print.data)

    def test_configuracoes_email_e_smtp(self):
        from email_service import parse_destinatarios, testar_configuracao_smtp
        
        # 1. Testar parser de múltiplos destinatários com vírgula, ponto e vírgula e espaços
        raw = "rh@max.com.br, selecao@max.com.br; gerente.rh@max.com.br   diretoria@max.com.br"
        dests = parse_destinatarios(raw)
        self.assertEqual(len(dests), 4)
        self.assertIn('rh@max.com.br', dests)
        self.assertIn('selecao@max.com.br', dests)
        self.assertIn('gerente.rh@max.com.br', dests)
        self.assertIn('diretoria@max.com.br', dests)

        # 2. Testar validação de dados incompletos
        sucesso, msg, _ = testar_configuracao_smtp({'smtp_server': '', 'smtp_user': '', 'smtp_password': ''})
        self.assertFalse(sucesso)
        self.assertIn('não foi informado', msg)

        # 3. Testar salvamento de configurações SMTP pelo admin
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        res = self.client.post('/admin/configuracoes', data={
            'action': 'salvar',
            'email_ativo': '1',
            'smtp_server': 'smtp.penso.com.br',
            'smtp_port': '587',
            'smtp_criptografia': 'tls',
            'smtp_remetente_nome': 'MAX Supermercados RH',
            'smtp_user': 'recrutamento@supermercadosmax.com.br',
            'smtp_password': 'senhatestepenso',
            'email_destinatario_rh': 'rh@supermercadosmax.com.br, selecao@supermercadosmax.com.br'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Configurações salvas com sucesso'.encode('utf-8'), res.data)

        # Verificar se os campos foram persistidos no banco
        from models import Configuracao
        with app.app_context():
            cfg_server = Configuracao.query.filter_by(chave='smtp_server').first()
            self.assertEqual(cfg_server.valor, 'smtp.penso.com.br')
            cfg_dest = Configuracao.query.filter_by(chave='email_destinatario_rh').first()
            self.assertIn('selecao@supermercadosmax.com.br', cfg_dest.valor)
            cfg_cripto = Configuracao.query.filter_by(chave='smtp_criptografia').first()
            self.assertEqual(cfg_cripto.valor, 'tls')

    def test_download_qrcode_e_imprimir_cartaz(self):
        # 1. Login admin
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        
        # 2. Testar download SVG
        res_svg = self.client.get('/admin/qrcode/download?formato=svg')
        self.assertEqual(res_svg.status_code, 200)
        self.assertEqual(res_svg.content_type, 'image/svg+xml; charset=utf-8')
        self.assertIn('attachment', res_svg.headers.get('Content-Disposition', ''))
        self.assertIn('qrcode_max_vagas.svg', res_svg.headers.get('Content-Disposition', ''))

        # 3. Testar download PNG
        res_png = self.client.get('/admin/qrcode/download?formato=png')
        self.assertEqual(res_png.status_code, 200)
        self.assertEqual(res_png.content_type, 'image/png')
        self.assertIn('attachment', res_png.headers.get('Content-Disposition', ''))
        self.assertIn('qrcode_max_vagas.png', res_png.headers.get('Content-Disposition', ''))

        # 4. Testar página dedicada de impressão de cartaz A4
        res_cartaz = self.client.get('/admin/cartaz/imprimir')
        self.assertEqual(res_cartaz.status_code, 200)
        self.assertIn('TRABALHE CONOSCO'.encode('utf-8'), res_cartaz.data)
        self.assertIn('MAX SUPERMERCADOS'.encode('utf-8'), res_cartaz.data)

if __name__ == '__main__':
    unittest.main()
