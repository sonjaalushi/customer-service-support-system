"""
Banking Multi-Agent Support System — FastAPI Application

Provides a REST API that accepts customer-service queries, routes them through
a three-agent LangGraph pipeline (reformulation → search → validation), logs
every interaction to SQLite, and exposes usage statistics.

Run:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import os
import time
import warnings
from contextlib import asynccontextmanager
from pathlib import Path

# Suppress warnings and set TensorFlow environment variables BEFORE any imports
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf.runtime_version')

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models.schemas import QueryRequest, QueryResponse
from database.queries_db import init_database, log_query, get_statistics
from agents.graph import create_agent_graph
from rag.vectorstore import (
    load_knowledge_base,
    chunk_documents,
    initialize_vectorstore,
    load_existing_vectorstore,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("banking_support")

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent / "knowledge_base"

# ---------------------------------------------------------------------------
# Lifespan context manager
# ---------------------------------------------------------------------------

# Will be set during startup
agent_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the database, vector store, and agent graph on startup."""

    global agent_graph

    # 0. Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_anthropic_key_here":
        logger.error(
            "ANTHROPIC_API_KEY is missing or set to placeholder! "
            "Edit backend/.env and add your real key."
        )
    else:
        masked = api_key[:8] + "..." + api_key[-4:]
        logger.info(f"ANTHROPIC_API_KEY loaded: {masked}")

    # 1. Database
    await init_database()
    logger.info("Database initialised.")

    # 2. Vector store
    if Path(CHROMA_DB_PATH).exists():
        logger.info("Existing ChromaDB found — loading from disk.")
        vectorstore = load_existing_vectorstore()
    else:
        logger.info("No ChromaDB found — building from knowledge base.")
        documents = load_knowledge_base()
        chunks = chunk_documents(documents)
        vectorstore = initialize_vectorstore(chunks)

    # 3. Agent graph
    agent_graph = create_agent_graph(vectorstore)
    logger.info("Multi-agent graph compiled and ready.")
    logger.info("Banking Multi-Agent Support System is operational.")

    yield

    # Shutdown (cleanup if needed)
    logger.info("Banking Multi-Agent Support System shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Banking Multi-Agent Support System",
    description=(
        "AI-powered customer service support with RAG and multi-agent system"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def health_check():
    """Basic health / readiness probe."""

    return {
        "status": "operational",
        "service": "Banking Multi-Agent Support System",
        "version": "1.0.0",
    }


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Run a customer-service question through the full agent pipeline."""

    if agent_graph is None:
        raise HTTPException(
            status_code=503,
            detail="Agent system is still initialising. Please try again shortly.",
        )

    logger.info(f"Processing query from '{request.rep_name}': {request.question[:80]}...")
    start_time = time.time()

    try:
        result = agent_graph.invoke({
            "original_question": request.question,
            "reformulated_query": "",
            "retrieved_context": "",
            "answer": "",
            "source_document": "",
            "confidence_score": 0,
            "validation_reasoning": "",
            "improvement_needed": "",
        })
    except Exception as exc:
        logger.error(f"Agent pipeline failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Agent pipeline failed: {exc}",
        )

    response_time_ms = int((time.time() - start_time) * 1000)
    logger.info(
        f"Query completed in {response_time_ms}ms — "
        f"confidence={result.get('confidence_score', 0)}%, "
        f"source={result.get('source_document', 'N/A')}"
    )

    # Log to database (fire-and-forget; don't fail the request on DB errors)
    try:
        await log_query({
            "rep_name": request.rep_name,
            "original_question": request.question,
            "reformulated_query": result.get("reformulated_query", ""),
            "answer": result.get("answer", ""),
            "source_document": result.get("source_document", ""),
            "confidence_score": result.get("confidence_score", 0),
            "response_time_ms": response_time_ms,
        })
    except Exception as exc:
        logger.warning(f"Failed to log query to database: {exc}")

    return QueryResponse(
        original_question=result.get("original_question", request.question),
        reformulated_query=result.get("reformulated_query", ""),
        answer=result.get("answer", ""),
        source_document=result.get("source_document", ""),
        confidence_score=result.get("confidence_score", 0),
        validation_reasoning=result.get("validation_reasoning", ""),
        improvement_needed=result.get("improvement_needed", ""),
        response_time_ms=response_time_ms,
    )


@app.get("/api/statistics")
async def statistics():
    """Return comprehensive query-log analytics."""

    try:
        stats = await get_statistics()
        return stats
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {exc}",
        )


@app.get("/api/document/{source_name}")
async def get_document(source_name: str):
    """Serve a raw knowledge-base document by name.

    ``source_name`` is converted to a filename: spaces are replaced with
    underscores and ``.txt`` is appended if missing.
    """

    filename = source_name.replace(" ", "_")
    if not filename.endswith(".txt"):
        filename += ".txt"

    file_path = KNOWLEDGE_BASE_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge base document '{filename}' not found.",
        )

    return FileResponse(
        path=str(file_path),
        media_type="text/plain",
        filename=filename,
    )


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
