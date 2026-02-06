"""
RAG vector store utilities for the Banking Support System.

Handles loading knowledge-base documents, chunking them for retrieval,
and initialising / persisting a ChromaDB vector store with
sentence-transformer embeddings.

Usage:
    from rag.vectorstore import (
        load_knowledge_base,
        chunk_documents,
        initialize_vectorstore,
        load_existing_vectorstore,
    )
"""

import os
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_knowledge_base() -> List[Document]:
    """Read every ``.txt`` file in the knowledge-base directory.

    Each file becomes one :class:`Document` whose ``metadata["source"]``
    is set to the filename (e.g. ``"fees_refunds.txt"``).
    """

    documents: List[Document] = []

    if not KNOWLEDGE_BASE_DIR.is_dir():
        raise FileNotFoundError(
            f"Knowledge-base directory not found: {KNOWLEDGE_BASE_DIR}"
        )

    for txt_file in sorted(KNOWLEDGE_BASE_DIR.glob("*.txt")):
        content = txt_file.read_text(encoding="utf-8")
        if content.strip():
            documents.append(
                Document(
                    page_content=content,
                    metadata={"source": txt_file.name},
                )
            )

    if not documents:
        raise ValueError("No .txt documents found in the knowledge base directory.")

    print(f"[vectorstore] Loaded {len(documents)} knowledge-base documents.")
    return documents


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """Split documents into smaller chunks for embedding.

    Uses :class:`RecursiveCharacterTextSplitter` which tries to split on
    paragraph / sentence boundaries before resorting to character counts.
    Source metadata is preserved on every chunk.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)
    print(f"[vectorstore] Split into {len(chunks)} chunks.")
    return chunks


def initialize_vectorstore(chunks: List[Document]) -> Chroma:
    """Create a new ChromaDB collection from document chunks and persist it.

    Returns the :class:`Chroma` vector store instance ready for
    ``similarity_search`` calls.
    """

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=_embeddings,
        persist_directory=CHROMA_DB_PATH,
    )
    print(f"[vectorstore] Created new vector store at {CHROMA_DB_PATH} "
          f"with {len(chunks)} chunks.")
    return vectorstore


def load_existing_vectorstore() -> Chroma:
    """Load a previously persisted ChromaDB collection from disk."""

    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=_embeddings,
    )
    print(f"[vectorstore] Loaded existing vector store from {CHROMA_DB_PATH}.")
    return vectorstore
