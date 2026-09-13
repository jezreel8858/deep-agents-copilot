# REQ-002: Especificação de Requisitos — Persistência Local e Nuvem de Incidentes de Workflows

**Status:** Aprovado para Blueprint Técnico  
**Data:** 2026-09-12  
**Autor:** @requirements-analyst  
**Workflow:** WORKFLOW-FEATURE-DEVELOPMENT (Etapa 2 — Elicitação de Requisitos)  
**Fonte Original (Stakeholder):**  
> *"preciso que durante todo o problema enfrentado por quaisquer agent durante um workflow seja persistido em um banco local, mas estruturado para um possivel uso de banco na nuvem de baixo custo como exemplo firestore e etc."*  
> *Complemento de Intake:* *"o que acha de usar o db de código aberto o Supabase?"*

---

## 1. Visão Geral e Alinhamento Estratégico

O objetivo deste requisito é prover ao ecossistema multi-agent (`deep-agents-copilot`) uma infraestrutura robusta, resiliente e de baixo custo para **captura e persistência contínua de todo e qualquer incidente** ocorrido durante a execução de workflows operacionais (erros de ferramentas, exceções de runtime, falhas de testes, quebras de paridade, acionamento de circuit breakers e intervenções humanas).

### Princípios Inegociáveis (Ground Truth)
1. **Local-First com Zero Latência:** Toda gravação ocorre primariamente em banco de dados local leve embutido (SQLite em modo WAL com colunas de busca rápida e payload estruturado em JSON1).
2. **Fail-Safe Absoluto:** A camada de persistência de incidentes nunca deve derrubar, interromper ou degradar a execução do workflow principal. Falhas de gravação devem ser capturadas silenciosamente com log de emergência.
3. **Interoperabilidade Documental Dual (Supabase PostgreSQL JSONB & Cloud NoSQL):** A estrutura do registro de incidente adota o padrão canônico documental JSON Schema, permitindo sincronização direta sem transformação complexa para **Supabase (PostgreSQL JSONB / REST)** e **Firebase Firestore**.
4. **Padrão Outbox Assíncrono:** Os incidentes são gravados localmente com `sync_status = "PENDING_SYNC"`, permitindo sincronização em lote para a nuvem sob demanda ou em background, sem exigir conexão de internet para a operação dos agentes.
5. **Sanitização de Segurança (PII & Secrets Scrubbing):** Antes de qualquer gravação local ou envio para a nuvem, chaves de API, senhas, tokens e credenciais devem ser automaticamente mascarados (`[REDACTED]`).

---

## 2. Requisitos Funcionais (EARS)

### REQ-001 [EARS - Ubíquo]: Captura Contínua de Incidentes nos Workflows
O sistema deve interceptar e registrar todo e qualquer incidente de execução enfrentado por qualquer agente durante qualquer fase dos 8 Workflows Canônicos (R-050).
- **Rastreabilidade:** *"preciso que durante todo o problema enfrentado por quaisquer agent durante um workflow seja persistido"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Interceptação automática de erro em step de workflow
    Dado que um agente executor (ex.: specialist-feature-developer) falha ao executar uma ferramenta ou sofre uma exceção
    Quando o evento de falha ou retry ocorre
    Então um registro de incidente deve ser gerado contendo agente, etapa, tipo de falha e timestamp.
  ```

### REQ-002 [EARS - Estado]: Persistência Primária em Banco Local SQLite com JSON1
Enquanto um workflow estiver em execução, todos os incidentes gerados devem ser persistidos localmente em um banco de dados SQLite (`.workflow-db/incidents.db`) contendo colunas indexadas de consulta rápida (`id`, `workflow_id`, `agent_id`, `severity`, `category`, `status`, `created_at`) e o payload completo serializado em formato JSON estruturado (compatível com JSON1).
- **Rastreabilidade:** *"seja persistido em um banco local"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Persistência local imediata em arquivo SQLite
    Dado que um incidente foi interceptado
    Quando a operação de gravação é solicitada
    Então o incidente deve ser inserido na tabela 'workflow_incidents' do banco local .workflow-db/incidents.db
    E o arquivo de banco de dados deve ser gerenciado no workspace sem requerer servidor de banco em execução.
  ```

