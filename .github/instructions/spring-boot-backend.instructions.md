---
applyTo: ["**/*.java"]
---

# Convenções de Código — Java/Spring Boot

> Resumo consolidado das convenções de backend para projetos Java/Spring Boot. Use este documento como referência principal para padrões de código; consulte `CLAUDE.md` e `.github/copilot-instructions.md` apenas para governança geral.
>
> **Instruções genéricas**: este arquivo é reutilizável por qualquer projeto Java/Spring Boot. Customizações específicas de projeto (schemas, transaction managers, typos legados) devem ser adicionadas via adapter próprio em `.github/instructions/<projeto>-spring-boot-backend.instructions.md`.

### Padrões Gerais

- Todo código, comentários, logs e documentação do domínio devem ser escritos em Português do Brasil.
- Prefira nomenclatura Java consistente com o contexto de negócio e com o padrão do projeto.

### Entity

- Usar `@Entity`, `@Builder`, `@Data`, `@NoArgsConstructor`, `@AllArgsConstructor`.
- Preferir `@EmbeddedId` para PK composta (exceção conhecida: entidades legadas com `@Id Long` — verificar schema do projeto).
- Flags devem ser `String` com valores `"S"`/`"N"`.
- Datas em entidades seguem padrão legado com `java.util.Date`.
- Usar `jakarta.persistence` (não `javax`).

### Service

- Estrutura padrão: interface + implementação (`XxxService` + `XxxServiceImpl`).
- Injeção por construtor com `@RequiredArgsConstructor` e campos `private final`.
- Logging com `@Log4j2` e placeholders (`log.info("... {}", valor)`).
- Registre início e fim das operações públicas em PT-BR; evite `String.format` em logs.
- Exceções de negócio: `BusinessException`; integração: `IntegrationException`.
- Prefira `@RequiredArgsConstructor` com `private final`; não use `@Autowired` nem `@AllArgsConstructor` em services.

### Controller

- Versionamento de rota em `/v1/`.
- Injetar sempre interface de serviço, nunca implementação concreta.
- Declarar `@ResponseStatus(HttpStatus.OK)` explicitamente.
- Usar OpenAPI v3 (`@Tag`, `@Operation`, `@Parameter`) quando aplicável.
- Assinaturas devem manter `throws BusinessException` quando for regra do módulo.

### Exceções e validação

- Centralize o tratamento de erro com `@RestControllerAdvice` e `@ExceptionHandler`.
- Trate explicitamente `BusinessException`, `IntegrationException`, validação (`MethodArgumentNotValidException`) e exceções genéricas.
- Não engula exceções; preserve a causa e registre `log.error(...)` quando necessário.

### Testes Unitários & Execução com Zero Ruído (R-008 / R-049)

- Base: JUnit 5 + Mockito (`@ExtendWith(MockitoExtension.class)`).
- Preferir padrão AAA (Arrange, Act, Assert).
- Evitar `@SpringBootTest` em teste unitário puro.
- `@DisplayName` em PT-BR descritivo.
- Para testes que dependem de contexto Spring, use `@ExtendWith(SpringExtension.class)` + `@ContextConfiguration(classes = {ClasseTestada.class})` + `@MockBean`.
- **Higiene de Execução (Zero-Noise)**: É terminantemente proibido rodar `mvn test` bare no terminal. Agentes DEVEM priorizar execução no sandbox via `ctx_execute` (Think in Code) para capturar apenas o resumo/falhas, ou utilizar modo silencioso com filtro:
  - Linux / Git Bash: `./mvnw test -Dtest=ClasseTest -q 2>&1 | grep -E "ERROR|FAILURE|BUILD|Tests run" | head -40`
  - PowerShell: `mvn test -Dtest=ClasseTest -q`

### Regras de Persistência e Banco

- Queries nativas devem usar `SCHEMA.TABELA` completo.
- Em múltiplos data sources, respeitar o `transactionManager` correto por schema.
- Evitar `getById/getOne/getReferenceById` em regra de negócio; preferir `findById(...).orElseThrow(...)`.
- Para update simples cross-schema, preferir `@Modifying` no repository.
- Antes de alterar entidades, joins, filtros ou integrações com banco, consulte a documentação de schema do projeto (ex.: `docs/database/DATABASE_SCHEMA_<PROJETO>.md`).
- Use `@Transactional(transactionManager = "<transactionManager-do-schema>")` conforme o schema do projeto; nunca misture transaction managers na mesma operação. Os nomes dos transaction managers são definidos no adapter específico do projeto.

### Guardrail de Manutenção

- Evitar blocos de código longos neste arquivo de governança.
- Se convenções detalhadas crescerem, mover para documentação dedicada por app e manter aqui só resumo + referência.

### Referências da convenção consolidada

- `CLAUDE.md` e `.github/copilot-instructions.md` para governança global.
- Este documento para as convenções genéricas de backend Java/Spring Boot.
- `docs/database/DATABASE_SCHEMA_<PROJETO>.md` para regras de persistência e consultas (nomenclatura definida pelo projeto).
- Adapter específico do projeto (ex.: `.github/instructions/<projeto>-spring-boot-backend.instructions.md`) para customizações como transaction managers, typos legados e schemas nomeados.
