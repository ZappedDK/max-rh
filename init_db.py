from models import db, User, Configuracao

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
            
        # Configurações padrão de E-mail
        configs_padrao = {
            'email_ativo': ('0', 'Habilitar envio de e-mail ao RH (1=Ativo, 0=Desativado)'),
            'smtp_server': ('smtp.gmail.com', 'Servidor SMTP'),
            'smtp_port': ('587', 'Porta SMTP (587 TLS ou 465 SSL)'),
            'smtp_user': ('seuemail@gmail.com', 'Usuário / E-mail de envio'),
            'smtp_password': ('suasenhadeprograma', 'Senha de aplicativo do e-mail'),
            'email_destinatario_rh': ('rh@supermercadomax.com.br', 'E-mails de destino do RH (separados por vírgula)')
        }
        
        for chave, (valor, desc) in configs_padrao.items():
            if not Configuracao.query.filter_by(chave=chave).first():
                cfg = Configuracao(chave=chave, valor=valor, descricao=desc)
                db.session.add(cfg)
                
        db.session.commit()
        print("[INIT] Banco de dados e configurações iniciais verificados.")

if __name__ == '__main__':
    from flask import Flask
    from config import Config
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    inicializar_banco(app)
