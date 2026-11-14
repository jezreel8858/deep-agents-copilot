# Test Implementation — Spring Boot (Slices, Integration e Builders)

## 2–4) Repository (`@DataJpaTest`), Controller (`@WebMvcTest`) e Integration (`@SpringBootTest`)

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
