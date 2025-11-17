#para rodar o codigo, executar no terminal: uvicorn main:app --reload
# main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, IntegrityError # Para capturar erros do DB
from typing import List, Optional

import datetime
import models
import schemas
import security
from database import engine, get_db

app = FastAPI(
    title="API da Biblioteca",
    description="API para o sistema de gerenciamento da biblioteca",
    version="1.0.0"
)
origins = [
    "http://localhost",       # Para testes locais
    "http://localhost:3000",  # Se o seu frontend React/Vue rodar na porta 3000
    "http://localhost:5173",  # Se o seu frontend (ex: Vite) rodar na porta 5173
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Quais origens são permitidas
    allow_credentials=True,    # Permitir cookies/autenticação
    allow_methods=["*"],         # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],         # Permitir todos os cabeçalhos
)

#gerar id por erro da api não conseguir ativar o trigger no mysql
def gerar_id_livro_py(db: Session) -> str:
    """
    Recria a lógica da FUNÇÃO gerar_id_livro do MySQL em Python.
    """
    v_year = datetime.datetime.now().year
    
    try:
        # 1. Encontra ou cria o contador
        contador_db = db.query(models.SeqCounters).filter_by(
            seq_name='livro', 
            seq_year=v_year
        ).first()
        
        if not contador_db:
            contador_db = models.SeqCounters(
                seq_name='livro', 
                seq_year=v_year, 
                seq_value=0
            )
            db.add(contador_db)
            db.commit() # Commit inicial para criar o contador
            db.refresh(contador_db)

        # 2. Incrementa o valor
        # Usamos uma atualização "atômica" para segurança
        db.query(models.SeqCounters).filter_by(
            seq_name='livro', 
            seq_year=v_year
        ).update({'seq_value': models.SeqCounters.seq_value + 1})
        
        # 3. Busca o valor atualizado
        db.commit() # Commit do update
        
        contador_atualizado = db.query(models.SeqCounters).filter_by(
            seq_name='livro', 
            seq_year=v_year
        ).first()
        
        if not contador_atualizado:
             raise Exception("Falha ao ler o contador após o incremento.")
             
        v_seq = contador_atualizado.seq_value
        
        # 4. Formata o ID
        v_id = f"LIV-{v_year:04d}-{v_seq:04d}"
        return v_id
        
    except Exception as e:
        db.rollback() # Desfaz qualquer commit parcial
        raise Exception(f"Erro ao gerar ID do livro: {str(e)}")


# =======================================================================
# 1. ENDPOINTS DE AUTENTICAÇÃO E SEGURANÇA
# =======================================================================

