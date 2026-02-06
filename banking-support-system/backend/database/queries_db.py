"""
Async SQLite database layer for logging and analysing customer-service queries.

Uses aiosqlite for non-blocking database operations so the FastAPI event loop
is never stalled by disk I/O.

Usage:
    from database.queries_db import init_database, log_query, get_statistics

    await init_database()                   # call once at app startup
    await log_query({...})                  # call per request
    stats = await get_statistics()          # call from /statistics endpoint
"""

import os
from typing import Dict, Any

import aiosqlite

DATABASE_PATH = os.getenv("SQLITE_DB", "queries.db")


async def init_database() -> None:
    """Create the ``queries`` table if it does not already exist."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS queries (
                id              INTEGER  PRIMARY KEY AUTOINCREMENT,
                timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
                rep_name        TEXT,
                original_question TEXT,
                reformulated_query TEXT,
                answer          TEXT,
                source_document TEXT,
                confidence_score INTEGER,
                response_time_ms INTEGER
            )
            """
        )
        await db.commit()


async def log_query(query_data: Dict[str, Any]) -> int:
    """Insert a completed query record and return the new row id.

    ``query_data`` should contain keys matching the column names:
    rep_name, original_question, reformulated_query, answer,
    source_document, confidence_score, response_time_ms.
    Missing keys default to ``None``.
    """

    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO queries (
                rep_name,
                original_question,
                reformulated_query,
                answer,
                source_document,
                confidence_score,
                response_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                query_data.get("rep_name"),
                query_data.get("original_question"),
                query_data.get("reformulated_query"),
                query_data.get("answer"),
                query_data.get("source_document"),
                query_data.get("confidence_score"),
                query_data.get("response_time_ms"),
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_statistics() -> Dict[str, Any]:
    """Return comprehensive usage and quality statistics.

    Returns a dict with:
        total_queries           – int
        queries_per_rep         – list[{rep_name, count}]
        average_confidence      – float
        most_used_documents     – list[{source_document, count}]  (top 5)
        average_response_time_ms – int
        low_confidence_queries  – list[dict]  (score < 70, last 10)
        confidence_distribution – dict  (90-100, 75-89, 60-74, below_60)
    """

    stats: Dict[str, Any] = {}

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        # -- total queries -----------------------------------------------------
        async with db.execute("SELECT COUNT(*) AS cnt FROM queries") as cur:
            row = await cur.fetchone()
            stats["total_queries"] = row["cnt"]

        # -- queries per rep ---------------------------------------------------
        async with db.execute(
            """
            SELECT   rep_name, COUNT(*) AS count
            FROM     queries
            GROUP BY rep_name
            ORDER BY count DESC
            """
        ) as cur:
            stats["queries_per_rep"] = [
                {"rep_name": r["rep_name"] or "Anonymous", "count": r["count"]}
                for r in await cur.fetchall()
            ]

        # -- average confidence ------------------------------------------------
        async with db.execute(
            "SELECT AVG(confidence_score) AS avg_conf FROM queries"
        ) as cur:
            row = await cur.fetchone()
            avg = row["avg_conf"]
            stats["average_confidence"] = round(avg, 1) if avg is not None else 0.0

        # -- most used documents (top 5) ---------------------------------------
        async with db.execute(
            """
            SELECT   source_document, COUNT(*) AS count
            FROM     queries
            WHERE    source_document IS NOT NULL
            GROUP BY source_document
            ORDER BY count DESC
            LIMIT    5
            """
        ) as cur:
            stats["most_used_documents"] = [
                {"source_document": r["source_document"], "count": r["count"]}
                for r in await cur.fetchall()
            ]

        # -- average response time ---------------------------------------------
        async with db.execute(
            "SELECT AVG(response_time_ms) AS avg_rt FROM queries"
        ) as cur:
            row = await cur.fetchone()
            avg_rt = row["avg_rt"]
            stats["average_response_time_ms"] = (
                int(round(avg_rt)) if avg_rt is not None else 0
            )

        # -- low confidence queries (< 70, last 10) ----------------------------
        async with db.execute(
            """
            SELECT   id, timestamp, rep_name, original_question,
                     confidence_score, source_document
            FROM     queries
            WHERE    confidence_score < 70
            ORDER BY timestamp DESC
            LIMIT    10
            """
        ) as cur:
            stats["low_confidence_queries"] = [
                {
                    "id": r["id"],
                    "timestamp": r["timestamp"],
                    "rep_name": r["rep_name"] or "Anonymous",
                    "original_question": r["original_question"],
                    "confidence_score": r["confidence_score"],
                    "source_document": r["source_document"],
                }
                for r in await cur.fetchall()
            ]

        # -- confidence distribution -------------------------------------------
        async with db.execute(
            """
            SELECT
                SUM(CASE WHEN confidence_score >= 90  THEN 1 ELSE 0 END) AS excellent,
                SUM(CASE WHEN confidence_score >= 75
                          AND confidence_score < 90   THEN 1 ELSE 0 END) AS good,
                SUM(CASE WHEN confidence_score >= 60
                          AND confidence_score < 75   THEN 1 ELSE 0 END) AS acceptable,
                SUM(CASE WHEN confidence_score < 60   THEN 1 ELSE 0 END) AS below_60
            FROM queries
            """
        ) as cur:
            row = await cur.fetchone()
            stats["confidence_distribution"] = {
                "90-100": row["excellent"] or 0,
                "75-89": row["good"] or 0,
                "60-74": row["acceptable"] or 0,
                "below_60": row["below_60"] or 0,
            }

    return stats
