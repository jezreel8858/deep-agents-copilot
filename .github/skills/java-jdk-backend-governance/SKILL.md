---
name: java-jdk-backend-governance
description: >-
  Boas práticas de governança para versões Java/JDK em backend enterprise,
  cobrindo LTS, compatibilidade de ecossistema, performance, segurança e migração.
tier: 1
category: governance
triggers:
  - "java lts"
  - "versão jdk backend"
  - "migração java"
  - "compatibilidade jdk"
  - "hardening jvm"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/backend/spring-boot/spring-boot-router.agent.md
  - .github/agents/backend/spring-reactive/spring-reactive-router.agent.md
tools: []
---

# Java/JDK Backend Governance

## Quando usar

- Quando for necessário definir versão-alvo de Java para backend.
- Quando houver planejamento de upgrade de JDK em ambiente corporativo.
- Quando a análise envolver compatibilidade entre framework, build tool e runtime.
- Quando a recomendação exigir equilíbrio entre performance, segurança e previsibilidade operacional.

## Diretrizes principais

| Tema | Diretriz | Critério verificável |
|---|---|---|
| LTS | Priorizar versões LTS com suporte ativo e política clara de atualização | versão atual vs alvo documentada e prazo de suporte mapeado |
| Compatibilidade | Validar matriz JDK × framework × bibliotecas × plataforma de execução | tabela de compatibilidade com riscos e bloqueios |
| Performance | Baseline antes/depois para startup, heap, GC e latência | métricas comparativas e regressões aceitas/rejeitadas |
| Segurança | Aplicar updates de segurança e monitorar CVEs do ecossistema Java | inventário de dependências e ciclo de patching |
| Migração | Executar migração faseada com canário e rollback | plano em etapas com critérios de aprovação |
| Operação | Padronizar flags JVM e observabilidade por ambiente | perfil JVM versionado e telemetria mínima definida |

## Checklist de decisão

- [ ] Versão LTS recomendada com justificativa temporal de suporte.
- [ ] Dependências críticas avaliadas quanto a compatibilidade.
- [ ] Impacto de GC/heap/startup medido em ambiente representativo.
- [ ] Plano de atualização de segurança e CVEs definido.
- [ ] Estratégia de migração com rollback validada.

## Referências oficiais

- Oracle Java SE Support Roadmap: https://www.oracle.com/java/technologies/java-se-support-roadmap.html
- Oracle Java SE Documentation: https://docs.oracle.com/en/java/javase/
- OpenJDK JEP Index: https://openjdk.org/jeps/0
- OpenJDK Release Process: https://openjdk.org/projects/jdk/
- Eclipse Adoptium (distribuições): https://adoptium.net/

