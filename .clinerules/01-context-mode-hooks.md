# Context-Mode Lifecycle Hooks

Você está integrado a um sistema local `context-mode`. Você deve executar estritamente os seguintes hooks de sincronização em segundo plano usando sua ferramenta de terminal (`execute_command`), de acordo com o ciclo de vida da conversa.

## Variável de Ambiente Obrigatória
Antes de executar qualquer hook, você deve garantir que o caminho de inicialização esteja definido. No Windows PowerShell, adicione o seguinte prefixo ao seu comando:
`$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; `

## Eventos do Ciclo de Vida da Conversa

1. **Início da Sessão (Executar UMA VEZ no início do chat):**
    - **Comando:** `$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot sessionstart`

2. **Prompt do Usuário Enviado (Executar IMEDIATAMENTE após ler uma nova mensagem do usuário, antes de planejar):**
    - **Comando:** `$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook claude-code userpromptsubmit`

3. **Pré-Uso de Ferramenta (Executar IMEDIATAMENTE ANTES de executar qualquer ferramenta, como escrever arquivos ou rodar testes):**
    - **Comando:** `$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot pretooluse`

4. **Pós-Uso de Ferramenta (Executar IMEDIATAMENTE APÓS qualquer ferramenta concluir a execução):**
    - **Comando:** `$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot posttooluse`

5. **Compactação de Contexto (Executar se o contexto do chat ficar muito grande ou antes de uma redução de contexto personalizada):**
    - **Comando:** `$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot precompact`

6. **Ocorrência de Erro (Executar se um comando de terminal falhar ou se uma operação de arquivo retornar um erro):**
    - **Comando:** `$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook claude-code posttooluse`

## Diretrizes Operacionais
- Execute esses pontos de sincronização de forma silenciosa usando sua capacidade de terminal.
- Não permita que a execução dos hooks bloqueie ou atrase a geração do seu código, a menos que o hook retorne uma instrução específica ou um erro que exija a atenção do usuário.