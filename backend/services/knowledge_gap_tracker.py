"""
Knowledge Gap Tracker
======================
Detects when a patient query cannot be answered from the existing vector store
and logs it as a "knowledge gap" for the admin to review and seed later.

A gap is detected when:
  - Hallucination score > 0.55  (model is clearly reasoning off-evidence)
  - AND the best retrieval score < 0.6  (evidence is not actually relevant)

Gaps are saved to: logs/knowledge_gaps.jsonl  (one JSON object per line)
They can be reviewed via GET /api/v1/admin/knowledge-gaps
"""

import json
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

GAPS_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "logs", "knowledge_gaps.jsonl"
)

os.makedirs(os.path.dirname(GAPS_LOG_PATH), exist_ok=True)


def _is_knowledge_gap(hallucination_score: float, retrieval_scores: list) -> bool:
    """
    Returns True when the evidence is clearly off-topic.
    Conditions:
      - hallucination_score > 0.55  (LLM auditor says claims are unsupported)
      - best retrieval score < 0.70  (top-ranked chunk is not very relevant)
    Both conditions must be true simultaneously to avoid false positives.
    """
    if not retrieval_scores:
        return hallucination_score > 0.55

    best_score = max(retrieval_scores)
    avg_score  = sum(retrieval_scores) / len(retrieval_scores)

    return hallucination_score > 0.55 and avg_score < 0.70


def log_knowledge_gap(
    query: str,
    hallucination_score: float,
    retrieval_scores: list,
    hallucination_flags: list,
    specialty: str = "General",
) -> bool:
    """
    Checks whether the query represents a knowledge gap.
    If so, appends a structured record to logs/knowledge_gaps.jsonl.

    Returns True if a gap was logged, False otherwise.
    """
    if not _is_knowledge_gap(hallucination_score, retrieval_scores):
        return False

    best_score = max(retrieval_scores) if retrieval_scores else 0.0
    avg_score  = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0

    gap_record = {
        "timestamp":         datetime.now(timezone.utc).isoformat(),
        "query":             query,
        "specialty_guess":   specialty,
        "hallucination_score": round(hallucination_score, 3),
        "best_retrieval_score": round(best_score, 3),
        "avg_retrieval_score":  round(avg_score, 3),
        "flags":             hallucination_flags[:3],  # top 3 flags only
        "status":            "pending_review",          # admin can set to "seeded" or "ignored"
    }

    try:
        with open(GAPS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(gap_record) + "\n")
        logger.warning(
            f"[KNOWLEDGE GAP] Query not covered by vector store: '{query[:80]}...' "
            f"(hallucination={hallucination_score:.2f}, best_retrieval={best_score:.2f}) "
            f"-- Logged to {GAPS_LOG_PATH}"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to log knowledge gap: {e}")
        return False


def get_all_gaps() -> list[dict]:
    """Read all logged knowledge gaps from disk."""
    if not os.path.exists(GAPS_LOG_PATH):
        return []
    gaps = []
    with open(GAPS_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    gaps.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    # Newest first
    return sorted(gaps, key=lambda g: g.get("timestamp", ""), reverse=True)


def mark_gap_seeded(query_prefix: str) -> int:
    """Mark all gaps matching a query prefix as seeded (admin utility)."""
    if not os.path.exists(GAPS_LOG_PATH):
        return 0
    updated = 0
    lines = []
    with open(GAPS_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("query", "").startswith(query_prefix):
                record["status"] = "seeded"
                updated += 1
            lines.append(json.dumps(record))
    with open(GAPS_LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return updated