@app.post("/token", response_model=schemas.Token, tags=["Segurança"])
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/usuarios/me", response_model=schemas.Usuario, tags=["Usuários"])
def read_users_me(
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    return current_user

@app.post("/api/usuarios/", response_model=schemas.Usuario, tags=["Usuários"])
def create_user(
    user_to_create: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    if current_user.grupo.nome_grupo != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Apenas Administradores podem criar usuários."
        )

    db_user = db.query(models.Usuarios).filter(models.Usuarios.username == user_to_create.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já registrado"
        )
        
    hashed_password = security.get_password_hash(user_to_create.senha)
    
    new_user = models.Usuarios(
        username=user_to_create.username,
        email=user_to_create.email,
        id_grupo=user_to_create.id_grupo,
        senha_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# =======================================================================
# 2. ENDPOINTS DE CLIENTES (UsuarioCliente)
# =======================================================================

@app.post("/api/clientes/", response_model=schemas.UsuarioCliente, tags=["Clientes"])
def create_cliente(
    cliente: schemas.UsuarioClienteCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")

    try:
        db_cliente = models.UsuarioCliente(**cliente.model_dump())
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except IntegrityError: # Captura erro de CPF duplicado
        db.rollback()
        raise HTTPException(status_code=400, detail="CPF já cadastrado.")

@app.get("/api/clientes/{cliente_id}", response_model=schemas.UsuarioCliente, tags=["Clientes"])
def read_cliente(
    cliente_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    db_cliente = db.query(models.UsuarioCliente).filter(models.UsuarioCliente.id_cliente == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente

@app.get("/api/clientes/", response_model=List[schemas.UsuarioCliente], tags=["Clientes"])
def read_all_clientes(
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    return db.query(models.UsuarioCliente).all()

# =======================================================================
# 3. ENDPOINTS DO ACERVO (Livros, Autores, etc.)
# =======================================================================

# ===== ENDPOINT 'create_livro' ATUALIZADO =====
@app.post("/api/livros/", response_model=schemas.Livro, tags=["Acervo - Livros"])
def create_livro(
    livro_data: schemas.LivroCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    """
    Cria um novo livro. O ID (LIV-AAAA-NNNN) é gerado pela
    função Python 'gerar_id_livro_py', ignorando a Trigger do DB.
    """
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")
        
    try:
        # 1. Gerar o novo ID
        # A função 'gerar_id_livro_py' lida com seus próprios commits
        novo_id_livro = gerar_id_livro_py(db)

        # 2. Preparar os dados do livro
        livro_dict = livro_data.model_dump(exclude={'autores_ids', 'categorias_ids'})
        livro_dict['id_livro'] = novo_id_livro # Adiciona o ID gerado

        db_livro = models.Livro(**livro_dict)
        
        # 3. Associar relações (se existirem)
        if livro_data.autores_ids:
            db_livro.autores = db.query(models.Autor).filter(models.Autor.id_autor.in_(livro_data.autores_ids)).all()
        if livro_data.categorias_ids:
            db_livro.categorias = db.query(models.Categoria).filter(models.Categoria.id_categoria.in_(livro_data.categorias_ids)).all()
        
        # 4. Salvar o livro
        db.add(db_livro)
        db.commit() # Commit final para o livro
        db.refresh(db_livro)
        return db_livro
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro de integridade: {e.orig}")
    except Exception as e:
        db.rollback()
        # Captura erros da função 'gerar_id_livro_py'
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.get("/api/livros/", response_model=List[schemas.Livro], tags=["Acervo - Livros"])
def read_all_livros(
    db: Session = Depends(get_db),
):
    livros = db.query(models.Livro).options(
        joinedload(models.Livro.autores),
        joinedload(models.Livro.categorias),
        joinedload(models.Livro.editora)
    ).all()
    return livros

# --- CRUDs auxiliares para Autores e Categorias ---
@app.post("/api/autores/", response_model=schemas.Autor, tags=["Acervo - Autores"])
def create_autor(
    autor: schemas.AutorCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")
    db_autor = models.Autor(**autor.model_dump())
    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    return db_autor

@app.get("/api/autores/", response_model=List[schemas.Autor], tags=["Acervo - Autores"])
def read_all_autores(db: Session = Depends(get_db)):
    return db.query(models.Autor).all()
    
# =======================================================================
# 4. ENDPOINTS DE LÓGICA DE NEGÓCIO (Empréstimos)
# =======================================================================

@app.post("/api/emprestimos/", response_model=schemas.Emprestimo, tags=["Empréstimos"])
def create_emprestimo(
    emprestimo_data: schemas.EmprestimoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")

    db_emprestimo = models.Emprestimo(**emprestimo_data.model_dump())
    
    try:
        db.add(db_emprestimo)
        db.commit()
        db.refresh(db_emprestimo)
        
        db_emprestimo_completo = db.query(models.Emprestimo).options(
            joinedload(models.Emprestimo.cliente),
            joinedload(models.Emprestimo.exemplar)
        ).filter(models.Emprestimo.id_emprestimo == db_emprestimo.id_emprestimo).first()
        
        return db_emprestimo_completo
        
    except OperationalError as e:
        db.rollback()
        erro_msg = str(e.orig)
        if "Limite de 3 emprestimos" in erro_msg:
            raise HTTPException(status_code=400, detail="Limite de 3 emprestimos ativos por cliente atingido.")
        elif "Exemplar não está disponível" in erro_msg:
            raise HTTPException(status_code=400, detail="Exemplar não está disponível para empréstimo.")
        else:
            raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {erro_msg}")
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


@app.post("/api/emprestimos/{emprestimo_id}/finalizar", tags=["Empréstimos"])
def finalizar_emprestimo(
    emprestimo_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")
        
    db_emprestimo = db.query(models.Emprestimo).filter(
        models.Emprestimo.id_emprestimo == emprestimo_id,
        models.Emprestimo.ativo == True
    ).first()
    
    if not db_emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado ou já finalizado.")
        
    try:
        db.execute(text(f"CALL finalizar_emprestimo({emprestimo_id})"))
        db.commit()
        
        return {"message": "Empréstimo finalizado com sucesso."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao finalizar empréstimo: {str(e)}")
    
@app.get("/api/emprestimos/", response_model=List[schemas.Emprestimo], tags=["Empréstimos"])
def read_all_emprestimos(
    ativo: Optional[bool] = None, # Filtro opcional: /api/emprestimos/?ativo=true
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    """
    Lista todos os empréstimos.
    - Se 'ativo=true', lista apenas empréstimos não devolvidos.
    - Se 'ativo=false', lista apenas empréstimos já finalizados.
    - Se não for fornecido, lista todos.
    """
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")

    query = db.query(models.Emprestimo).options(
        joinedload(models.Emprestimo.cliente),
        joinedload(models.Emprestimo.exemplar)
    )
    
    if ativo is not None:
        query = query.filter(models.Emprestimo.ativo == ativo)
        
    return query.all()

@app.get("/api/emprestimos/por-cliente/{cliente_id}", response_model=List[schemas.Emprestimo], tags=["Empréstimos"])
def read_emprestimos_por_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    """
    Lista o histórico de todos os empréstimos de um cliente específico.
    """
    # Verificação de segurança:
    # (Idealmente, um cliente só pode ver o seu próprio, e um admin/bibliotecário pode ver todos)
    
    return db.query(models.Emprestimo).options(
        joinedload(models.Emprestimo.exemplar) # Carrega dados do exemplar junto
    ).filter(models.Emprestimo.id_cliente == cliente_id).all()

@app.get("/api/emprestimos/{emprestimo_id}", response_model=schemas.Emprestimo, tags=["Empréstimos"])
def read_emprestimo_por_id(
    emprestimo_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    """
    Busca um empréstimo específico pelo seu ID.
    """
    emprestimo = db.query(models.Emprestimo).options(
        joinedload(models.Emprestimo.cliente),
        joinedload(models.Emprestimo.exemplar)
    ).filter(models.Emprestimo.id_emprestimo == emprestimo_id).first()
    
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
        
    return emprestimo    

# =======================================================================
# 5. ENDPOINTS DE EXEMPLARES
# =======================================================================

@app.post("/api/exemplares/", response_model=schemas.Exemplar, tags=["Acervo - Exemplares"])
def create_exemplar(
    exemplar_data: schemas.ExemplarCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")

    db_livro = db.query(models.Livro).filter(models.Livro.id_livro == exemplar_data.id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail=f"Livro com ID {exemplar_data.id_livro} não encontrado.")

    db_exemplar = models.Exemplar(**exemplar_data.model_dump())
    
    try:
        db.add(db_exemplar)
        db.commit()
        db.refresh(db_exemplar)
        return db_exemplar
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro de integridade (ex: código de barras duplicado): {e.orig}")

@app.get("/api/exemplares/por-livro/{livro_id}", response_model=List[schemas.Exemplar], tags=["Acervo - Exemplares"])
def get_exemplares_por_livro(
    livro_id: str,
    db: Session = Depends(get_db)
):
    exemplares = db.query(models.Exemplar).filter(models.Exemplar.id_livro == livro_id).all()
    if not exemplares:
        raise HTTPException(status_code=404, detail="Nenhum exemplar encontrado para este livro.")
    return exemplares

# =======================================================================
# 6. ENDPOINTS DE ENTIDADES DE APOIO (Editora, Categoria)
# =======================================================================

@app.post("/api/editoras/", response_model=schemas.Editora, tags=["Acervo - Editoras"])
def create_editora(
    editora: schemas.EditoraCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")
        
    db_editora = models.Editora(**editora.model_dump())
    
    try:
        db.add(db_editora)
        db.commit()
        db.refresh(db_editora)
        return db_editora
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Editora já cadastrada.")

@app.get("/api/editoras/", response_model=List[schemas.Editora], tags=["Acervo - Editoras"])
def read_all_editoras(db: Session = Depends(get_db)):
    return db.query(models.Editora).all()

@app.post("/api/categorias/", response_model=schemas.Categoria, tags=["Acervo - Categorias"])
def create_categoria(
    categoria: schemas.CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuarios = Depends(security.get_current_user)
):
    if current_user.grupo.nome_grupo not in ("Bibliotecario", "Administrador"):
        raise HTTPException(status_code=403, detail="Permissão negada.")
        
    db_categoria = models.Categoria(**categoria.model_dump())
    
    try:
        db.add(db_categoria)
        db.commit()
        db.refresh(db_categoria)
        return db_categoria
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Categoria já cadastrada.")

@app.get("/api/categorias/", response_model=List[schemas.Categoria], tags=["Acervo - Categorias"])
def read_all_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()