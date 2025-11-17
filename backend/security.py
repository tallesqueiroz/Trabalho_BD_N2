# security.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.orm import Session

# Importe seus modelos e schemas de usuário e o get_db
import models
import schemas
from database import get_db

# --- Configuração de Criptografia (Hashing) ---
# Usa bcrypt para as senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Configuração do JWT (Token) ---
# 
# ATENÇÃO: Mova esta chave para uma variável de ambiente!
# Ex: `export SECRET_KEY='seu_segredo_super_forte'`
# Nunca deixe a chave secreta no código.
# 
# Para gerar uma boa chave, use no terminal:
# openssl rand -hex 32
#
SECRET_KEY = "sua_chave_secreta_aqui" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token expira em 30 minutos

# Define o "esquema" de autenticação.
# tokenUrl="token" diz ao Swagger UI para usar o endpoint /token para autenticar
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- Funções Auxiliares de Senha ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro bate com o hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera um hash bcrypt para a senha."""
    return pwd_context.hash(password)


# --- Funções de Autenticação e Token ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo Access Token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Padrão de 30 minutos
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.Usuarios]:
    """
    Busca o usuário no banco e verifica sua senha.
    Retorna o objeto do usuário se for válido, ou None se não for.
    """
    # 1. Busca o usuário pelo username
    user = db.query(models.Usuarios).filter(models.Usuarios.username == username).first()
    if not user:
        return None # Usuário não encontrado
    
    # 2. Verifica se a senha bate com o hash salvo no banco
    if not verify_password(password, user.senha_hash):
        return None # Senha incorreta
        
    return user # Autenticação bem-sucedida

# --- Dependência Principal de Segurança ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuarios:
    """
    Dependência do FastAPI: decodifica o token, valida e retorna o usuário do banco.
    Qualquer endpoint que usar esta dependência estará protegido.
    """
    # Exceção padrão para erros de credencial
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decodifica o token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 2. Extrai o username (o "subject" ou 'sub' do token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # Valida se os dados do token estão no formato esperado
        token_data = schemas.TokenData(username=username)

    except (JWTError, ValidationError):
        # Se o token estiver expirado, malformado ou inválido
        raise credentials_exception
        
    # 3. Busca o usuário no banco de dados
    user = db.query(models.Usuarios).filter(models.Usuarios.username == token_data.username).first()
    
    if user is None:
        # Se o token for válido, mas o usuário não existir mais no DB
        raise credentials_exception
        
    # 4. Retorna o objeto do usuário (modelo SQLAlchemy)
    return user