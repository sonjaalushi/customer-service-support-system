# Banking Multi-Agent Support System

An AI-powered customer service support tool that uses a **three-agent LangGraph pipeline** backed by **Retrieval-Augmented Generation (RAG)** to answer banking questions accurately and transparently. Built for XBO Bank's customer-service representatives.

## Features

- **Multi-Agent Pipeline** — Three specialised agents work in sequence:
  1. **Reformulation Agent** strips emotion and jargon, producing precise search queries
  2. **Search Agent** retrieves context from a vector store and synthesises a sourced answer
  3. **Validation Agent** scores accuracy, completeness, specificity, source alignment, and clarity (0-100%)
- **RAG Knowledge Base** — Seven banking-policy documents chunked and embedded in ChromaDB for fast semantic retrieval
- **Confidence Scoring** — Every answer gets a weighted quality score with colour-coded badges (Excellent / Good / Acceptable / Review Needed)
- **Manager Dashboard** — Real-time analytics with Recharts: queries per rep, confidence distribution, most-used documents, low-confidence alerts
- **Query Logging** — Every interaction is persisted to SQLite with response time, confidence, and source metadata

## Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | Claude Sonnet 4 (Anthropic) |
| Orchestration | LangGraph + LangChain |
| Vector Store | ChromaDB with sentence-transformers (`all-MiniLM-L6-v2`) |
| Backend API | FastAPI + Uvicorn |
| Database | SQLite via aiosqlite |
| Frontend | React 18 + Vite 5 |
| Styling | Tailwind CSS 3.4 |
| Charts | Recharts |

## Prerequisites

- Python 3.10+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

## Installation

### Backend

```bash
cd banking-support-system/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY

# Start the server
python main.py
```

The API will be available at `http://localhost:8000`. On first run the knowledge base is automatically chunked and embedded into ChromaDB (takes ~30 seconds).

### Frontend

```bash
cd banking-support-system/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The UI will be available at `http://localhost:5173`. API requests are proxied to the backend automatically.

## Usage

### Representative View

1. Enter your name (optional) and the customer's question
2. Click **Submit Query**
3. The system runs the three-agent pipeline:
   - Reformulates the question into banking-specific search terms
   - Retrieves relevant context from the knowledge base
   - Generates a sourced answer and validates it
4. Review the answer, confidence score, source document, and any improvement suggestions

### Manager Dashboard

- **Stats Cards** — Total queries, average confidence, average response time, active reps
- **Bar Chart** — Queries per representative
- **Pie Chart** — Confidence score distribution
- **Most Used Documents** — Top 5 knowledge-base files by query count
- **Low Confidence Alerts** — Recent queries scoring below 70%
- Auto-refreshes every 30 seconds

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/query` | Submit a question through the agent pipeline |
| `GET` | `/api/statistics` | Retrieve usage and quality analytics |
| `GET` | `/api/document/{name}` | Download a raw knowledge-base document |

### POST /api/query

**Request:**
```json
{
  "question": "How do I dispute a fraudulent charge?",
  "rep_name": "Jane Smith"
}
```

**Response:**
```json
{
  "original_question": "How do I dispute a fraudulent charge?",
  "reformulated_query": "unauthorized transaction fraud dispute process report ...",
  "answer": "XBO Bank provides Zero Liability Protection ...",
  "source_document": "fraud_disputes.txt",
  "confidence_score": 92,
  "validation_reasoning": "Answer is accurate and complete ...",
  "improvement_needed": "None — answer meets quality threshold.",
  "response_time_ms": 4820
}
```

## Project Structure

```
banking-support-system/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── graph.py              # LangGraph 3-node pipeline
│   │   └── prompts.py            # Reformulation, Search, Validation prompts
│   ├── database/
│   │   ├── __init__.py
│   │   └── queries_db.py         # Async SQLite logging & statistics
│   ├── knowledge_base/
│   │   ├── account_opening.txt
│   │   ├── app_troubleshooting.txt
│   │   ├── branch_info.txt
│   │   ├── credit_cards.txt
│   │   ├── fees_refunds.txt
│   │   ├── fraud_disputes.txt
│   │   └── loans_mortgages.txt
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic request / response models
│   ├── rag/
│   │   ├── __init__.py
│   │   └── vectorstore.py        # ChromaDB + sentence-transformers
│   ├── .env.example
│   ├── main.py                   # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnswerDisplay.jsx
│   │   │   ├── ConfidenceScore.jsx
│   │   │   ├── ManagerDashboard.jsx
│   │   │   ├── QueryInput.jsx
│   │   │   ├── RepView.jsx
│   │   │   └── StatsCard.jsx
│   │   ├── services/
│   │   │   └── api.js            # Axios API client
│   │   ├── styles/
│   │   │   └── index.css         # Tailwind directives + custom classes
│   │   ├── App.jsx               # Root component with view toggle
│   │   └── main.jsx              # React entry point
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
└── README.md
```

## Demo Guide

When demonstrating the system, follow this sequence:

1. **Start both servers** (backend then frontend)
2. **Representative View** — submit 3-4 varied questions:
   - *"A customer says someone stole money from their account"* (fraud)
   - *"What are your credit card options?"* (products)
   - *"Customer is angry about a $35 fee"* (fees/refunds)
   - *"The app keeps crashing when I try to deposit a check"* (troubleshooting)
3. **Observe the pipeline** — show the reformulated query, answer with source, and confidence score for each
4. **Switch to Manager Dashboard** — show real-time stats populating after the queries above
5. **Highlight key features**:
   - Confidence badges change colour by tier
   - Low-confidence answers trigger improvement suggestions
   - Charts and stats auto-refresh every 30 seconds
   - Source documents can be viewed with one click
