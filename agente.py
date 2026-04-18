from datetime import datetime
from pathlib import Path

from agno.agent import Agent
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

# --- CONFIGURAÇÕES E CAMINHOS ---
DOCS_DIR = Path("./docs")
PROMPT_FILE = Path("./prompts/prompt_relatorio.txt")
REPORTS_DIR = Path("./relatorios_exportados")

TEXT_EXTENSIONS = [
    "*.txt",
    "*.md",
    "*.py",
    "*.js",
    "*.dart",
    "*.ts",
    "*.xml",
    "*.xsl",
]


@tool
def transcribe_audios(audio_folder: str = "audios", title: str = "") -> dict:
    """
    Transcreve todos os arquivos de áudio da pasta especificada
    e retorna as transcrições consolidadas.
    """
    return run_transcription(audio_folder=audio_folder, title=title)


def setup_knowledge_base() -> Knowledge:
    """Configura e popula a base de conhecimento com os arquivos locais."""
    vector_db = LanceDb(
        table_name="tech_docs_knowledge",
        uri="tmp/lancedb",
    )
    knowledge_base = Knowledge(vector_db=vector_db)

    # Processamento de PDFs
    if any(DOCS_DIR.glob("*.pdf")):
        knowledge_base.add_content(
            path=str(DOCS_DIR),
            reader=PDFReader(chunk_strategy=SemanticChunking()),
            skip_if_exists=True,
        )
        print("INFO: PDFs encontrados e processados.")

    # Processamento de arquivos de texto e código
    has_text_files = any(
        True for ext in TEXT_EXTENSIONS for _ in DOCS_DIR.glob(ext)
    )
    if has_text_files:
        knowledge_base.add_content(
            path=str(DOCS_DIR),
            reader=TextReader(chunk_strategy=SemanticChunking()),
            skip_if_exists=True,
        )
        print("INFO: Arquivos de texto/código processados.")

    return knowledge_base


def main():
    knowledge_base = setup_knowledge_base()

    # Configuração do Agente Especialista
    tech_writer_agent = Agent(
        name="Documentador de Soluções",
        model=OpenAIChat(id="gpt-4o"),
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=agent_instructions,
        markdown=True,
        tools=[transcribe_audios],
    )

    # Prepara o arquivo de prompt caso não exista
    if not PROMPT_FILE.exists():
        PROMPT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(
                "Analise os arquivos e gere uma documentação técnica completa."
            )
        print(
            f"⚠️ Arquivo de prompt não encontrado. Criado um modelo em: {PROMPT_FILE}"
        )

    # Lê a instrução principal
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_comando = f.read()

    print(f"🚀 Executando comando a partir de: {PROMPT_FILE}")

    # Gera a resposta com o agente
    response = tech_writer_agent.run(prompt_comando)

    # Exporta o relatório final
    if response and response.content:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        file_path = REPORTS_DIR / f"documentacao_solucao_{timestamp}.md"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.content)

        print(f"\n✅ Relatório exportado com sucesso em: {file_path}")


if __name__ == "__main__":
    main()
