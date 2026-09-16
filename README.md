# 🛒 Sistema de Recrutamento e Gestão de Candidatos (Max Supermercados)

Sistema completo desenvolvido em **Python (Flask + SQLAlchemy)** para substituir a ficha de emprego impressa em papel por um fluxo moderno, seguro e **Mobile-First** acessível via **QR Code**, integrado a um **Painel Administrativo de RH para Desktop**.

---

## 🚀 Principais Funcionalidades

### 📱 1. Formulário do Candidato (Mobile First / QR Code)
- **Acesso Neutro e Profissional:** Sem o nome da empresa no formulário público, conferindo uma apresentação clean e focada na solicitação de emprego ("Trabalhe Conosco").
- **Opção de Tema Escuro e Claro (Dark/Light Mode):** Botão no cabeçalho para alternar entre modo Claro e Escuro, salvando a preferência no navegador do candidato.
- **Divisão em 6 Etapas Inteligentes (Wizard):** Com barra de progresso visual para não cansar o candidato:
  1. **Vaga e Unidade:** Cargo pretendido, pretensão salarial e seleção entre as 10 unidades da rede Max.
  2. **Dados Pessoais & Endereço:** Nome completo, filiação, idade, sexo, telefones, estado civil, filhos e endereço com **autocompletar de CEP via ViaCEP**.
  3. **Documentos, Formação e Medidas:** RG, órgão expedidor, CPF, PIS/PASEP, escolaridade, cor da pele, PCD, tamanho da camisa para uniforme e calçado.
  4. **Experiências Anteriores:** Até 3 últimos empregos com tempo de permanência, cargo e motivo de saída.
  5. **Saúde e Rotina:** Questionário de 8 perguntas de saúde (incluindo se pode pegar peso e dores na coluna), disponibilidade de horário, horas extras e finais de semana.
  6. **Termo LGPD & Assinatura Digital:** Termo de consentimento e **área de desenho touch** para assinatura na tela do celular.
- **Formatações e Máscaras Rigorosas:**
  - **CPF Único:** Máscara `000.000.000-00`, validação matemática real dos dois dígitos verificadores e bloqueio de cadastro duplicado (apenas 1 ficha por CPF).
  - **Nome Completo e Nome da Mãe:** Bloqueio de números e caracteres especiais em tempo real (aceita apenas letras e acentos).
  - **Telefone / Celular:** Máscara dinâmica `(00) 00000-0000`.
  - **Data de Nascimento:** Máscara `DD/MM/AAAA` com cálculo instantâneo da idade.
  - **Pretensão Salarial:** Máscara de moeda `R$ 0.000,00`.

---

### 💻 2. Painel Administrativo do RH (Desktop / Web)
- **Upload de Logotipo em PNG de Alta Qualidade:**
  - Em `Configurações & Logo`, o administrador pode fazer upload do logotipo oficial da empresa em formato PNG transparente.
  - O logotipo é exibido automaticamente na barra superior do painel, na tela de login, nos cartazes de QR Code e no cabeçalho das fichas impressas.
- **Autenticação Segura:** Login com hash criptografado (acesso inicial: `admin` / `admin123`).
- **Níveis de Acesso e Gestão de Usuários:**
  - `Administrador`: Acesso geral, upload de logotipo, gestão de usuários e configurações de SMTP.
  - `Recrutador`: Visualização de candidatos, alteração de status, adição de observações e upload de anexos.
- **Dashboard com Métricas Rápidas:** Contadores de fichas Pendentes, Em Análise, Contratar, Não Contratar e Banco de Talentos.
- **Busca e Filtros:** Pesquisa instantânea por Nome, CPF, Protocolo ou Cargo, e filtros por Unidade e Status.
- **Ficha Completa do Candidato:** Visualização estruturada com botão de WhatsApp direto para contato rápido.
- **Ações de Recrutamento:**
  - Alteração de status: **✓ Contratar**, **✕ Não Contratar**, **⏳ Em Análise**, **⭐ Banco de Talentos**.
  - **Anotações Internas:** Registro de observações sobre entrevistas com autor e data/hora.
  - **Anexos e Documentos:** Upload e visualização de fotos 3x4 do candidato, fotos de documentos (RG/CNH) ou currículos.
- **Impressão da Ficha Física / Salvar em PDF:**
  - Formato tradicional de folha A4 com logotipo e a assinatura digital do candidato pronta para impressão ou arquivo físico.
- **Gerador de QR Code com Flyer para a Loja:**
  - Baixe o QR Code em alta definição (SVG) e imprima o cartaz de divulgação A4 pronto para colocar na recepção e balcões.

---

### 📧 3. Notificação por E-mail ao RH
- Configuração de servidor SMTP (Gmail, Outlook ou corporativo) no painel admin.
- Disparo em segundo plano (background thread) para que a submissão do candidato seja instantânea.
- E-mail com resumo e link direto para a ficha.

---

## 🗄️ Banco de Dados (PostgreSQL / MySQL / SQLite)

Suporte nativo a **PostgreSQL** e **MySQL** via SQLAlchemy no arquivo `.env`:

```env
# Exemplo PostgreSQL:
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/max_candidatos

# Exemplo MySQL:
# DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/max_candidatos?charset=utf8mb4

# Padrão offline:
DATABASE_URL=sqlite:///candidatos_max.db
```

---

## ⚙️ Como Executar

### No Windows (1 clique)
Dê um clique duplo em:
```
run.bat
```

### Via Terminal
```bash
python app.py
```

Acesso:
- **Formulário do Candidato (Mobile):** `http://localhost:5000/candidatura`
- **Painel do RH (Desktop):** `http://localhost:5000/admin/login`
  - **Usuário Padrão:** `admin`
  - **Senha Padrão:** `admin123`
