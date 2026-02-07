#!/usr/bin/env python3
"""
Diagnostic script for the Banking Multi-Agent Support System.

Checks environment configuration, API key validity, knowledge base
presence, and ChromaDB status.  Run from the backend/ directory:

    python test_api.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1. Environment & .env file
# ---------------------------------------------------------------------------

ENV_PATH = Path(__file__).resolve().parent / ".env"
print("=" * 60)
print("BANKING SUPPORT SYSTEM — DIAGNOSTIC CHECK")
print("=" * 60)

print(f"\n[1/5] Checking .env file at: {ENV_PATH}")
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print("  OK  .env file found and loaded.")
else:
    print("  FAIL  .env file NOT found!")
    print("        Fix: cp .env.example .env  then add your API key.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. API key presence
# ---------------------------------------------------------------------------

print("\n[2/5] Checking ANTHROPIC_API_KEY...")
api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not api_key or api_key == "your_anthropic_key_here":
    print("  FAIL  ANTHROPIC_API_KEY is missing or still set to placeholder!")
    print("        Fix: Edit backend/.env and set a real Anthropic API key.")
    print("        Format: ANTHROPIC_API_KEY=sk-ant-api03-...")
    sys.exit(1)

# Mask the key for display (show first 12 + last 4 chars)
masked = api_key[:12] + "..." + api_key[-4:] if len(api_key) > 20 else api_key[:8] + "..."
print(f"  OK  API key found: {masked}")

# ---------------------------------------------------------------------------
# 3. Knowledge base
# ---------------------------------------------------------------------------

print("\n[3/5] Checking knowledge base documents...")
kb_dir = Path(__file__).resolve().parent / "knowledge_base"
expected_files = [
    "account_opening.txt",
    "app_troubleshooting.txt",
    "branch_info.txt",
    "credit_cards.txt",
    "fees_refunds.txt",
    "fraud_disputes.txt",
    "loans_mortgages.txt",
]

missing = []
for fname in expected_files:
    fpath = kb_dir / fname
    if fpath.exists():
        size = fpath.stat().st_size
        print(f"  OK  {fname} ({size:,} bytes)")
    else:
        print(f"  FAIL  {fname} — MISSING")
        missing.append(fname)

if missing:
    print(f"\n  FAIL  {len(missing)} knowledge base file(s) missing!")
    sys.exit(1)
else:
    print(f"  OK  All {len(expected_files)} documents present.")

# ---------------------------------------------------------------------------
# 4. ChromaDB status
# ---------------------------------------------------------------------------

print("\n[4/5] Checking ChromaDB vector store...")
chroma_path = Path(os.getenv("CHROMA_DB_PATH", "./chroma_db"))
if chroma_path.exists() and any(chroma_path.iterdir()):
    file_count = sum(1 for _ in chroma_path.rglob("*") if _.is_file())
    print(f"  OK  ChromaDB directory exists at {chroma_path} ({file_count} files)")
else:
    print(f"  WARN  ChromaDB not found at {chroma_path}")
    print("        It will be auto-created on first server startup.")
    print("        This is normal for a fresh install.")

# ---------------------------------------------------------------------------
# 5. API connectivity test
# ---------------------------------------------------------------------------

print("\n[5/5] Testing Claude API call...")
try:
    from langchain_anthropic import ChatAnthropic
    from langchain.schema import HumanMessage

    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=api_key,
        temperature=0.0,
        max_tokens=100,
    )

    response = llm.invoke([HumanMessage(content="Reply with exactly: API_TEST_OK")])
    reply = response.content.strip()
    print(f"  OK  Claude responded: \"{reply}\"")
    print("  OK  API connection is working!")

except Exception as e:
    error_type = type(e).__name__
    print(f"  FAIL  API call failed!")
    print(f"        Error type: {error_type}")
    print(f"        Message:    {e}")
    print()

    if "AuthenticationError" in error_type or "401" in str(e):
        print("  Diagnosis: Your API key is INVALID or EXPIRED.")
        print("  Fix: Get a new key from https://console.anthropic.com/")
        print("       Then update ANTHROPIC_API_KEY in backend/.env")
    elif "RateLimitError" in error_type or "429" in str(e):
        print("  Diagnosis: You've hit the API rate limit.")
        print("  Fix: Wait a minute and try again, or check your plan limits.")
    elif "Connection" in error_type or "timeout" in str(e).lower():
        print("  Diagnosis: Cannot reach the Anthropic API.")
        print("  Fix: Check your internet connection and firewall settings.")
    elif "NotFoundError" in error_type or "404" in str(e):
        print("  Diagnosis: The model name may be invalid.")
        print("  Fix: Check that 'claude-sonnet-4-20250514' is available on your plan.")
    else:
        print("  Diagnosis: Unexpected error. See message above.")

    sys.exit(1)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print()
print("=" * 60)
print("ALL CHECKS PASSED")
print("=" * 60)
print()
print("Your system is correctly configured. Start the servers:")
print("  Backend:  cd backend && python main.py")
print("  Frontend: cd frontend && npm run dev")
print()