### REQ-003 [EARS - Evento]: Estruturação Canônica do Incidente em Schema Documental
Quando um incidente for capturado, o motor deve formatá-lo conforme o schema canônico neutro (`docs/schemas/workflow-incident.schema.json`) contendo: identificadores únicos (`incident_id`, `workflow_id`, `session_id`), contexto (`target_project`, `target_files`, `active_skill`), detalhes do erro (`error_type`, `message`, `stack_trace`, `tool_call`) e estado de resolução (`status`, `retry_count`, `action_taken`).
- **Rastreabilidade:** *"mas estruturado para um possivel uso de banco na nuvem de baixo custo"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Conformidade estrutural do registro de incidente
    Dado um incidente formatado pelo motor de telemetria
    Quando o registro é validado contra o JSON Schema canônico
    Então a validação deve passar com 100% de conformidade
    E todos os campos obrigatórios devem estar presentes.
  ```

### REQ-004 [EARS - Evento]: Cobertura da Trilha Completa de Incidentes
Quando houver qualquer uma das seguintes ocorrências em um workflow, o sistema deve classificar e persistir o incidente na categoria apropriada:
1. `TOOL_FAILURE`: Erro de execução de ferramenta (tool call error, exit code != 0).
2. `RUNTIME_EXCEPTION`: Exceção não tratada capturada durante execução ou compilação.
3. `CIRCUIT_BREAKER`: Acionamento de circuit breaker determinístico (ex.: teto de reprodução ou retries excedido).
4. `PARITY_BREAK`: Divergência entre testes de caracterização Golden Master e nova implementação.
5. `QUALITY_GATE_FAILURE`: Reprovação em quality gate (testes quebrados, falha de linter, security check).
6. `HUMAN_ESCALATION`: Interrupção de automação para decisão/aprovação humana obrigatória.
- **Rastreabilidade:** *"durante todo o problema enfrentado por quaisquer agent"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Registro de acionamento de circuit breaker
    Dado que uma rotina de teste atinge 3 tentativas sem sucesso e aciona o circuit breaker
    Quando o evento é sinalizado
    Então um incidente da categoria 'CIRCUIT_BREAKER' com severidade 'HIGH' deve ser persistido no banco local.
  ```

### REQ-005 [EARS - Evento]: Padrão Outbox para Sincronização Assíncrona com Nuvem
Quando um incidente for inserido no banco local, ele deve receber o atributo `sync_status = "PENDING_SYNC"`; um serviço de sincronização dedicado (ou comando `/sync-incidents`) deve ser capaz de ler os registros pendentes e transmiti-los em lote para a nuvem sem interferir na performance dos agentes.
- **Rastreabilidade:** *"estruturado para um possivel uso de banco na nuvem de baixo custo como exemplo firestore e etc."*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Atualização de status pós-sincronização
    Dado que existem 5 incidentes com sync_status = 'PENDING_SYNC' no banco local
    Quando o processo de sincronização com o banco remoto é executado com sucesso
    Então os registros locais devem ter seu status atualizado para 'SYNCED' e data de sincronização preenchida.
  ```

### REQ-006 [EARS - Opcional]: Mapeamento Nativo para Supabase (PostgreSQL JSONB) e Firestore
Onde credenciais de banco remoto estiverem configuradas, o motor de sincronização deve suportar o envio tanto para **Supabase** (tabela relacional com coluna JSONB via REST/PostgREST API) quanto para **Firebase Firestore** (coleção documental direta `workflow_incidents`).
- **Rastreabilidade:** *"o que acha de usar o db de código aberto o Supabase?"*
- **Prioridade:** Should Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Sincronização para Supabase via PostgREST
    Dado que a URL e API Key do Supabase estão presentes no ambiente
    Quando o lote de incidentes é enviado
    Então a API REST do Supabase deve persistir os registros na tabela 'workflow_incidents' preservando o payload JSONB.
  ```

### REQ-007 [EARS - Indesejado]: Resiliência e Isolamento contra Falhas de Persistência (Fail-Safe)
Se a conexão com o banco local SQLite falhar (ex.: disco cheio, lock temporário) ou a conexão com a nuvem estiver indisponível, então o motor de persistência deve capturar o erro internamente, escrever uma linha em log de contingência (`.workflow-db/fallback.log`) e **NUNCA** lançar exceção que interrompa a execução da tarefa do agente.
- **Rastreabilidade:** *"Fail-Safe operacional"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Falha de escrita no banco não aborta o workflow
    Dado que o arquivo de banco de dados SQLite está temporariamente bloqueado
    Quando o agente tenta registrar um incidente
    Então o sistema deve registrar a falha no log de contingência
    E a execução da tarefa principal do agente deve prosseguir sem interrupção.
  ```

### REQ-008 [EARS - Evento]: Pareamento de Resolução e Destilação de Lição Aprendida
Quando um erro previamente registrado for superado ou corrigido pelo agente (ex.: teste passa de vermelho para verde, ou retry bem-sucedido), o sistema deve atualizar o incidente com o diagnóstico de causa raiz (`root_cause`), o diff da correção (`successful_patch`) e uma síntese de lição aprendida (`lesson_learned`), permitindo a consulta preventiva em execuções futuras.
- **Rastreabilidade:** *"esse banco de dados vai ser nao só para observabilidade mas para que os agents aprendam com os erros"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Atualização de resolução pós-sucesso
    Dado que um incidente com status 'RETRYING' ou 'OPEN' existe no banco local
    Quando o agente aplica a correção com sucesso
    Então o incidente deve ser atualizado para status 'RESOLVED'
    E deve conter a causa raiz e a lição aprendida destilada para reutilização.
  ```

