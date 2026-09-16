import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import logging

logger = logging.getLogger(__name__)

def get_config_dict():
    from models import Configuracao
    configs = Configuracao.query.all()
    return {c.chave: c.valor for c in configs}

def _enviar_email_thread(dados_candidato, app_url):
    try:
        cfg = get_config_dict()
        ativo = cfg.get('email_ativo', '0') == '1'
        if not ativo:
            logger.info('Envio de e-mail desativado nas configuracoes.')
            return

        smtp_server = cfg.get('smtp_server')
        smtp_port = int(cfg.get('smtp_port', 587))
        smtp_user = cfg.get('smtp_user')
        smtp_pass = cfg.get('smtp_password')
        destinatarios = cfg.get('email_destinatario_rh', '').split(',')
        destinatarios = [d.strip() for d in destinatarios if d.strip()]

        if not smtp_server or not smtp_user or not destinatarios:
            logger.warning('Configurações de SMTP incompletas para envio.')
            return

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[Novo Candidato RH] {dados_candidato.get('nome_completo')} - {dados_candidato.get('cargo_pretendido')}"
        msg['From'] = smtp_user
        msg['To'] = ', '.join(destinatarios)

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f4f6f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: #0d47a1; color: white; padding: 20px; text-align: center;">
                    <h2 style="margin: 0; letter-spacing: 1px;">MAX SUPERMERCADOS</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Notificação de Nova Candidatura</p>
                </div>
                <div style="padding: 24px;">
                    <p style="font-size: 16px;">Uma nova ficha de cadastro foi preenchida pelo candidato via QR Code / Mobile.</p>
                    
                    <div style="background: #f8fafc; border-left: 4px solid #0d47a1; padding: 15px; margin: 20px 0;">
                        <p style="margin: 4px 0;"><strong>Protocolo:</strong> {dados_candidato.get('protocolo')}</p>
                        <p style="margin: 4px 0;"><strong>Nome Completo:</strong> {dados_candidato.get('nome_completo')}</p>
                        <p style="margin: 4px 0;"><strong>Cargo Pretendido:</strong> {dados_candidato.get('cargo_pretendido')}</p>
                        <p style="margin: 4px 0;"><strong>Loja Próxima / Unidade:</strong> {dados_candidato.get('loja_proxima')}</p>
                        <p style="margin: 4px 0;"><strong>CPF:</strong> {dados_candidato.get('cpf')}</p>
                        <p style="margin: 4px 0;"><strong>Celular:</strong> {dados_candidato.get('celular')}</p>
                        <p style="margin: 4px 0;"><strong>E-mail:</strong> {dados_candidato.get('email', 'Não informado')}</p>
                        <p style="margin: 4px 0;"><strong>Escolaridade:</strong> {dados_candidato.get('grau_escolaridade', '-')}</p>
                    </div>

                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{app_url}/admin/candidato/{dados_candidato.get('id')}" 
                           style="background: #0d47a1; color: white; text-decoration: none; padding: 12px 25px; border-radius: 5px; font-weight: bold; display: inline-block;">
                            Acessar Ficha Completa no Painel do RH
                        </a>
                    </div>
                </div>
                <div style="background: #eee; padding: 12px; text-align: center; font-size: 12px; color: #777;">
                    Este e-mail foi gerado automaticamente pelo Sistema de Recrutamento Max Supermercados.
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, destinatarios, msg.as_string())

        logger.info(f"E-mail de notificacao enviado com sucesso para {destinatarios}")
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de notificacao do RH: {e}")

def notificar_rh_novo_candidato(app, dados_candidato, app_url):
    """Dispara e-mail em background thread com contexto de aplicação"""
    def tarefa():
        with app.app_context():
            _enviar_email_thread(dados_candidato, app_url)
            
    thread = threading.Thread(target=tarefa)
    thread.daemon = True
    thread.start()
