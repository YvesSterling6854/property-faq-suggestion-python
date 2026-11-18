from dataclasses import dataclass
from typing import Any

from .infrai_gateway import InfraiGateway


@dataclass(frozen=True)
class FaqQuery:
    text: str
    property_id: str | None = None


@dataclass(frozen=True)
class FaqEntry:
    question: str
    answer: str
    kind: str
    property_id: str | None = None


class FaqSuggestionService:
    def __init__(self, gateway: InfraiGateway) -> None:
        self.gateway = gateway

    def suggest(self, query: FaqQuery, limit: int = 5) -> list[FaqEntry]:
        if not query.text.strip():
            return []
        matches = self.gateway.query(self.gateway.embedding(query.text), query.property_id, top_k=max(limit, 8))
        entries = [self._entry(m) for m in matches]
        if not entries:
            return []
        ranked = self.gateway.rerank(query.text, [e.question for e in entries], top_k=limit)
        by_question = {e.question: e for e in entries}
        ordered = [by_question[r.get("document", r.get("text", ""))] for r in ranked if r.get("document", r.get("text", "")) in by_question]
        return (ordered or entries)[:limit]

    @staticmethod
    def _entry(match: dict[str, Any]) -> FaqEntry:
        meta = match.get("metadata", match)
        return FaqEntry(meta["question"], meta["answer"], meta.get("kind", "faq"), meta.get("property_id"))

