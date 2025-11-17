# Sistema de Gerenciamento de Biblioteca

API completa para gerenciamento de biblioteca com controle de empréstimos, reservas, acervo e usuários.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **MySQL 8.0+** - [Download](https://dev.mysql.com/downloads/mysql/)

## Instalação e Configuração

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/Trabalho_BD_N2.git
cd Trabalho_BD_N2
```

### 2. Configurar o MySQL

#### 2.1. Inicie o servidor MySQL

Certifique-se de que o MySQL está rodando em sua máquina. No Windows, você pode verificar nos Serviços do Windows ou executar:

```bash
mysql --version
```

#### 2.2. Execute o script SQL

Conecte-se ao MySQL e execute o script de criação do banco:

```bash
mysql -u root -p < biblioteca_db.sql
```

Ou, se preferir, abra o MySQL Workbench/phpMyAdmin e execute o conteúdo do arquivo `biblioteca_db.sql`.

> **Nota:** O script cria automaticamente:
> - Banco de dados `biblioteca_db`
> - Todas as tabelas necessárias
> - Triggers e procedures
> - Usuários: `app_user`, `bibliotecario`, `leitor`
> - Um usuário administrador padrão (username: `admin`, senha: `admin@biblioteca2025`)

### 3. Configurar o Backend (Python)

#### 3.1. Criar ambiente virtual Python

Na raiz do projeto, execute:

**Windows:**
```bash
python -m venv venv
```

#### 3.2. Ativar o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

#### 3.3. Instalar dependências Python

```bash
pip install -r backend/requirements.txt
```

#### 3.4. Configurar credenciais do banco

Abra o arquivo `backend/database.py` e ajuste a string de conexão se necessário:

```python
DATABASE_URL = "mysql://app_user:AppUser#2025@localhost:3306/biblioteca_db"
```

Formato: `mysql://USUARIO:SENHA@HOST:PORTA/NOME_DB`

### 4. Configurar o Frontend (Node.js)

#### 4.1. Navegar até a pasta do frontend

```bash
cd frontend
```

#### 4.2. Instalar dependências Node

```bash
npm install
```

## Executando a Aplicação

### Iniciar o Backend

1. **Certifique-se de estar na pasta `backend`:**

```bash
cd backend
```

2. **Com o ambiente virtual ativado, execute:**

**Windows:**
```bash
..\venv\Scripts\uvicorn.exe main:app --reload
```

O backend estará disponível em: `http://localhost:8000`

Documentação da API (Swagger): `http://localhost:8000/docs`

### Iniciar o Frontend

1. **Abra um NOVO terminal** (mantenha o backend rodando)

2. **Navegue até a pasta `frontend`:**

```bash
cd frontend
```

3. **Execute:**

```bash
npm start
```

O frontend será aberto automaticamente em: `http://localhost:3000`

## Credenciais Padrão

Após executar o script SQL, você pode fazer login com:

- **Usuário:** `admin`
- **Senha:** `admin@biblioteca2025`

## Estrutura do Projeto

```
Trabalho_BD_N2/
├── backend/
│   ├── database.py          # Configuração do banco
│   ├── main.py             # API FastAPI
│   ├── models.py           # Modelos SQLAlchemy
│   ├── schemas.py          # Schemas Pydantic
│   ├── security.py         # Autenticação JWT
│   ├── gerar_hash.py       # Utilitário para gerar hash de senha
│   └── requirements.txt    # Dependências Python
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
├── venv/                   # Ambiente virtual Python (criado)
├── biblioteca_db.sql       # Script do banco de dados
├── .gitignore
└── README.md
```

## Recursos Principais

- Gerenciamento de acervo (livros, autores, categorias, editoras)
- Controle de exemplares com código de barras
- Sistema de empréstimos com cálculo automático de multas
- Sistema de reservas com notificações
- Autenticação JWT com diferentes níveis de acesso
- Auditoria com logs de ações
- Triggers e procedures para integridade de dados
- Geração automática de IDs customizados (formato LIV-AAAA-NNNN)

```

## 📄 Licença

Este projeto foi desenvolvido como trabalho acadêmico.

---