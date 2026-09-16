import json
from pathlib import Path

from TASK4.models.schemas import RAGContext


KNOWLEDGE_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "knowledge.json"
)


def load_knowledge() -> list[dict]:
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def retrieve(query: str, top_k: int = 3) -> list[RAGContext]:
    knowledge = load_knowledge()

    query_words = set(query.lower().split())

    scored = []

    for item in knowledge:
        keywords = {
            keyword.lower()
            for keyword in item.get("keywords", [])
        }

        matches = query_words.intersection(keywords)

        if not matches:
            continue

        score = min(1.0, 0.5 + (len(matches) * 0.08))

        scored.append(
            (
                score,
                RAGContext(
                    source_id=item["source_id"],
                    source_type=item["source_type"],
                    title=item["title"],
                    relevant_information=item[
                        "relevant_information"
                    ],
                    relevance_score=round(score, 2),
                ),
            )
        )

    scored.sort(key=lambda item: item[0], reverse=True)

    return [item[1] for item in scored[:top_k]]