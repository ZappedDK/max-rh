import smtplib
import re
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

logger = logging.getLogger(__name__)

def parse_destinatarios(raw_destinatarios):
    """Extrai e valida lista de e-mails separados por vírgula, ponto e vírgula, espaço ou quebra de linha"""
    if not raw_destinatarios:
        return []
    pedacos = re.split(r'[,;\s\n\r]+', str(raw_destinatarios).strip())
    # Mantém apenas endereços que tenham formato básico válido com @ e .
    emails = []
    for p in pedacos:
        p_clean = p.strip()
        if p_clean and '@' in p_clean and '.' in p_clean:
            if p_clean not in emails:
                emails.append(p_clean)
    return emails

def get_config_dict():
    from models import Configuracao
    try:
        configs = Configuracao.query.all()
        return {c.chave: c.valor for c in configs}
    except Exception as e:
        logger.error(f"Erro ao carregar configurações de e-mail do banco: {e}")
        return {}

def criar_conexao_smtp(smtp_server, smtp_port, smtp_user, smtp_pass, criptografia='tls'):
    """
    Estabelece conexão com o servidor SMTP (Penso Mail, Gmail, Outlook, etc.)
    suportando portas 587 (TLS/STARTTLS), 465 (SSL) ou 25 (Normal).
    """
    porta = int(smtp_port) if smtp_port else 587
    cripto = str(criptografia or '').strip().lower()

    # Se a porta for 465 ou criptografia configurada como SSL
    if porta == 465 or cripto == 'ssl':
        server = smtplib.SMTP_SSL(smtp_server, porta, timeout=15)
    else:
        server = smtplib.SMTP(smtp_server, porta, timeout=15)
        # Se for porta 587 ou configurado TLS, ativa STARTTLS
        if cripto != 'nenhuma' and cripto != 'sem':
            try:
                server.ehlo()
                server.starttls()
                server.ehlo()
            except Exception as e:
                logger.warning(f"Aviso ao tentar STARTTLS na porta {porta}: {e}")

    # Autenticação
    if smtp_user and smtp_pass:
        server.login(smtp_user, smtp_pass)

    return server

