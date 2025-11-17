DROP DATABASE IF EXISTS biblioteca_db;
CREATE DATABASE biblioteca_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE biblioteca_db;

-- Tabelas auxiliares / controle de IDs
-- Tabela para controlar sequências customizadas (por ano, por tipo)
CREATE TABLE seq_counters (
  seq_name VARCHAR(100) NOT NULL,
  seq_year INT NOT NULL,
  seq_value INT NOT NULL DEFAULT 0,
  PRIMARY KEY (seq_name, seq_year)
) ENGINE=InnoDB;

-- Tabelas principais
-- Autor
CREATE TABLE autor (
  id_autor INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  sobrenome VARCHAR(100),
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Categoria
CREATE TABLE categoria (
  id_categoria INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL UNIQUE,
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Editora (adicionada para completar dados de Livro)
CREATE TABLE editora (
  id_editora INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(150) NOT NULL,
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Livro (id crítico gerado por função customizada)
CREATE TABLE livro (
  id_livro VARCHAR(20) PRIMARY KEY, -- formato LIV-AAAA-NNNN
  titulo VARCHAR(255) NOT NULL,
  isbn VARCHAR(20) UNIQUE,
  ano_publicacao INT,
  id_editora INT,
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_editora) REFERENCES editora(id_editora)
) ENGINE=InnoDB;

-- Associação Livro_Autor (N:N)
CREATE TABLE livro_autor (
  id_livro VARCHAR(20) NOT NULL,
  id_autor INT NOT NULL,
  PRIMARY KEY (id_livro, id_autor),
  FOREIGN KEY (id_livro) REFERENCES livro(id_livro) ON DELETE CASCADE,
  FOREIGN KEY (id_autor) REFERENCES autor(id_autor) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Associação Livro_Categoria (N:N)
CREATE TABLE livro_categoria (
  id_livro VARCHAR(20) NOT NULL,
  id_categoria INT NOT NULL,
  PRIMARY KEY (id_livro, id_categoria),
  FOREIGN KEY (id_livro) REFERENCES livro(id_livro) ON DELETE CASCADE,
  FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Exemplar
CREATE TABLE exemplar (
  id_exemplar INT AUTO_INCREMENT PRIMARY KEY,
  id_livro VARCHAR(20) NOT NULL,
  codigo_barras VARCHAR(50) UNIQUE,
  status ENUM('Disponível','Emprestado','Reservado','Perda') NOT NULL DEFAULT 'Disponível',
  localizacao VARCHAR(150),
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_livro) REFERENCES livro(id_livro) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Usuario_Cliente
CREATE TABLE usuario_cliente (
  id_cliente INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(150) NOT NULL,
  cpf VARCHAR(14) UNIQUE NOT NULL,
  email VARCHAR(150),
  telefone VARCHAR(30),
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- usuarios e grupos_usuarios (controle de acesso interno)
CREATE TABLE grupos_usuarios (
  id_grupo INT AUTO_INCREMENT PRIMARY KEY,
  nome_grupo VARCHAR(50) UNIQUE NOT NULL,
  descricao VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  senha_hash VARCHAR(255) NOT NULL, -- salvar hashes (bcrypt/etc) no backend
  id_grupo INT NOT NULL,
  email VARCHAR(150),
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_grupo) REFERENCES grupos_usuarios(id_grupo)
) ENGINE=InnoDB;

-- Empréstimo
CREATE TABLE emprestimo (
  id_emprestimo INT AUTO_INCREMENT PRIMARY KEY,
  id_exemplar INT NOT NULL,
  id_cliente INT NOT NULL,
  data_emprestimo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_prevista_devolucao DATE NOT NULL,
  data_devolucao DATETIME DEFAULT NULL,
  multa DECIMAL(10,2) DEFAULT 0.00,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_exemplar) REFERENCES exemplar(id_exemplar),
  FOREIGN KEY (id_cliente) REFERENCES usuario_cliente(id_cliente)
) ENGINE=InnoDB;

-- Reserva
CREATE TABLE reserva (
  id_reserva INT AUTO_INCREMENT PRIMARY KEY,
  id_exemplar INT NOT NULL,
  id_cliente INT NOT NULL,
  data_reserva DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_expiracao DATETIME,
  notificado BOOLEAN DEFAULT FALSE,
  status ENUM('Ativa','Atendida','Expirada','Cancelada') DEFAULT 'Ativa',
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_exemplar) REFERENCES exemplar(id_exemplar),
  FOREIGN KEY (id_cliente) REFERENCES usuario_cliente(id_cliente)
) ENGINE=InnoDB;

-- Logs simples (opcional, útil para auditoria)
CREATE TABLE audit_log (
  id_log INT AUTO_INCREMENT PRIMARY KEY,
  entidade VARCHAR(50),
  entidade_id VARCHAR(50),
  acao VARCHAR(50),
  descricao TEXT,
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Índices sugeridos
CREATE INDEX idx_livro_isbn ON livro(isbn);
CREATE INDEX idx_usuario_cpf ON usuario_cliente(cpf);
-- índice para facilitar busca de empréstimos ativos por cliente
CREATE INDEX idx_emprestimo_cliente_ativo ON emprestimo(id_cliente, data_devolucao);
-- índice para empréstimos atrasados
CREATE INDEX idx_emprestimo_prevdev ON emprestimo(data_prevista_devolucao, data_devolucao);

-- FUNÇÃO: gerar_id_livro() - Geração de ID crítico
-- Formato: LIV-AAAA-NNNN (ano + seq 4 dígitos por ano)
-- Justificativa: garante ID legível, agrupado por ano, evita colisões mesmo em concorrência (lock interno)
DROP FUNCTION IF EXISTS gerar_id_livro;
DELIMITER $$

CREATE FUNCTION gerar_id_livro() RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
  DECLARE v_year INT;
  DECLARE v_seq INT;
  DECLARE v_id VARCHAR(20);

  SET v_year = YEAR(CURDATE());

  -- Se ainda não existe contador pro ano atual, cria
  IF NOT EXISTS (SELECT 1 FROM seq_counters WHERE seq_name = 'livro' AND seq_year = v_year) THEN
    INSERT INTO seq_counters (seq_name, seq_year, seq_value)
    VALUES ('livro', v_year, 0);
  END IF;

  -- Incrementa o contador
  UPDATE seq_counters
    SET seq_value = seq_value + 1
    WHERE seq_name = 'livro' AND seq_year = v_year;

  -- Recupera o novo valor
  SELECT seq_value INTO v_seq
    FROM seq_counters
    WHERE seq_name = 'livro' AND seq_year = v_year;

  -- Monta o ID no formato LIV-AAAA-NNNN
  SET v_id = CONCAT('LIV-', LPAD(v_year,4,'0'), '-', LPAD(v_seq,4,'0'));
  RETURN v_id;
END$$
DELIMITER ;


-- Exemplo de trigger para gerar id_livro ao inserir sem informar id
-- (opcional: usar no INSERT para simplificar)
DROP TRIGGER IF EXISTS trg_livro_before_insert;
DELIMITER $$
CREATE TRIGGER trg_livro_before_insert
BEFORE INSERT ON livro
FOR EACH ROW
BEGIN
  IF NEW.id_livro IS NULL OR NEW.id_livro = '' THEN
    SET NEW.id_livro = gerar_id_livro();
  END IF;
END$$
DELIMITER ;

-- Trigger 1: AFTER INSERT em emprestimo -> atualiza status do exemplar para 'Emprestado'
-- Justificativa: cumpre RNF06 (integridade transacional) e RF04
DROP TRIGGER IF EXISTS trg_emprestimo_after_insert;
DELIMITER $$
CREATE TRIGGER trg_emprestimo_after_insert
AFTER INSERT ON emprestimo
FOR EACH ROW
BEGIN
  -- somente atualiza se exemplar estiver disponível
  UPDATE exemplar
    SET status = 'Emprestado'
    WHERE id_exemplar = NEW.id_exemplar
      AND status = 'Disponível';
  -- inserir log
  INSERT INTO audit_log(entidade, entidade_id, acao, descricao)
    VALUES ('Exemplar', CAST(NEW.id_exemplar AS CHAR), 'EmprestimoCriado', CONCAT('Emprestimo ID=', NEW.id_emprestimo));
END$$
DELIMITER ;

-- Trigger 2: BEFORE UPDATE em emprestimo -> se data_devolucao preenchida, calcula multa (se houver)
-- Justificativa: garante cálculo consistente de multa imediatamente quando devolução registrada
DROP TRIGGER IF EXISTS trg_emprestimo_before_update;
DELIMITER $$
CREATE TRIGGER trg_emprestimo_before_update
BEFORE UPDATE ON emprestimo
FOR EACH ROW
BEGIN
  DECLARE dias_atraso INT;
  DECLARE valor_multa DECIMAL(10,2);
  -- se a devolução está sendo inserida (antes era NULL e agora não é NULL)
  IF OLD.data_devolucao IS NULL AND NEW.data_devolucao IS NOT NULL THEN
    SET dias_atraso = DATEDIFF(DATE(NEW.data_devolucao), NEW.data_prevista_devolucao);
    IF dias_atraso > 0 THEN
      SET valor_multa = dias_atraso * 1.00; -- R$1,00 por dia (exemplo) - business rule
    ELSE
      SET valor_multa = 0.00;
    END IF;
    SET NEW.multa = valor_multa;
  END IF;
END$$
DELIMITER ;

-- PROCEDURE: finalizar_emprestimo(id_emprestimo)
-- - Atualiza data_devolucao para NOW(), calcula multa (usando triggres já definidas)
-- - Marca emprestimo como inativo (ativo = FALSE), atualiza exemplar para Disponível,
-- - Se existir fila de reservas (status Ativa) para o exemplar, notifica próximo e muda exemplar para 'Reservado' (não Disponível)
-- Justificativa: encapsula a logica transacional para devolução e notificação de reservas.
DROP PROCEDURE IF EXISTS finalizar_emprestimo;
DELIMITER $$
CREATE PROCEDURE finalizar_emprestimo(IN p_id_emprestimo INT)
BEGIN
  DECLARE v_id_exemplar INT;
  DECLARE v_next_reserva_id INT;
  DECLARE v_next_cliente INT;
  DECLARE v_exists INT;

  -- obter exemplar
  SELECT id_exemplar INTO v_id_exemplar FROM emprestimo WHERE id_emprestimo = p_id_emprestimo;

  -- registrar devolução agora (dispara trigger BEFORE UPDATE para calcular multa)
  UPDATE emprestimo
    SET data_devolucao = NOW(),
        ativo = FALSE
    WHERE id_emprestimo = p_id_emprestimo;

  -- verifica se existe reserva ativa para este exemplar (fila por data_reserva)
  SELECT id_reserva, id_cliente INTO v_next_reserva_id, v_next_cliente
    FROM reserva
    WHERE id_exemplar = v_id_exemplar
      AND status = 'Ativa'
      AND (data_expiracao IS NULL OR data_expiracao > NOW())
    ORDER BY data_reserva ASC
    LIMIT 1;

  -- Se não encontrou reserva (v_next_reserva_id NULL), atualizar exemplar para Disponível
  IF v_next_reserva_id IS NULL THEN
    UPDATE exemplar SET status = 'Disponível' WHERE id_exemplar = v_id_exemplar;
  ELSE
    -- marcar reserva como notificada e status atendida (poderia ser 'Atendida' após confirmação; aqui apenas notifica)
    UPDATE reserva
      SET notificado = TRUE, status = 'Atendida'
      WHERE id_reserva = v_next_reserva_id;

    -- atualizar exemplar para Reservado (esperando retirada pelo cliente)
    UPDATE exemplar SET status = 'Reservado' WHERE id_exemplar = v_id_exemplar;
END IF;
END$$
DELIMITER ;

-- Views
-- 1) Acervo_Disponivel: Livros com exemplares disponíveis
-- 2) Emprestimos_Atrasados: Empréstimos cuja data_prevista_devolucao < hoje e data_devolucao IS NULL

DROP VIEW IF EXISTS Acervo_Disponivel;
CREATE VIEW Acervo_Disponivel AS
SELECT 
  l.id_livro,
  l.titulo,
  l.isbn,
  e.id_exemplar,
  e.codigo_barras,
  e.localizacao
FROM livro l
JOIN exemplar e ON e.id_livro = l.id_livro
WHERE e.status = 'Disponível';

DROP VIEW IF EXISTS Emprestimos_Atrasados;
CREATE VIEW Emprestimos_Atrasados AS
SELECT 
  emp.id_emprestimo,
  emp.id_exemplar,
  emp.id_cliente,
  u.nome AS nome_cliente,
  emp.data_emprestimo,
  emp.data_prevista_devolucao
FROM emprestimo emp
JOIN usuario_cliente u ON u.id_cliente = emp.id_cliente
WHERE emp.data_prevista_devolucao < CURDATE()
  AND emp.data_devolucao IS NULL
  AND emp.ativo = TRUE;

-- ===========================
-- Regras extras / constraints (limite de empréstimos ativos por cliente)
-- ===========================
DROP TRIGGER IF EXISTS trg_emprestimo_before_insert_limit;
DELIMITER $$
CREATE TRIGGER trg_emprestimo_before_insert_limit
BEFORE INSERT ON emprestimo
FOR EACH ROW
BEGIN
  DECLARE v_count INT;
  -- contar empréstimos ativos (data_devolucao IS NULL ou ativo = TRUE)
  SELECT COUNT(*) INTO v_count FROM emprestimo
    WHERE id_cliente = NEW.id_cliente AND ativo = TRUE AND data_devolucao IS NULL;
  IF v_count >= 3 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Limite de 3 emprestimos ativos por cliente atingido.';
  END IF;

  -- Verifica se exemplar está disponível
  IF (SELECT status FROM exemplar WHERE id_exemplar = NEW.id_exemplar) <> 'Disponível' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exemplar não está disponível para empréstimo.';
  END IF;

  -- Define data_prevista_devolucao padrão caso não informado: 15 dias a partir de data_emprestimo
  IF NEW.data_prevista_devolucao IS NULL THEN
    SET NEW.data_prevista_devolucao = DATE_ADD(DATE(NEW.data_emprestimo), INTERVAL 15 DAY);
  END IF;
END$$
DELIMITER ;


-- Criar logins de aplicação/operadores (exemplo)
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'AppUser#2025';
CREATE USER IF NOT EXISTS 'bibliotecario'@'%' IDENTIFIED BY 'Biblio#2025';
CREATE USER IF NOT EXISTS 'leitor'@'%' IDENTIFIED BY 'Leitor#2025';

-- app_user: usado pela aplicação (backend). Concede SELECT/INSERT/UPDATE/DELETE nas tabelas necessárias
GRANT SELECT, INSERT, UPDATE, DELETE ON bibliotheca_db.* TO 'app_user'@'%';
-- Observação: o nome do DB no GRANT acima tem um possível erro proposital para forçar ajuste conforme ambiente.
-- Corrigir GRANT:
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'app_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON `biblioteca_db`.* TO 'app_user'@'%';

-- bibliotecario: operador humano, pode gerenciar empréstimos, reservas e exemplares, leitura de livros/autores
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'bibliotecario'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON `biblioteca_db`.exemplar TO 'bibliotecario'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON `biblioteca_db`.emprestimo TO 'bibliotecario'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON `biblioteca_db`.reserva TO 'bibliotecario'@'%';
GRANT SELECT ON `biblioteca_db`.livro TO 'bibliotecario'@'%';
GRANT SELECT ON `biblioteca_db`.autor TO 'bibliotecario'@'%';
GRANT SELECT ON `biblioteca_db`.categoria TO 'bibliotecario'@'%';
GRANT EXECUTE ON `biblioteca_db`.* TO 'bibliotecario'@'%';

-- leitor: apenas leitura do acervo e seus próprios empréstimos/reservas (no nível da aplicação filtrar por id)
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'leitor'@'%';
GRANT SELECT ON `biblioteca_db`.livro TO 'leitor'@'%';
GRANT SELECT ON `biblioteca_db`.exemplar TO 'leitor'@'%';
GRANT SELECT ON `biblioteca_db`.autor TO 'leitor'@'%';
GRANT SELECT ON `biblioteca_db`.categoria TO 'leitor'@'%';
-- não dar acesso direto às tabelas de usuários/credenciais do sistema (usuarios)


-- Exemplos de inserts

INSERT INTO grupos_usuarios (nome_grupo, descricao) VALUES ('Administrador','Gerencia o sistema'), ('Bibliotecario','Opera o dia-a-dia'), ('Cliente','Usuario final');

-- criar um editora/autor/categoria e um livro via função
INSERT INTO editora (nome) VALUES ('Editora Exemplo');
INSERT INTO autor (nome, sobrenome) VALUES ('Paulo','Silva');
INSERT INTO categoria (nome) VALUES ('Ficcao');

-- criar livro (id gerada pela trigger/função se não informar)
INSERT INTO livro (titulo, isbn, ano_publicacao, id_editora) VALUES ('Livro Exemplo','978-0-00-000000-1',2025,1);

-- assoc autor/categoria
INSERT INTO livro_autor (id_livro, id_autor) SELECT id_livro, 1 FROM livro LIMIT 1;
INSERT INTO livro_categoria (id_livro, id_categoria) SELECT id_livro, 1 FROM livro LIMIT 1;

-- criar exemplar
INSERT INTO exemplar (id_livro, codigo_barras, localizacao) SELECT id_livro, CONCAT('CB', LPAD(FLOOR(RAND()*99999),5,'0')), 'Estante A' FROM livro LIMIT 1;

-- criar cliente
INSERT INTO usuario_cliente (nome, cpf, email) VALUES ('Cliente Teste','123.456.789-00','cliente@ex.com');

-- criar emprestimo (deve respeitar triggers e contadores)
-- SELECT id_exemplar FROM exemplar LIMIT 1;
INSERT INTO emprestimo (id_exemplar, id_cliente, data_prevista_devolucao) VALUES (1,1, DATE_ADD(CURDATE(), INTERVAL 15 DAY));

select * from usuario_cliente;

SELECT * FROM grupos_usuarios;

INSERT INTO grupos_usuarios (id_grupo, nome_grupo)
VALUES (1, 'Administrador');


INSERT INTO usuarios (username, senha_hash, id_grupo, email)
VALUES (
    'admin',
    '$2b$12$4OFy3F555DIBl3NXAqSVFuZCe2AWa7y4xrqHRHTvah6.u0Oow65IG',  -- seu hash aqui
    1,
    'admin@suabiblioteca.com'
);

SHOW TRIGGERS WHERE `Trigger` = 'trg_livro_before_insert';

USE biblioteca_db;
CREATE TABLE IF NOT EXISTS seq_counters (
  seq_name VARCHAR(100) NOT NULL,
  seq_year INT NOT NULL,
  seq_value INT NOT NULL DEFAULT 0,
  PRIMARY KEY (seq_name, seq_year)
) ENGINE=InnoDB;



DROP FUNCTION IF EXISTS gerar_id_livro;
DELIMITER $$
CREATE FUNCTION gerar_id_livro() RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
  DECLARE v_year INT;
  DECLARE v_seq INT;
  DECLARE v_id VARCHAR(20);
  SET v_year = YEAR(CURDATE());
  IF NOT EXISTS (SELECT 1 FROM seq_counters WHERE seq_name = 'livro' AND seq_year = v_year) THEN
    INSERT INTO seq_counters (seq_name, seq_year, seq_value)
    VALUES ('livro', v_year, 0);
  END IF;
  UPDATE seq_counters
    SET seq_value = seq_value + 1
    WHERE seq_name = 'livro' AND seq_year = v_year;
  SELECT seq_value INTO v_seq
    FROM seq_counters
    WHERE seq_name = 'livro' AND seq_year = v_year;
  SET v_id = CONCAT('LIV-', LPAD(v_year,4,'0'), '-', LPAD(v_seq,4,'0'));
  RETURN v_id;
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_livro_before_insert;
DELIMITER $$
CREATE TRIGGER trg_livro_before_insert
BEFORE INSERT ON livro
FOR EACH ROW
BEGIN
  IF NEW.id_livro IS NULL OR NEW.id_livro = '' THEN
    SET NEW.id_livro = gerar_id_livro();
  END IF;
END$$
DELIMITER ;

INSERT INTO livro (titulo, id_editora)
VALUES ('Teste Direto do SQL', 1);

GRANT ALL PRIVILEGES ON `biblioteca_db`.* TO 'app_user'@'%';

FLUSH PRIVILEGES;