### REQ-009 [EARS - Evento]: Purge e Liberação de Espaço no Banco (Storage Pruning)
Quando uma lição aprendida for promovida para memória estável/governança ou atingir o critério de expiração definido (ex.: incidentes resolvidos após retenção configurável), o motor de persistência deve excluir os registros de incidentes brutos do banco Supabase e do SQLite local (executando DELETE e VACUUM local), liberando espaço em disco e mantendo o consumo do banco sempre sob controle.
- **Rastreabilidade:** *"precisamos de um mecanismo de liberar espaço no banco(Supabase), por exemplo apos o agent aprender com erro, o registro desse error deve ser excluido"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Exclusão de incidentes resolvidos e liberados de espaço
    Dado que existem incidentes com status 'RESOLVED' e lições já assimiladas no banco
    Quando a rotina de purge/pruning é acionada
    Então os registros brutos devem ser excluídos do Supabase e do SQLite local
    E o espaço em disco deve ser compactado.
  ```

---

## 3. Requisitos Não-Funcionais (FURPS+)

### RNF-001 [Performance]: Gravação Local Ultrarrápida (<5ms)
A gravação de incidentes no SQLite local em modo WAL (Write-Ahead Logging) não deve adicionar latência perceptível à execução dos agentes, com tempo de escrita de transação inferior a 5 milissegundos por evento.
- **Prioridade:** Must Have

### RNF-002 [Reliability]: Transacionalidade e Isolamento Local ACID
O banco de dados local deve garantir propriedades ACID para evitar corrupção de dados em caso de encerramento abrupto do processo de IA ou falha do editor IDE.
- **Prioridade:** Must Have

### RNF-003 [Portability]: Interoperabilidade Documental Neutra
O schema dos incidentes deve ser estritamente agnóstico de fornecedor de nuvem:
- Compatibilidade nativa com colunas `JSONB` do PostgreSQL (Supabase / RDS).
- Compatibilidade nativa com documentos do Firebase Firestore.
- Compatibilidade nativa com arquivos JSON/JSONL para auditoria humana direta.
- **Prioridade:** Must Have

### RNF-004 [Security / Privacy]: Sanitização Automática de Dados Sensíveis
O motor de persistência deve aplicar compulsoriamente um filtro de sanitização em expressões regulares para substituir credenciais, senhas, Bearer tokens, chaves SSH e API keys pelo valor `[REDACTED]` antes de gravar no disco ou enviar para a nuvem.
- **Prioridade:** Must Have

---

## 4. Matriz de Priorização (MoSCoW)

| ID | Nome do Requisito | Tipo | Prioridade |
|---|---|:---:|:---:|
| **REQ-001** | Captura Contínua de Incidentes nos Workflows | Funcional | **Must Have** |
| **REQ-002** | Persistência Primária em Banco Local SQLite com JSON1 | Funcional | **Must Have** |
| **REQ-003** | Estruturação Canônica do Incidente em Schema Documental | Funcional | **Must Have** |
| **REQ-004** | Cobertura da Trilha Completa de Incidentes | Funcional | **Must Have** |
| **REQ-005** | Padrão Outbox para Sincronização Assíncrona com Nuvem | Funcional | **Must Have** |
| **REQ-006** | Mapeamento Nativo para Supabase (PostgreSQL JSONB) e Firestore | Funcional | **Should Have** |
| **REQ-007** | Resiliência e Isolamento contra Falhas de Persistência (Fail-Safe) | Funcional | **Must Have** |
| **REQ-008** | Pareamento de Resolução e Destilação de Lição Aprendida | Funcional | **Must Have** |
| **REQ-009** | Purge e Liberação de Espaço no Banco (Storage Pruning) | Funcional | **Must Have** |
| **RNF-001** | Gravação Local Ultrarrápida (<5ms) | Não-Funcional | **Must Have** |
| **RNF-002** | Transacionalidade e Isolamento Local ACID | Não-Funcional | **Must Have** |
| **RNF-003** | Interoperabilidade Documental Neutra | Não-Funcional | **Must Have** |
| **RNF-004** | Sanitização Automática de Dados Sensíveis | Não-Funcional | **Must Have** |

---

## 5. Próximo Passo do Workflow

- **Etapa Concluída:** Etapa 2 — Elicitação de Requisitos (`@requirements-analyst`)
- **Próxima Etapa:** Etapa 3 — Technical Blueprint & Contratos (`@tech-solution-architect`)
  - Ação: Elaborar o Technical Blueprint com DDL SQLite, JSON Schema do incidente (`workflow-incident.schema.json`), contrato de interface do repositório Outbox e adapter de sincronização para Supabase / Firestore.

