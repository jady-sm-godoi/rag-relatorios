from datetime import datetime  # Opcional: para nomes de arquivos únicos
from pathlib import Path

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.reader.text_reader import TextReader
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.vectordb.lancedb import LanceDb
from dotenv import load_dotenv

from audio2text import run_transcription
from instructions import agent_instructions

load_dotenv()

# --- CONFIGURAÇÃO DE CAMINHOS ---
DOCS_DIR = Path("./docs")
PROMPTS_DIR = Path("./prompts/prompt_relatorio.txt")
REPORTS_DIR = Path("./relatorios_exportados")

# 1. Configuração do Vector DB
vector_db = LanceDb(
    table_name="tech_docs_knowledge",
    uri="tmp/lancedb",
)

# 2. Base de Conhecimento
knowledge_base = Knowledge(vector_db=vector_db)

# Processamento de PDFs
if any(DOCS_DIR.glob("*.pdf")):
    knowledge_base.add_content(
        path=str(DOCS_DIR),
        reader=PDFReader(chunk_strategy=SemanticChunking()),
        skip_if_exists=True,
    )
    print("INFO: PDFs encontrados e processados.")

# Processamento de Texto e Código
text_extensions = [
    "*.txt",
    "*.md",
    "*.py",
    "*.js",
    "*.dart",
    "*.ts",
    "*.xml",
    "*.xsl",
]
if any(any(DOCS_DIR.glob(ext)) for ext in text_extensions):
    knowledge_base.add_content(
        path=str(DOCS_DIR),
        reader=TextReader(chunk_strategy=SemanticChunking()),
        skip_if_exists=True,
    )
    print("INFO: Arquivos de texto/código processados.")

# Banco de dados de histórico
db = SqliteDb(db_file="tmp/historico_agente.db")


@tool
def transcribe_audios(audio_folder: str = "audios", title: str = "") -> dict:
    """
    Transcribe all audio files inside the 'audios' folder
    and return the transcriptions
    """
    return run_transcription(audio_folder=audio_folder, title=title)


# 3. Agente Especialista
tech_writer_agent = Agent(
    name="Documentador de Soluções",
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    db=db,
    search_knowledge=True,
    instructions=agent_instructions,
    markdown=True,
    tools=[transcribe_audios],
)

# --- 4. LEITURA DO PROMPT DE ARQUIVO EXTERNO ---
prompt_file = PROMPTS_DIR

if not prompt_file.exists():
    # Cria um arquivo de exemplo se não existir para evitar erro
    PROMPTS_DIR.mkdir(exist_ok=True)
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(
            "Analise os arquivos e gere uma documentação técnica completa."
        )
    print(
        f"⚠️ Arquivo de prompt não encontrado. Criado um modelo em: {prompt_file}"
    )

# Lê o conteúdo do arquivo
with open(prompt_file, "r", encoding="utf-8") as f:
    prompt_comando = f.read()

print(f"🚀 Executando comando a partir de: {prompt_file}")

# 5. Gerar a resposta e capturar o conteúdo
response = tech_writer_agent.run(prompt_comando)

if response and response.content:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Gerando nome com timestamp para não sobrescrever (Opcional)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    file_path = REPORTS_DIR / f"documentacao_solucao_{timestamp}.md"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response.content)

    print(f"\n✅ Relatório exportado com sucesso em: {file_path}")
