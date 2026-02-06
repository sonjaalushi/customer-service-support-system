"""
LangGraph multi-agent orchestration for the Banking Support System.

Defines a three-node pipeline:
  1. Reformulation Agent — transforms raw customer queries into search-optimized queries
  2. Search Agent — retrieves context from the vector store and generates an answer
  3. Validation Agent — evaluates answer quality and assigns a confidence score

Usage:
    from agents.graph import create_agent_graph
    graph = create_agent_graph(vectorstore)
    result = graph.invoke({"original_question": "How do I open an account?"})
"""

import os
import re
from typing import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, END

from agents.prompts import (
    REFORMULATION_AGENT_PROMPT,
    SEARCH_AGENT_PROMPT,
    VALIDATION_AGENT_PROMPT,
)

# ---------------------------------------------------------------------------
# LLM initialisation
# ---------------------------------------------------------------------------

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.0,
    max_tokens=2048,
)

# ---------------------------------------------------------------------------
# Agent state schema
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    original_question: str
    reformulated_query: str
    retrieved_context: str
    answer: str
    source_document: str
    confidence_score: int
    validation_reasoning: str
    improvement_needed: str


# ---------------------------------------------------------------------------
# Agent node functions
# ---------------------------------------------------------------------------


def reformulation_agent(state: AgentState) -> AgentState:
    """Transform the raw customer question into a precise, keyword-rich search query."""

    prompt = REFORMULATION_AGENT_PROMPT.format(query=state["original_question"])

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        reformulated = response.content.strip()
    except Exception as e:
        # On failure, pass the original question through so the pipeline can continue
        reformulated = state["original_question"]
        print(f"[reformulation_agent] LLM call failed, using original question: {e}")

    return {**state, "reformulated_query": reformulated}


def _build_search_node(vectorstore):
    """Return a search-agent node function closed over the given vectorstore."""

    def search_agent(state: AgentState) -> AgentState:
        """Retrieve relevant context from the vector store and generate an answer."""

        query = state["reformulated_query"]

        # --- Retrieve documents from ChromaDB ---------------------------------
        try:
            docs = vectorstore.similarity_search(query, k=3)
            context_parts = []
            source_files = set()
            for doc in docs:
                source = doc.metadata.get("source", "unknown")
                source_files.add(source)
                context_parts.append(
                    f"[Source: {source}]\n{doc.page_content}"
                )
            context = "\n\n---\n\n".join(context_parts) if context_parts else ""
        except Exception as e:
            context = ""
            source_files = set()
            print(f"[search_agent] Vector store retrieval failed: {e}")

        if not context:
            return {
                **state,
                "retrieved_context": "",
                "answer": (
                    "I could not find specific information about this in our "
                    "knowledge base. Please contact XBO Bank customer service "
                    "at 1-800-926-2265 for further assistance."
                ),
                "source_document": "N/A",
            }

        # --- Call the LLM with retrieved context ------------------------------
        prompt = SEARCH_AGENT_PROMPT.format(query=query, context=context)

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            raw_answer = response.content.strip()
        except Exception as e:
            print(f"[search_agent] LLM call failed: {e}")
            return {
                **state,
                "retrieved_context": context,
                "answer": (
                    "I encountered an issue generating a response. Please "
                    "contact XBO Bank customer service at 1-800-926-2265 for "
                    "assistance."
                ),
                "source_document": ", ".join(sorted(source_files)),
            }

        # --- Parse structured answer -----------------------------------------
        answer = _extract_section(raw_answer, "Answer")
        source_document = _extract_section(raw_answer, "Source Document")

        # Fallbacks if parsing didn't find the expected headers
        if not answer:
            answer = raw_answer
        if not source_document:
            source_document = ", ".join(sorted(source_files)) if source_files else "N/A"

        return {
            **state,
            "retrieved_context": context,
            "answer": answer,
            "source_document": source_document,
        }

    return search_agent


def validation_agent(state: AgentState) -> AgentState:
    """Evaluate the generated answer for accuracy, completeness, and quality."""

    prompt = VALIDATION_AGENT_PROMPT.format(
        original_query=state["original_question"],
        reformulated_query=state["reformulated_query"],
        context=state["retrieved_context"],
        answer=state["answer"],
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_validation = response.content.strip()
    except Exception as e:
        print(f"[validation_agent] LLM call failed: {e}")
        return {
            **state,
            "confidence_score": 0,
            "validation_reasoning": f"Validation failed due to an error: {e}",
            "improvement_needed": "Validation could not be performed. Manual review required.",
        }

    # --- Parse confidence score -----------------------------------------------
    confidence_score = _parse_confidence_score(raw_validation)

    # --- Parse reasoning ------------------------------------------------------
    reasoning = _extract_section(raw_validation, "Reasoning")
    if not reasoning:
        reasoning = raw_validation

    # --- Parse improvement needed ---------------------------------------------
    improvement = _extract_section(raw_validation, "Improvement Needed")
    if not improvement:
        improvement = "None — answer meets quality threshold." if confidence_score >= 80 else "Review required."

    return {
        **state,
        "confidence_score": confidence_score,
        "validation_reasoning": reasoning,
        "improvement_needed": improvement,
    }


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def create_agent_graph(vectorstore):
    """Build and compile the three-node LangGraph pipeline.

    Args:
        vectorstore: A LangChain-compatible vector store (e.g. Chroma)
                     that exposes a ``similarity_search`` method.

    Returns:
        A compiled LangGraph ``StateGraph`` ready to be invoked with
        ``{"original_question": "..."}``.
    """

    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("reformulate", reformulation_agent)
    workflow.add_node("search", _build_search_node(vectorstore))
    workflow.add_node("validate", validation_agent)

    # Define edges: linear pipeline
    workflow.set_entry_point("reformulate")
    workflow.add_edge("reformulate", "search")
    workflow.add_edge("search", "validate")
    workflow.add_edge("validate", END)

    return workflow.compile()


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _extract_section(text: str, header: str) -> str:
    """Extract the content following a markdown-bold header like **Header:**.

    Captures everything after ``**{header}:**`` up to the next ``**...**``
    header or end of string.
    """

    pattern = rf"\*\*{re.escape(header)}:\*\*\s*(.*?)(?=\n\*\*[A-Z]|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def _parse_confidence_score(text: str) -> int:
    """Extract a numeric confidence score (0-100) from validation output.

    Looks for patterns like ``**Confidence Score:** 85%`` or just ``85%``
    near the beginning of the text.
    """

    # Try the structured format first
    pattern = r"\*\*Confidence Score:\*\*\s*(\d{1,3})\s*%"
    match = re.search(pattern, text)
    if match:
        return max(0, min(100, int(match.group(1))))

    # Fallback: first percentage near the start of the text
    pattern = r"(\d{1,3})\s*%"
    match = re.search(pattern, text[:500])
    if match:
        return max(0, min(100, int(match.group(1))))

    # If nothing could be parsed, return 0 to signal manual review
    return 0
