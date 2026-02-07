# Troubleshooting Guide

## Quick Diagnosis

Run the diagnostic script from the `backend/` directory:

```bash
cd backend
python test_api.py
```

This checks all five critical areas and tells you exactly what's wrong.

---

## Issue 1: "I encountered an issue generating a response" / 0% confidence

**Root cause:** The Anthropic API key is missing or invalid.

### Step 1 — Verify `.env` exists

```bash
ls -la backend/.env
```

If missing, create it:

```bash
cp backend/.env.example backend/.env
```

### Step 2 — Verify the API key is set

```bash
# Show first 30 chars only (don't expose the full key)
cut -c1-30 backend/.env | grep ANTHROPIC
```

You should see something like:
```
ANTHROPIC_API_KEY=sk-ant-api03
```

If it still says `your_anthropic_key_here`, replace it with your real key from
[console.anthropic.com](https://console.anthropic.com/).

### Step 3 — Test API connectivity

```bash
cd backend
python test_api.py
```

Look for step `[5/5]`. If it says `FAIL`, the error message will tell you:
- **AuthenticationError / 401** → Key is invalid or expired
- **RateLimitError / 429** → Wait and retry, or check plan limits
- **Connection error** → Check internet / firewall
- **NotFoundError / 404** → Model not available on your plan

### Step 4 — Restart the backend

After fixing `.env`, restart the server:

```bash
cd backend
python main.py
```

Watch the startup logs. You should see:
```
[INFO] banking_support: ANTHROPIC_API_KEY loaded: sk-ant-a...xxxx
[INFO] banking_support: Database initialised.
[INFO] banking_support: Multi-agent graph compiled and ready.
[INFO] banking_support: Banking Multi-Agent Support System is operational.
```

If you see `ANTHROPIC_API_KEY is missing or set to placeholder!`, the key isn't loaded.

---

## Issue 2: "I could not find specific information" (but documents exist)

**Root cause:** ChromaDB was not initialised or is corrupted.

### Check ChromaDB

```bash
ls -la backend/chroma_db/
```

If missing or empty, delete and rebuild:

```bash
rm -rf backend/chroma_db
cd backend
python main.py
```

On startup you'll see:
```
[startup] No ChromaDB found — building from knowledge base.
[vectorstore] Loaded 7 knowledge-base documents.
[vectorstore] Split into N chunks.
[vectorstore] Created new vector store at ./chroma_db with N chunks.
```

### Verify knowledge base files

```bash
wc -c backend/knowledge_base/*.txt
```

All 7 files should exist with 3,000+ bytes each:
```
 3508 account_opening.txt
 6858 app_troubleshooting.txt
 5209 branch_info.txt
 7137 credit_cards.txt
 3668 fees_refunds.txt
 7650 fraud_disputes.txt
 3204 loans_mortgages.txt
```

---

## Issue 3: Frontend can't reach backend (network error)

### Check backend is running

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status":"operational","service":"Banking Multi-Agent Support System","version":"1.0.0"}
```

### Check CORS

The backend allows requests from `localhost:5173` and `localhost:3000`.
If you changed the frontend port, update the `allow_origins` list in `backend/main.py`.

### Check proxy

The Vite dev server proxies `/api` requests to `localhost:8000`.
Verify `frontend/vite.config.js` has:
```js
proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } }
```

---

## Issue 4: Reading server logs

The backend logs every pipeline step. Watch them in real time:

```bash
cd backend
python main.py
```

For each query you'll see:
```
[INFO]  Processing query from 'John': Customer card was stolen yesterday...
[INFO]  [reformulation] Calling Claude to reformulate query...
[INFO]  [reformulation] Result: unauthorized debit credit card stolen ...
[INFO]  [search] Retrieving documents for: unauthorized debit credit ...
[INFO]  [search] Retrieved 3 chunks from: fraud_disputes.txt
[INFO]  [search] Calling Claude to generate answer...
[INFO]  [search] Answer generated (847 chars)
[INFO]  [validation] Calling Claude to validate answer...
[INFO]  [validation] Confidence score: 92%
[INFO]  Query completed in 4820ms — confidence=92%, source=fraud_disputes.txt
```

If any step shows `[ERROR]`, that's where the pipeline broke.

---

## Checklist

| Check | Command | Expected |
|-------|---------|----------|
| `.env` exists | `ls backend/.env` | File found |
| Key is real | `cut -c1-30 backend/.env` | Starts with `sk-ant-` |
| API works | `python backend/test_api.py` | `ALL CHECKS PASSED` |
| KB files | `ls backend/knowledge_base/*.txt \| wc -l` | `7` |
| ChromaDB | `ls backend/chroma_db/` | Non-empty directory |
| Backend running | `curl localhost:8000/` | `{"status":"operational"...}` |
| Frontend running | Open `localhost:5173` | UI loads |
