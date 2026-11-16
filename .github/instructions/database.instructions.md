---
applyTo: ["migrations/**", "schema/**", "**/db/**", "**/*.sql", "**/alembic/**", "**/flyway/**", "**/liquibase/**", "docs/schema/**"]
---

# Convenções de Código — Banco de Dados / Migrações

> Resumo consolidado das convenções para gerenciamento de banco de dados, migrações e consultas em qualquer projeto. Use este documento como referência principal para padrões de BD; consulte `CLAUDE.md` e `.github/copilot-instructions.md` apenas para governança geral.
>
> **Instruções genéricas**: este arquivo é reutilizável por qualquer projeto com banco de dados relacional ou de documento. Customizações específicas de SGBD (Oracle, PostgreSQL, SQL Server) devem ser adicionadas via adapter próprio.

### Padrões Gerais

- Nomes de tabelas e colunas em `snake_case` com significado de negócio explícito.
- Usar singular para tabelas de entidade (`usuario`, `produto`) e plural para tabelas de junção/pivot (`usuario_roles`).
- Prefixar views com `vw_`, stored procedures com `sp_`, functions com `fn_`.
- Sempre usar `SCHEMA.TABELA` completo em queries nativas.

### Migrações

- Toda alteração de schema deve ser versionada por migração (nunca DDL manual em produção).
- Nome de migração: `V[versão]__[descricao_em_snake_case].sql` (padrão Flyway) ou `[timestamp]_[descricao].py` (Alembic).
- Migrações devem ser **idempotentes** quando possível: `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`.
- Nunca fazer `DROP TABLE` / `DROP COLUMN` direto em produção; usar estratégia de deprecação primeiro.
- Toda migração deve ter rollback documentado ou script de reversão disponível.

```sql
-- V20260101_001__adiciona_campo_status_usuario.sql
ALTER TABLE schema_nome.usuario 
  ADD COLUMN IF NOT EXISTS status VARCHAR(1) NOT NULL DEFAULT 'A';

-- Rollback: ALTER TABLE schema_nome.usuario DROP COLUMN status;
```

### Nomenclatura de Constraints

```sql
-- Primary Key: pk_[tabela]
CONSTRAINT pk_usuario PRIMARY KEY (id)

-- Foreign Key: fk_[tabela_filha]_[tabela_pai]
CONSTRAINT fk_pedido_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)

-- Unique: uq_[tabela]_[campo(s)]
CONSTRAINT uq_usuario_email UNIQUE (email)

-- Index: idx_[tabela]_[campo(s)]
CREATE INDEX idx_pedido_data_criacao ON pedido(data_criacao);

-- Check: ck_[tabela]_[campo]
CONSTRAINT ck_usuario_status CHECK (status IN ('A', 'I'))
```

### Consultas e Queries

- Evitar `SELECT *` em código de produção — listar colunas explicitamente.
- Parâmetros SEMPRE via bind parameters (nunca concatenação de string — SQL injection).
- Usar CTEs (`WITH`) para queries complexas em vez de subqueries aninhadas.
- Adicionar índices em colunas de filtro frequente e colunas de FK.
- Documentar queries complexas com comentário de `-- Razão: [por quê essa query]`.

```sql
-- Correto (bind parameter)
SELECT id, nome, email FROM schema.usuario WHERE id = :id AND status = :status

-- Errado (concatenação — vulnerabilidade SQL injection)
SELECT * FROM usuario WHERE id = '" + id + "'
```

### Transações

- Escopo mínimo de transação (abrir mais tarde, fechar mais cedo).
- Nunca misturar operações de schemas com transaction managers distintos na mesma transação.
- Rollback explícito em catch de exceção com log do motivo.
- Operações de leitura (`SELECT`) geralmente não precisam de transação.

### Dados Sensíveis

- Campos sensíveis (CPF, senha, token) devem ser hasheados/criptografados antes de persistir.
- Nunca logar dados sensíveis (CPF, senha, número de cartão) — mascarar: `***.***.***-**`.
- Colunas de senha devem usar hash bcrypt/argon2, nunca MD5 ou SHA1 simples.

### Documentação de Schema

- Toda tabela deve ter um `COMMENT` no banco com sua responsabilidade.
- Documentação de schema mantida em `docs/schema/DATABASE_SCHEMA_<PROJETO>.md`.
- Antes de alterar entidades, joins ou filtros com banco, consultar a documentação de schema do projeto.

### Guardrail de Manutenção

- Manter este adapter genérico — sem referências a SGBD específico (Oracle, PostgreSQL, MySQL) ou projeto.
- Customizações de SGBD → adapter próprio: `.github/instructions/<projeto>-database.instructions.md`.

### Referências da convenção consolidada

- `CLAUDE.md` e `.github/copilot-instructions.md` para governança geral.
- `docs/schema/DATABASE_SCHEMA_<PROJETO>.md` para schema real do projeto.
- Adapter específico do projeto para transaction managers, schemas nomeados e customizações.

<!-- R-064/R-065: Cadeia pós-plano unificada: *-arch-advisor / planejador retorna motivo: "plano_materializacao_pendente" -> @docs-engineer (materializador único docs/plans/<tipo>/ DRAFT) -> @plan-critic (R-065) -> Gate HITL -> executor (Q&A consultivo isento). -->

