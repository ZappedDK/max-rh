import re
import random
import string
from datetime import datetime, timezone
import segno

def limpar_apenas_digitos(valor):
    if not valor:
        return ''
    return re.sub(r'\D', '', str(valor))

def validar_cpf(cpf_str):
    """Valida matematicamente os dois dígitos verificadores do CPF"""
    cpf = limpar_apenas_digitos(cpf_str)
    if len(cpf) != 11:
        return False
    # CPFs inválidos conhecidos (todos dígitos iguais)
    if cpf == cpf[0] * 11:
        return False
    
    # 1º dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    d1 = 0 if resto == 10 else resto
    if d1 != int(cpf[9]):
        return False
        
    # 2º dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    d2 = 0 if resto == 10 else resto
    if d2 != int(cpf[10]):
        return False
        
    return True

def formatar_cpf(cpf_str):
    cpf = limpar_apenas_digitos(cpf_str)
    if len(cpf) == 11:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    return cpf_str

def gerar_protocolo():
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f'MAX-{codigo}'

def gerar_qrcode_svg_data(url):
    """Gera um QR Code em SVG e retorna string/data-uri para visualização no navegador"""
    qr = segno.make_qr(url)
    return qr.svg_data_uri(scale=5)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