def gerar_html_candidato(dados_candidato, app_url):
    """Gera o layout corporativo do e-mail de notificação com dados completos do candidato"""
    protocolo = dados_candidato.get('protocolo', 'N/D')
    nome = dados_candidato.get('nome_completo', 'Candidato')
    cargo = dados_candidato.get('cargo_pretendido', 'Não informado')
    loja = dados_candidato.get('loja_proxima', 'Geral')
    cpf = dados_candidato.get('cpf', '-')
    celular = dados_candidato.get('celular', '-')
    telefone_recado = dados_candidato.get('telefone_recado', '-')
    email = dados_candidato.get('email', 'Não informado')
    escolaridade = dados_candidato.get('grau_escolaridade', '-')
    cidade = dados_candidato.get('cidade', '-')
    bairro = dados_candidato.get('bairro', '-')
    disp_horario = dados_candidato.get('disponibilidade_horario', '-')
    pcd = dados_candidato.get('pcd', 'Não')
    data_cad = dados_candidato.get('data_cadastro', '')
    cid_id = dados_candidato.get('id', '')

    # Link do WhatsApp
    cel_digitos = re.sub(r'\D', '', str(celular))
    wa_link = f"https://wa.me/55{cel_digitos}" if len(cel_digitos) >= 10 else None

    link_painel = f"{app_url}/admin/candidato/{cid_id}" if cid_id else f"{app_url}/admin/candidatos"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; margin: 0; padding: 24px; color: #1e293b;">
      <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 620px; background-color: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
        
        <!-- Header Corporativo MAX -->
        <tr>
          <td style="background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%); padding: 26px 30px; text-align: center; color: #ffffff;">
            <h1 style="margin: 0; font-size: 24px; font-weight: 900; letter-spacing: 1.5px;">MAX SUPERMERCADOS</h1>
            <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Portal de Recrutamento & Seleção</p>
          </td>
        </tr>

        <!-- Faixa de Destaque da Notificação -->
        <tr>
          <td style="background-color: #eff6ff; padding: 14px 30px; border-bottom: 1px solid #dbeafe;">
            <table width="100%" border="0" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <span style="display: inline-block; background-color: #2563eb; color: #ffffff; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Nova Candidatura</span>
                  <span style="font-size: 13px; color: #475569; margin-left: 8px;">Protocolo: <strong>{protocolo}</strong></span>
                </td>
                <td align="right" style="font-size: 12px; color: #64748b;">
                  {data_cad}
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Conteúdo Principal -->
        <tr>
          <td style="padding: 28px 30px;">
            
            <h2 style="margin: 0 0 6px 0; font-size: 20px; color: #0f172a; font-weight: 800;">{nome}</h2>
            <p style="margin: 0 0 20px 0; font-size: 14px; color: #64748b;">Preencheu a ficha digital de cadastro para a equipe MAX.</p>

            <!-- Card Vaga Pretendida -->
            <div style="background-color: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 16px 18px; margin-bottom: 22px;">
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="font-size: 14px;">
                <tr>
                  <td style="padding: 4px 0; color: #64748b; width: 40%;"><strong>Cargo Pretendido:</strong></td>
                  <td style="padding: 4px 0; color: #0d47a1; font-weight: 700; font-size: 15px;">{cargo}</td>
                </tr>
                <tr>
                  <td style="padding: 4px 0; color: #64748b;"><strong>Loja / Unidade:</strong></td>
                  <td style="padding: 4px 0; color: #1e293b; font-weight: 600;">{loja}</td>
                </tr>
                <tr>
                  <td style="padding: 4px 0; color: #64748b;"><strong>Disponibilidade:</strong></td>
                  <td style="padding: 4px 0; color: #1e293b;">{disp_horario}</td>
                </tr>
                <tr>
                  <td style="padding: 4px 0; color: #64748b;"><strong>Vaga PCD:</strong></td>
                  <td style="padding: 4px 0; color: #1e293b;">{pcd}</td>
                </tr>
              </table>
            </div>

            <!-- Dados Pessoais e Contatos -->
            <h3 style="margin: 0 0 12px 0; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; font-weight: 700;">Dados de Contato & Localização</h3>
            <table width="100%" border="0" cellpadding="0" cellspacing="0" style="font-size: 14px; border-collapse: collapse; margin-bottom: 24px;">
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 8px 0; color: #64748b; width: 35%;">CPF:</td>
                <td style="padding: 8px 0; color: #1e293b; font-weight: 600;">{cpf}</td>
              </tr>
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 8px 0; color: #64748b;">Celular / WhatsApp:</td>
                <td style="padding: 8px 0; color: #1e293b; font-weight: 600;">
                  {celular}
                  {f' <a href="{wa_link}" target="_blank" style="color: #16a34a; text-decoration: none; font-size: 12px; margin-left: 8px; font-weight: bold;">(Abrir WhatsApp)</a>' if wa_link else ''}
                </td>
              </tr>
              {f'''<tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 8px 0; color: #64748b;">Tel. Recado:</td>
                <td style="padding: 8px 0; color: #1e293b;">{telefone_recado}</td>
              </tr>''' if telefone_recado and telefone_recado != '-' else ''}
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 8px 0; color: #64748b;">E-mail do Candidato:</td>
                <td style="padding: 8px 0; color: #2563eb;">{email}</td>
              </tr>
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 8px 0; color: #64748b;">Localização:</td>
                <td style="padding: 8px 0; color: #1e293b;">{bairro} - {cidade}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #64748b;">Escolaridade:</td>
                <td style="padding: 8px 0; color: #1e293b;">{escolaridade}</td>
              </tr>
            </table>

            <!-- Botão de Ação -->
            <div style="text-align: center; margin: 30px 0 10px 0;">
              <a href="{link_painel}" target="_blank" style="background-color: #0d47a1; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-size: 15px; font-weight: 700; display: inline-block; box-shadow: 0 4px 12px rgba(13, 71, 161, 0.3);">
                Ver Ficha Completa no Painel do RH &rarr;
              </a>
            </div>

          </td>
        </tr>

        <!-- Rodapé do E-mail -->
        <tr>
          <td style="background-color: #f8fafc; padding: 18px 30px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
            Este é um e-mail automático gerado pelo Sistema MAX RH.<br>
            Para gerenciar os e-mails destinatários, acesse Configurações no painel administrativo.
          </td>
        </tr>

      </table>
    </body>
    </html>
    """
    return html

def _enviar_email_thread(dados_candidato, app_url):
    """Envia o e-mail em background com tratamento completo de erros"""
    try:
        cfg = get_config_dict()
        ativo = cfg.get('email_ativo', '0') == '1'
        if not ativo:
            logger.info('Envio de e-mail desativado nas configurações do sistema.')
            return

        smtp_server = cfg.get('smtp_server', '').strip()
        smtp_port = cfg.get('smtp_port', '587').strip()
        smtp_user = cfg.get('smtp_user', '').strip()
        smtp_pass = cfg.get('smtp_password', '').strip()
        cripto = cfg.get('smtp_criptografia', 'tls').strip()
        remetente_nome = cfg.get('smtp_remetente_nome', 'MAX Supermercados RH').strip()
        destinatarios = parse_destinatarios(cfg.get('email_destinatario_rh', ''))

        if not smtp_server or not smtp_user or not destinatarios:
            logger.warning('Configurações de SMTP ou destinatários incompletos para envio.')
            return

        # Monta a mensagem
        protocolo = dados_candidato.get('protocolo', '')
        nome = dados_candidato.get('nome_completo', 'Novo Candidato')
        cargo = dados_candidato.get('cargo_pretendido', '')
        loja = dados_candidato.get('loja_proxima', '')

        assunto = f"[Novo Candidato] {nome} - {cargo} ({loja})"
        if protocolo:
            assunto += f" #{protocolo}"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From'] = formataddr((remetente_nome, smtp_user))
        msg['To'] = ', '.join(destinatarios)

        html = gerar_html_candidato(dados_candidato, app_url)
        msg.attach(MIMEText(html, 'html'))

        server = criar_conexao_smtp(smtp_server, smtp_port, smtp_user, smtp_pass, cripto)
        server.sendmail(smtp_user, destinatarios, msg.as_string())
        server.quit()

        logger.info(f"E-mail de nova candidatura ({protocolo}) enviado com sucesso para: {destinatarios}")
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de notificação de novo candidato: {e}")

def notificar_rh_novo_candidato(app, dados_candidato, app_url):
    """Dispara o envio de e-mail em background thread com o contexto do Flask"""
    def tarefa():
        with app.app_context():
            _enviar_email_thread(dados_candidato, app_url)
            
    thread = threading.Thread(target=tarefa)
    thread.daemon = True
    thread.start()

def testar_configuracao_smtp(cfg_teste=None):
    """
    Testa a conexão SMTP corporativa (Penso Mail, Gmail, Outlook, etc.)
    e envia um e-mail de teste aos destinatários configurados.
    Retorna: (sucesso: bool, mensagem_detalhada: str, destinatarios: list)
    """
    if cfg_teste is None:
        cfg = get_config_dict()
    else:
        cfg = cfg_teste

    smtp_server = str(cfg.get('smtp_server') or '').strip()
    smtp_port = str(cfg.get('smtp_port') or '587').strip()
    smtp_user = str(cfg.get('smtp_user') or '').strip()
    smtp_pass = str(cfg.get('smtp_password') or '').strip()
    cripto = str(cfg.get('smtp_criptografia') or 'tls').strip().lower()
    remetente_nome = str(cfg.get('smtp_remetente_nome') or 'MAX Supermercados RH').strip()
    destinatarios = parse_destinatarios(cfg.get('email_destinatario_rh', ''))

    if not smtp_server:
        return False, "O Servidor SMTP não foi informado (ex: smtp.penso.com.br).", []
    if not smtp_user:
        return False, "O Usuário/E-mail de envio (remetente) não foi informado.", []
    if not smtp_pass:
        return False, "A senha da conta de e-mail SMTP não foi informada.", []
    if not destinatarios:
        if smtp_user and '@' in smtp_user:
            destinatarios = [smtp_user]
        else:
            return False, "Nenhum e-mail de destino do RH válido foi informado. Cadastre ao menos um e-mail para receber os alertas.", []

    try:
        server = criar_conexao_smtp(smtp_server, smtp_port, smtp_user, smtp_pass, cripto)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[TESTE RH] Configuração de E-mail MAX RH Concluída com Sucesso!"
        msg['From'] = formataddr((remetente_nome, smtp_user))
        msg['To'] = ', '.join(destinatarios)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; background-color: #f1f5f9; padding: 24px; color: #1e293b;">
          <div style="max-width: 580px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,0.06);">
            <div style="background: #0d47a1; color: white; padding: 22px; text-align: center;">
              <h2 style="margin: 0; letter-spacing: 1px;">MAX SUPERMERCADOS</h2>
              <p style="margin: 4px 0 0; opacity: 0.9; font-size: 13px;">Teste de Integração de E-mail Corporativo</p>
            </div>
            <div style="padding: 24px;">
              <div style="background-color: #ecfdf5; border-left: 4px solid #10b981; padding: 14px 16px; border-radius: 6px; margin-bottom: 20px;">
                <strong style="color: #065f46; font-size: 15px; display: block; margin-bottom: 4px;">Servidor SMTP Conectado com Sucesso!</strong>
                <span style="color: #047857; font-size: 13px;">
                  Sua conta de e-mail (Penso Mail / Corporativo) está autenticada e pronta para notificar o RH a cada nova candidatura preenchida via QR Code ou link.
                </span>
              </div>

              <h4 style="margin: 0 0 10px 0; color: #334155; font-size: 14px;">Parâmetros Técnicos Utilizados no Teste:</h4>
              <table style="width: 100%; font-size: 13px; border-collapse: collapse; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                <tr>
                  <td style="padding: 8px 12px; color: #64748b; border-bottom: 1px solid #e2e8f0;">Servidor SMTP:</td>
                  <td style="padding: 8px 12px; font-weight: 600; border-bottom: 1px solid #e2e8f0;">{smtp_server}:{smtp_port}</td>
                </tr>
                <tr>
                  <td style="padding: 8px 12px; color: #64748b; border-bottom: 1px solid #e2e8f0;">Segurança / Criptografia:</td>
                  <td style="padding: 8px 12px; font-weight: 600; border-bottom: 1px solid #e2e8f0;">{cripto.upper()}</td>
                </tr>
                <tr>
                  <td style="padding: 8px 12px; color: #64748b; border-bottom: 1px solid #e2e8f0;">Conta de Disparo (Remetente):</td>
                  <td style="padding: 8px 12px; font-weight: 600; border-bottom: 1px solid #e2e8f0;">{smtp_user}</td>
                </tr>
                <tr>
                  <td style="padding: 8px 12px; color: #64748b;">Destinatários do RH (Recebedores):</td>
                  <td style="padding: 8px 12px; font-weight: 600; color: #2563eb;">{', '.join(destinatarios)}</td>
                </tr>
              </table>
            </div>
            <div style="background-color: #f8fafc; padding: 14px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
              MAX Supermercados • Sistema de Gestão de Colaboradores & RH
            </div>
          </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))
        server.sendmail(smtp_user, destinatarios, msg.as_string())
        server.quit()

        return True, f"Conexão realizada com sucesso! E-mail de teste enviado para: {', '.join(destinatarios)}", destinatarios

    except smtplib.SMTPAuthenticationError as e:
        return False, f"Falha de autenticação no servidor: Usuário ou senha incorretos para a conta {smtp_user}. Verifique se a senha foi digitada corretamente.", destinatarios
    except smtplib.SMTPConnectError as e:
        return False, f"Não foi possível conectar ao servidor SMTP '{smtp_server}' na porta {smtp_port}. Verifique o endereço do servidor e liberação de porta.", destinatarios
    except Exception as e:
        err_str = str(e)
        if "timed out" in err_str.lower() or "timeout" in err_str.lower():
            return False, f"Tempo limite de conexão esgotado ao tentar alcançar '{smtp_server}:{smtp_port}'. Verifique a porta e se o servidor exige SSL (porta 465) ou TLS (porta 587).", destinatarios
        return False, f"Erro ao testar envio de e-mail: {err_str}", destinatarios
