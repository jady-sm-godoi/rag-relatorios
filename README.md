# Agente de IA para Geração de Relatórios Técnicos

Este projeto implementa um agente de Inteligência Artificial autônomo, construído com a biblioteca `agno-ai`, capaz de gerar relatórios técnicos detalhados a partir de uma base de conhecimento diversificada, incluindo código-fonte, documentos de texto, PDFs e transcrições de áudio.

O agente atua como um "Arquiteto de Software" virtual, analisando os arquivos fornecidos para reconstruir a lógica de uma solução e documentá-la de forma estruturada, seguindo um formato pré-definido.

## Como Funciona

O fluxo de trabalho do projeto é orquestrado em algumas etapas principais:

1.  **Coleta de Dados**: O usuário popula as pastas `docs/` com arquivos de texto, código e PDFs, e a pasta `audios/` com arquivos de áudio que contêm informações relevantes (ex: gravações de reuniões de planejamento).

2.  **Transcrição de Áudio (Ferramenta)**: Ao ser executado, o agente primeiro verifica a pasta `audios/`. Se encontrar arquivos, ele utiliza a ferramenta `transcribe_audios` (implementada em `audio2text.py`) para transcrevê-los para texto. O resultado é salvo em um arquivo `.txt` dentro da pasta `docs/`, tornando-se parte da base de conhecimento.

3.  **Criação da Base de Conhecimento (RAG)**: O script `agente.py` lê todos os arquivos da pasta `docs/`. Ele utiliza uma estratégia de `SemanticChunking` para dividir os documentos em pedaços com coesão semântica, converte esses pedaços em vetores (embeddings) e os armazena em um banco de dados vetorial (`LanceDB`).

4.  **Execução do Agente**: Com a base de conhecimento pronta, o agente é inicializado. Ele recebe uma persona e instruções detalhadas (de `instructions.py`) e uma tarefa principal (do arquivo `prompts/prompt_relatorio.txt`).

5.  **Geração do Relatório**: O agente executa a tarefa. Usando a técnica de RAG (`search_knowledge=True`), ele busca na base de conhecimento vetorial as informações mais relevantes para cada seção do relatório que precisa escrever, garantindo que a resposta seja fundamentada nos dados fornecidos.

6.  **Exportação**: O relatório final, formatado em Markdown, é salvo na pasta `relatorios_exportados/` com um timestamp para garantir que nenhum trabalho anterior seja sobrescrito.

## Estrutura do Projeto

```
rag-relatorios/
├── audios/                  # Coloque seus arquivos de áudio aqui (.mp3, .wav, etc.)
├── docs/                    # Coloque sua base de conhecimento aqui (.py, .js, .txt, .md, .pdf)
├── prompts/
│   └── prompt_relatorio.txt # O prompt principal que define a tarefa do agente.
├── relatorios_exportados/   # Os relatórios gerados em .md são salvos aqui.
├── tmp/                     # Armazena o banco de dados vetorial (LanceDB).
├── .env                     # Arquivo para variáveis de ambiente (ex: OPENAI_API_KEY).
├── .gitignore
├── agente.py                # Script principal que orquestra todo o processo.
├── audio2text.py            # Utilitário e ferramenta para transcrição de áudio.
├── instructions.py          # "System Prompt" que define a persona e o comportamento do agente.
└── requirements.txt         # Dependências do projeto.
```

## Pré-requisitos

-   Python 3.9+
-   `pip` (gerenciador de pacotes do Python)
-   **FFmpeg**: A biblioteca `pydub` (usada em `audio2text.py`) requer o FFmpeg para processar diferentes formatos de áudio.
    -   **No Ubuntu/Debian**: `sudo apt-get install ffmpeg`
    -   **No macOS (com Homebrew)**: `brew install ffmpeg`
    -   **No Windows**: Baixe o executável no site oficial e adicione-o ao PATH do sistema.

## Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd rag-relatorios
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # venv\Scripts\activate    # No Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e adicione sua chave da API da OpenAI:
    ```env
    OPENAI_API_KEY="sk-..."
    ```

## Como Usar

1.  **Adicione seus arquivos**:
    -   Coloque todos os documentos, códigos-fonte e PDFs que servirão de base para o relatório na pasta `docs/`.
    -   Se tiver áudios, coloque-os na pasta `audios/`.
    -   **Importante**: Para que o agente possa analisar o histórico de desenvolvimento, gere um arquivo com os logs do Git. Dentro do seu repositório Git, execute o comando abaixo e mova o arquivo gerado para a pasta `docs/`:
        ```bash
        # Gera um arquivo com o patch dos últimos 5 commits
        git log -p -n 5 > historico_commits.txt
        ```
        > Você pode ajustar o número `-n 5` para capturar mais ou menos commits, conforme necessário.

2.  **Customize o prompt (opcional)**:
    -   Edite o arquivo `prompts/prompt_relatorio.txt` para ajustar o formato do relatório ou as instruções da tarefa principal.
    -   Edite `instructions.py` se quiser alterar a persona ou o comportamento geral do agente.

3.  **Execute o agente**:
    No seu terminal, com o ambiente virtual ativado, execute o script principal:
    ```bash
    python agente.py
    ```

4.  **Verifique o resultado**:
    O script exibirá o progresso no terminal. Ao final, uma mensagem indicará que o relatório foi salvo com sucesso na pasta `relatorios_exportados/`.

## Componentes Chave

-   **`agente.py`**: O coração do projeto. Ele configura a base de conhecimento, inicializa o agente e gerencia o fluxo de execução.
-   **`audio2text.py`**: Expõe a funcionalidade de transcrição como uma `tool` para o agente. Ele lida com a divisão de áudios longos em partes menores (`chunks`) para contornar limitações de APIs de reconhecimento de fala.
-   **`instructions.py`**: Define a "personalidade" e as diretrizes de alto nível do agente. É crucial para garantir que o resultado seja técnico, preciso e bem estruturado.
-   **`prompt_relatorio.txt`**: Funciona como a "tarefa do usuário". É um prompt flexível que pode ser facilmente modificado sem alterar o código Python, permitindo adaptar o objetivo do relatório para diferentes contextos.

---

*Este projeto utiliza a biblioteca agno-ai para a criação do agente.*