# schemas.py
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime, date
# Importa as Enumerações do models.py para usar nos schemas
from models import StatusExemplarEnum, StatusReservaEnum

# --- Schemas Base e de Leitura Simples (para nesting) ---

class AutorBase(BaseModel):
    nome: str
    sobrenome: Optional[str] = None

class AutorCreate(AutorBase):
    pass

class Autor(AutorBase):
    id_autor: int
    model_config = ConfigDict(from_attributes=True)

class CategoriaBase(BaseModel):
    nome: str

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id_categoria: int
    model_config = ConfigDict(from_attributes=True)

class EditoraBase(BaseModel):
    nome: str

class EditoraCreate(EditoraBase):
    pass

class Editora(EditoraBase):
    id_editora: int
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Livro (Mais complexos) ---

class LivroBase(BaseModel):
    titulo: str
    isbn: Optional[str] = None
    ano_publicacao: Optional[int] = None
    id_editora: Optional[int] = None

class LivroCreate(LivroBase):
    # O id_livro NÃO é incluído aqui, pois sua trigger no DB o gera
    # IDs das relações M:N
    autores_ids: List[int] = []
    categorias_ids: List[int] = []

class Livro(LivroBase):
    id_livro: str # O ID gerado pelo DB
    # Respostas aninhadas (nested):
    editora: Optional[Editora] = None
    autores: List[Autor] = []
    categorias: List[Categoria] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Exemplar ---

class ExemplarBase(BaseModel):
    id_livro: str
    codigo_barras: Optional[str] = None
    status: StatusExemplarEnum = StatusExemplarEnum.Disponível
    localizacao: Optional[str] = None

class ExemplarCreate(ExemplarBase):
    pass

class Exemplar(ExemplarBase):
    id_exemplar: int
    livro: Optional[Livro] = None # Retorna o livro completo
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de UsuarioCliente ---

class UsuarioClienteBase(BaseModel):
    nome: str
    cpf: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None

class UsuarioClienteCreate(UsuarioClienteBase):
    pass

class UsuarioCliente(UsuarioClienteBase):
    id_cliente: int
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Empréstimo ---

class EmprestimoBase(BaseModel):
    id_exemplar: int
    id_cliente: int
    # data_prevista_devolucao: sua trigger define 15 dias se for Nulo
    data_prevista_devolucao: Optional[date] = None 

class EmprestimoCreate(EmprestimoBase):
    pass

class Emprestimo(EmprestimoBase):
    id_emprestimo: int
    data_emprestimo: datetime
    data_devolucao: Optional[datetime] = None
    multa: Optional[float] = 0.00
    ativo: bool
    
    # Relações aninhadas para resposta
    cliente: Optional[UsuarioCliente] = None
    exemplar: Optional[Exemplar] = None # Pode simplificar para mostrar menos dados
    
    model_config = ConfigDict(from_attributes=True)
    
# --- Schemas de Reserva ---
# (Similar ao Empréstimo, crie os schemas Base, Create e Read)

# --- Schemas de Segurança (Grupos e Usuários) ---

class GrupoUsuarioBase(BaseModel):
    nome_grupo: str
    descricao: Optional[str] = None

class GrupoUsuarioCreate(GrupoUsuarioBase):
    pass

class GrupoUsuario(GrupoUsuarioBase):
    id_grupo: int
    model_config = ConfigDict(from_attributes=True)

class UsuarioBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    id_grupo: int

class UsuarioCreate(UsuarioBase):
    senha: str # Recebe a senha em texto puro

class Usuario(UsuarioBase):
    id_usuario: int
    grupo: Optional[GrupoUsuario] = None # Retorna o grupo aninhado
    model_config = ConfigDict(from_attributes=True)

# --- Schemas para Token (Autenticação) ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None