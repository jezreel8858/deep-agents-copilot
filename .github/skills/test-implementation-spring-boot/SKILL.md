---
name: test-implementation-spring-boot
description: 
  Padrões consolidados para implementação de testes em Spring Boot com JUnit 5
  e Mockito, incluindo unit tests, integration tests e testes de repositório.
tier: 2
category: testing
triggers:
  - "spring boot testing"
  - "junit 5"
  - "mockito"
  - "spring integration test"
  - "repository test spring"
  - "service test spring boot"
  - "controller test mockmvc"
  - "jacoco"
  - "mvn test"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/instructions/spring-boot-backend.instructions.md
  - .github/skills/test-implementation-backend/SKILL.md
tools: []
---

# Test Implementation — Spring Boot / JUnit 5 / Mockito

> **Escopo**: implementação específica para stack **Java + Spring Boot 3+ + JUnit 5 + Mockito + JaCoCo**.
> Para padrões agnósticos de backend, consulte `test-implementation-backend`.

## Contexto

Stack de referência:
- **Jakarta EE** (`jakarta.servlet`, não `javax`)
- **Mockito** via `@ExtendWith(MockitoExtension.class)`
- **@SpringBootTest** apenas para testes de integração real
- **Test Slices** (`@WebMvcTest`, `@DataJpaTest`) para testes rápidos e isolados
- **Transações** isoladas por teste (`@Transactional` com rollback)
- **JaCoCo** para relatórios de cobertura

## 1) Unit Tests — JUnit 5 + Mockito

### Padrão Base (Service)

```java
@ExtendWith(MockitoExtension.class)
class [Entidade]ServiceImplTest {
  
  @Mock
  private [Entidade]Repository [entidade]Repository;
  
  @Mock
  private UsuarioService usuarioService;
  
  @InjectMocks
  private [Entidade]ServiceImpl [entidade]Service;
  
  @BeforeEach
  void setUp() {
    // Setup de mocks e estado inicial
  }

  @Test
  @DisplayName("Deve salvar [entidade] quando dados válidos")
  void deveSalvar_quandoDadosValidos() {
    // Arrange
    [Entidade]DTO dto = [Entidade]DTO.builder()
        .campo("valor-valido")
        .build();
    [Entidade] entidadeSalva = [Entidade].builder().id(1L).build();
    
    when([entidade]Repository.save(any([Entidade].class)))
        .thenReturn(entidadeSalva);
    
    // Act
    [Entidade] resultado = [entidade]Service.salvar(dto);
    
    // Assert
    assertNotNull(resultado);
    assertEquals(1L, resultado.getId());
    verify([entidade]Repository).save(any([Entidade].class));
  }

  @Test
  @DisplayName("Deve lançar BusinessException quando dados inválidos")
  void deveLancar_BusinessException_quandoDadosInvalidos() {
    // Arrange
    [Entidade]DTO dto = [Entidade]DTO.builder().campo(null).build();
    
    // Act & Assert
    assertThrows(BusinessException.class,
      () -> [entidade]Service.salvar(dto));
    
    verify([entidade]Repository, never()).save(any());
  }
}
```

### Checklist de Unit Test

- [ ] Todos os métodos públicos testados (happy path + edge cases)
- [ ] Exceções testadas com `assertThrows`
- [ ] Mocks com `when().thenReturn()` ou `doThrow()`
- [ ] Verification com `verify()` e `times()`
- [ ] `@BeforeEach` com setup comum
- [ ] PT-BR em `@DisplayName`
- [ ] Cobertura: ≥ 80% linhas, ≥ 70% ramos

### Usando ArgumentCaptor

```java
@Test
@DisplayName("Deve validar argumentos ao salvar")
void deveValidarArgumentos_aoSalvar() {
  ArgumentCaptor<[Entidade]> captor = ArgumentCaptor.forClass([Entidade].class);
  
  when([entidade]Repository.save(any())).thenReturn(new [Entidade]());
  
  [entidade]Service.salvar(dto);
  
  verify([entidade]Repository).save(captor.capture());
  assertEquals("valor-esperado", captor.getValue().getCampo());
}
```

### Testando Exceções Específicas

```java
// BusinessException (regra de negócio)
BusinessException ex = assertThrows(BusinessException.class,
  () -> [entidade]Service.salvar(dtoInvalido));
assertEquals("Mensagem esperada", ex.getMessage());

// IntegrationException (falha de integração)
when([entidade]Repository.save(any()))
  .thenThrow(new DataIntegrityViolationException("FK constraint"));
assertThrows(IntegrationException.class,
  () -> [entidade]Service.salvar(dto));
```

## 2) Repository Tests — @DataJpaTest

### Test Slice com H2 In-Memory

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
class [Entidade]RepositoryTest {
  
  @Autowired
  private [Entidade]Repository [entidade]Repository;
  
  @Autowired
  private TestEntityManager entityManager;
  
  @Test
  @DisplayName("Deve retornar [entidade] por campo único")
  void deveRetornarPorCampoUnico() {
    [Entidade] entidade = [Entidade].builder().campo("valor").build();
    entityManager.persistAndFlush(entidade);
    
    Optional<[Entidade]> resultado = [entidade]Repository.findByCampo("valor");
    
    assertTrue(resultado.isPresent());
    assertEquals("valor", resultado.get().getCampo());
  }

