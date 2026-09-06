---
name: spring-boot-backend-patterns
description: >-
  Diretrizes enterprise para análise e recomendação de arquitetura, operação e
  evolução de serviços backend com Spring Boot, sem implementação direta.
tier: 2
category: quality
triggers:
  - "spring boot enterprise"
  - "boas práticas spring boot"
  - "arquitetura backend spring"
  - "observabilidade spring"
  - "segurança spring boot"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/backend/spring-boot/spring-boot-router.agent.md
tools: []
---

# Spring Boot Backend Patterns

> Esta skill cobre o modo **Advisory** (análise/recomendação, sem código). Para o modo **Implementação** (codificar feature/bugfix), ver [`spring-boot-implementation-patterns`](../spring-boot-implementation-patterns/SKILL.md).

## Quando usar

- Quando houver decisão técnica sobre arquitetura e operação em Spring Boot.
- Quando for necessário revisar qualidade de configuração, startup e performance.
- Quando existir dúvida sobre compatibilidade de versão entre Spring Boot, Spring Framework e Java.
- Quando for preciso recomendar hardening e observabilidade sem alterar código.

## Pilares técnicos

| Pilar | Diretriz objetiva | Evidência mínima |
|---|---|---|
| Versionamento | Priorizar versões estáveis e suporte ativo (Spring Boot + Java LTS) | `pom.xml`/`build.gradle`, matriz de versões, release notes |
| Arquitetura | Fronteiras claras de módulos, configuração externa e perfil por ambiente | estrutura de pacotes, `application*.yml`, conventions |
| Performance | Medir startup, consumo de memória e latência antes de otimizar | baseline de métricas e comparação por cenário |
| Observabilidade | Expor métricas, health checks e tracing com padrão único | Actuator, logs estruturados, integração de telemetria |
| Segurança | Aplicar princípio de menor privilégio e defesa em profundidade | controles de autenticação/autorização, gestão de segredos, dependências |
| Migração | Planejar upgrades por fases com rollback explícito | inventário de breaking changes e plano de transição |

## Checklist verificável

- [ ] Versão de Java/JDK e Spring Boot foi identificada com evidência.
- [ ] Compatibilidade entre dependências críticas foi validada.
- [ ] Existe recomendação de observabilidade com métricas mínimas (latência, erro, saturação).
- [ ] Riscos de segurança foram priorizados por severidade.
- [ ] Existe plano de migração com fases, critério de sucesso e rollback.

## Anti-padrões

- ❌ Recomendar upgrade sem matriz de compatibilidade e janela de suporte.
- ❌ Diagnosticar performance sem baseline mensurável.
- ❌ Tratar observabilidade apenas como logging sem métricas/traces.
- ❌ Prescrever práticas específicas de projeto sem evidência contextual.

## Referências oficiais

- Spring Boot Reference: https://docs.spring.io/spring-boot/reference/
- Spring Framework Reference: https://docs.spring.io/spring-framework/reference/
- Spring Security Reference: https://docs.spring.io/spring-security/reference/
- Spring Boot Actuator: https://docs.spring.io/spring-boot/reference/actuator/
- Java SE (Oracle): https://docs.oracle.com/en/java/javase/
- OpenJDK: https://openjdk.org/projects/jdk/

