# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. String de conexão (substitua com seus dados)
# Formato: "mysql://USUARIO:SENHA@HOST:PORTA/NOME_DB"
DATABASE_URL = "mysql://app_user:AppUser#2025@localhost:3306/biblioteca_db"

# 2. Engine de conexão
engine = create_engine(DATABASE_URL)

# 3. Fábrica de sessões (para interagir com o DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base para seus modelos (similar ao @Entity)
Base = declarative_base()

# Função para injetar a sessão de DB nas rotas da API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()