#!/usr/bin/env python3
"""Quick test to verify all imports work correctly."""

try:
    print("Testing imports...")

    # Test agents.graph imports
    print("  - Testing agents.graph...")
    from agents.graph import create_agent_graph
    print("    ✓ agents.graph imported successfully")

    # Test agents.prompts imports
    print("  - Testing agents.prompts...")
    from agents.prompts import (
        REFORMULATION_AGENT_PROMPT,
        SEARCH_AGENT_PROMPT,
        VALIDATION_AGENT_PROMPT,
    )
    print("    ✓ agents.prompts imported successfully")

    # Test rag.vectorstore imports
    print("  - Testing rag.vectorstore...")
    from rag.vectorstore import (
        load_knowledge_base,
        chunk_documents,
        initialize_vectorstore,
        load_existing_vectorstore,
    )
    print("    ✓ rag.vectorstore imported successfully")

    # Test database imports
    print("  - Testing database.queries_db...")
    from database.queries_db import init_database, log_query, get_statistics
    print("    ✓ database.queries_db imported successfully")

    # Test models imports
    print("  - Testing models.schemas...")
    from models.schemas import QueryRequest, QueryResponse
    print("    ✓ models.schemas imported successfully")

    print("\n✅ All imports successful!")

except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

