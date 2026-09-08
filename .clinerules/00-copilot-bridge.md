# Unified AI Architecture Bridge (Cline, Copilot & Claude)

Você deve alinhar sua execução, personalidade, estilo de código e capacidades com a arquitetura e as diretrizes globais do projeto. Antes de iniciar qualquer tarefa, é **estritamente obrigatório** que você leia e siga a estrutura abaixo.

---

## 1. Project Context & Core Guidelines (Claude & Cline)
- **Localização Principal:** `CLAUDE.md` na raiz do repositório.
- **Instrução:**
  - Leia o arquivo `CLAUDE.md` imediatamente para entender os comandos globais do projeto (build, test, lint), estilo de código, convenções de naming e regras do ecossistema.
  - Siga todas as restrições e diretrizes operacionais definidas em `CLAUDE.md` como regras de prioridade máxima para a construção e manutenção da aplicação.

---

## 2. GitHub Copilot Instructions
- **Localização Principal:** `.github/copilot-instructions.md`
- **Instrução:**
  - Inspecione `.github/copilot-instructions.md` para absorver os padrões comportamentais, contextos de domínio e convenções específicas já estabelecidas para os assistentes de IA neste repositório.
  - Alinhe o estilo de geração de código e as respostas com as diretrizes descritas neste arquivo.

---

## 3. Custom Agents & Personas
- **Localização:** `.github/agents/` (ou perfis especialistas no diretório raiz).
- **Instrução:** Verifique se a intenção do usuário corresponde a algum perfil de agente especializado dentro dessa pasta. Se uma correspondência for encontrada, adote essa persona exata, suas restrições de sistema e seu estilo comportamental.

---

## 4. Global & Project Prompts
- **Localização:** `.github/prompts/`
- **Instrução:** Leia os prompts do sistema ou templates relevantes localizados neste diretório. Você deve aderir aos padrões de código, padrões de projeto e restrições negativas estritas definidas nesses arquivos.

---

## 5. Agent Skills & Tool Execution
- **Localização:** `.github/skills/`
- **Instrução:**
  - Cada subpasta dentro de `.github/skills/` contém um arquivo `SKILL.md` (ou arquivo de instruções equivalente).
  - Antes de escrever código, consulte a pasta da habilidade específica que corresponde à tarefa atual (ex.: testes, deploy, fluxos do Git).
  - Trate o arquivo `SKILL.md` como um checklist obrigatório e um guia de execução. Se a habilidade referenciar scripts locais, use suas ferramentas de terminal para executar esses scripts exatamente como prescrito.

---

## 6. Unified Execution Workflow
1. **Descobrir & Ler:** Escanear o arquivo `CLAUDE.md`, `.github/copilot-instructions.md` e o diretório `.github/` para mapear as regras e fluxos de trabalho existentes.
2. **Planejar:** Propor um plano de ação claro e estruturado que respeite os limites dos agentes, prompts e convenções do projeto.
3. **Executar:** Executar comandos no terminal, aplicar alterações/diffs nos arquivos e testar o código aderindo rigorosamente às diretrizes e habilidades documentadas.