  @Test
  @DisplayName("Deve retornar lista vazia quando nenhum registro encontrado")
  void deveRetornarListaVazia_quandoNenhumRegistroEncontrado() {
    List<[Entidade]> resultado = [entidade]Repository.findAll();
    assertThat(resultado).isEmpty();
  }
}
```

## 3) Controller Tests — @WebMvcTest

### HTTP Mock Testing com MockMvc

```java
@WebMvcTest([Entidade]Controller.class)
class [Entidade]ControllerTest {
  
  @Autowired
  private MockMvc mockMvc;
  
  @Autowired
  private ObjectMapper objectMapper;
  
  @MockBean
  private [Entidade]Service [entidade]Service;
  
  @Test
  @DisplayName("Deve retornar 200 OK ao buscar [entidade]")
  void deveRetornar200_aoBuscar() throws Exception {
    [Entidade] entidade = [Entidade].builder().id(1L).build();
    when([entidade]Service.obterPorId(1L)).thenReturn(entidade);
    
    mockMvc.perform(get("/v1/[entidades]/1")
        .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.id").value(1L));
  }

  @Test
  @DisplayName("Deve retornar 400 Bad Request com validação falha")
  void deveRetornar400_comValidacaoFalha() throws Exception {
    mockMvc.perform(post("/v1/[entidades]")
        .contentType(MediaType.APPLICATION_JSON)
        .content("{}"))
        .andExpect(status().isBadRequest());
    
    verify([entidade]Service, never()).salvar(any());
  }
}
```

## 4) Integration Tests — @SpringBootTest

### Full Context (apenas para integração real)

```java
@SpringBootTest
@Transactional
class [Entidade]IntegrationTest {
  
  @Autowired
  private [Entidade]Repository [entidade]Repository;
  
  @Autowired
  private [Entidade]Service [entidade]Service;
  
  @Test
  @DisplayName("Deve criar e buscar [entidade] end-to-end")
  void deveCriarEBuscarE2E() {
    [Entidade] entidade = [Entidade].builder().campo("valor").build();
    [Entidade] salvo = [entidade]Repository.save(entidade);
    
    assertNotNull(salvo.getId());
    assertTrue([entidade]Repository.findById(salvo.getId()).isPresent());
  }
}
```

## 5) Coverage Targets (JaCoCo)

| Métrica | Mínimo | Ideal |
|---|---|---|
| Linhas | 70% | 80%+ |
| Ramos | 60% | 70%+ |
| Funções | 75% | 85%+ |

## 6) Comandos Maven / JaCoCo — Execução com Zero Ruído (R-008 / R-049)

> **ATENÇÃO**: É terminantemente proibido rodar `mvn test` bare no terminal (despeja centenas de linhas de logs INFO, Spring banner e download de plugins no contexto). Utilize sempre o padrão silencioso com filtro ou Think-in-Code via `ctx_execute`.

### A) Via `ctx_execute` (Think-in-Code — Recomendado)

```javascript
const { execSync } = require('child_process');
try {
  const out = execSync('mvn test -Dtest=[Entidade]ServiceImplTest -q', { encoding: 'utf8' });
  console.log(out.trim() || 'BUILD SUCCESS — 0 failures');
} catch (err) {
  const full = (err.stdout || '') + '\n' + (err.stderr || '');
  console.log(full.split('\n').filter(l => /(FAILURE|ERROR|<<<|Tests run)/.test(l)).slice(0, 30).join('\n'));
}
```

### B) Via Terminal com Filtro Obrigatório

```bash
# Apenas uma classe (modo silencioso + filtro)
./mvnw test -Dtest=[Entidade]ServiceImplTest -q 2>&1 | grep -E "ERROR|FAILURE|BUILD|Tests run" | head -40

# Apenas um método específico
./mvnw test -Dtest=[Entidade]ServiceImplTest#deveSalvar_quandoDadosValidos -q 2>&1 | grep -E "ERROR|FAILURE|BUILD|Tests run" | head -40

# Com relatório JaCoCo (batch mode silencioso)
./mvnw test jacoco:report -B -q 2>&1 | grep -E "ERROR|FAILURE|BUILD|Tests run" | head -40

# Em PowerShell / Windows:
mvn test -Dtest=[Entidade]ServiceImplTest -q
```

## 7) Test Data Builders (Pattern)

```java
public class [Entidade]TestBuilder {
  private [Entidade] entidade;
  
  public [Entidade]TestBuilder() {
    this.entidade = [Entidade].builder()
        .campo("valor-padrao")
        .build();
  }
  
  public [Entidade]TestBuilder comCampo(String campo) {
    entidade.setCampo(campo);
    return this;
  }
  
  public [Entidade] build() { return entidade; }
}
```

## 8) AssertJ (mais expressivo que assertEquals)

```java
import static org.assertj.core.api.Assertions.*;

assertThat(resultado)
  .isNotNull()
  .extracting([Entidade]::getCampo)
  .asString()
  .startsWith("valor");
```

## 9) Anti-padrões

- ❌ `@SpringBootTest` para unit tests puros (lento)
- ❌ Shared state entre testes (não use `static`)
- ❌ Testes interdependentes (cada deve rodar isolado)
- ❌ Sem `@Transactional` em testes de integração com BD (evita sujeira)
- ❌ Cobertura <70% sem justificativa de risco

## Referências

- JUnit 5: https://junit.org/junit5/docs/current/user-guide/
- Mockito: https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html
- Spring Testing: https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing
- JaCoCo: https://www.eclemma.org/jacoco/

