# models.py
import enum
from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, Table,
                        Boolean, DECIMAL, Date, Enum as SqlEnum, TEXT)
# 'FetchedValue' foi REMOVIDO daqui
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base # Importa a 'Base' do seu arquivo database.py

# --- Enumerações (para colunas ENUM) ---
class StatusExemplarEnum(enum.Enum):
    Disponível = "Disponível"
    Emprestado = "Emprestado"
    Reservado = "Reservado"
    Perda = "Perda"

class StatusReservaEnum(enum.Enum):
    Ativa = "Ativa"
    Atendida = "Atendida"
    Expirada = "Expirada"
    Cancelada = "Cancelada"

# --- Tabelas de Associação (Muitos-para-Muitos) ---

# Tabela livro_autor (linka Livro e Autor)
livro_autor_table = Table('livro_autor', Base.metadata,
    Column('id_livro', String(20), ForeignKey('livro.id_livro'), primary_key=True),
    Column('id_autor', Integer, ForeignKey('autor.id_autor'), primary_key=True)
)

# Tabela livro_categoria (linka Livro e Categoria)
livro_categoria_table = Table('livro_categoria', Base.metadata,
    Column('id_livro', String(20), ForeignKey('livro.id_livro'), primary_key=True),
    Column('id_categoria', Integer, ForeignKey('categoria.id_categoria'), primary_key=True)
)


# --- Modelos Principais (Tabelas) ---

class Autor(Base):
    __tablename__ = "autor"
    id_autor = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    sobrenome = Column(String(100))
    criado_em = Column(DateTime, server_default=func.now())
    
    livros = relationship("Livro", secondary=livro_autor_table, back_populates="autores")

class Categoria(Base):
    __tablename__ = "categoria"
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True)
    criado_em = Column(DateTime, server_default=func.now())
    
    livros = relationship("Livro", secondary=livro_categoria_table, back_populates="categorias")

class Editora(Base):
    __tablename__ = "editora"
    id_editora = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    criado_em = Column(DateTime, server_default=func.now())
    
    livros = relationship("Livro", back_populates="editora")

class Livro(Base):
    __tablename__ = "livro"
    
    # ===== ALTERAÇÃO AQUI =====
    # Voltamos ao simples. O Python vai fornecer o valor.
    id_livro = Column(String(20), primary_key=True)
    # ==========================
    
    titulo = Column(String(255), nullable=False)
    isbn = Column(String(20), unique=True, index=True)
    ano_publicacao = Column(Integer)
    id_editora = Column(Integer, ForeignKey("editora.id_editora"))
    criado_em = Column(DateTime, server_default=func.now())
    
    # Relações
    editora = relationship("Editora", back_populates="livros")
    autores = relationship("Autor", secondary=livro_autor_table, back_populates="livros")
    categorias = relationship("Categoria", secondary=livro_categoria_table, back_populates="livros")
    exemplares = relationship("Exemplar", back_populates="livro")

class Exemplar(Base):
    __tablename__ = "exemplar"
    id_exemplar = Column(Integer, primary_key=True, autoincrement=True)
    id_livro = Column(String(20), ForeignKey("livro.id_livro"), nullable=False)
    codigo_barras = Column(String(50), unique=True)
    status = Column(SqlEnum(StatusExemplarEnum), nullable=False, default=StatusExemplarEnum.Disponível)
    localizacao = Column(String(150))
    criado_em = Column(DateTime, server_default=func.now())
    
    livro = relationship("Livro", back_populates="exemplares")
    emprestimos = relationship("Emprestimo", back_populates="exemplar")
    reservas = relationship("Reserva", back_populates="exemplar")

class UsuarioCliente(Base):
    __tablename__ = "usuario_cliente"
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    email = Column(String(150))
    telefone = Column(String(30))
    criado_em = Column(DateTime, server_default=func.now())
    
    emprestimos = relationship("Emprestimo", back_populates="cliente")
    reservas = relationship("Reserva", back_populates="cliente")

class GruposUsuarios(Base):
    __tablename__ = "grupos_usuarios"
    id_grupo = Column(Integer, primary_key=True, autoincrement=True)
    nome_grupo = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(255))
    
    usuarios = relationship("Usuarios", back_populates="grupo")

class Usuarios(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    id_grupo = Column(Integer, ForeignKey("grupos_usuarios.id_grupo"), nullable=False)
    email = Column(String(150))
    criado_em = Column(DateTime, server_default=func.now())
    
    grupo = relationship("GruposUsuarios", back_populates="usuarios")

class Emprestimo(Base):
    __tablename__ = "emprestimo"
    id_emprestimo = Column(Integer, primary_key=True, autoincrement=True)
    id_exemplar = Column(Integer, ForeignKey("exemplar.id_exemplar"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("usuario_cliente.id_cliente"), nullable=False)
    data_emprestimo = Column(DateTime, nullable=False, server_default=func.now())
    data_prevista_devolucao = Column(Date, nullable=False)
    data_devolucao = Column(DateTime, default=None)
    multa = Column(DECIMAL(10, 2), default=0.00)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime, server_default=func.now())
    
    exemplar = relationship("Exemplar", back_populates="emprestimos")
    cliente = relationship("UsuarioCliente", back_populates="emprestimos")

class Reserva(Base):
    __tablename__ = "reserva"
    id_reserva = Column(Integer, primary_key=True, autoincrement=True)
    id_exemplar = Column(Integer, ForeignKey("exemplar.id_exemplar"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("usuario_cliente.id_cliente"), nullable=False)
    data_reserva = Column(DateTime, nullable=False, server_default=func.now())
    data_expiracao = Column(DateTime)
    notificado = Column(Boolean, default=False)
    status = Column(SqlEnum(StatusReservaEnum), default=StatusReservaEnum.Ativa)
    criado_em = Column(DateTime, server_default=func.now())
    
    exemplar = relationship("Exemplar", back_populates="reservas")
    cliente = relationship("UsuarioCliente", back_populates="reservas")

class AuditLog(Base):
    __tablename__ = "audit_log"
    id_log = Column(Integer, primary_key=True, autoincrement=True)
    entidade = Column(String(50))
    entidade_id = Column(String(50))
    acao = Column(String(50))
    descricao = Column(TEXT)
    criado_em = Column(DateTime, server_default=func.now())

# ===== NOVO MODELO AQUI =====
# Mapeia a tabela de contadores para o Python
class SeqCounters(Base):
    __tablename__ = "seq_counters"
    seq_name = Column(String(100), primary_key=True)
    seq_year = Column(Integer, primary_key=True)
    seq_value = Column(Integer, nullable=False, default=0)