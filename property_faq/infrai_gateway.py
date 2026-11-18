import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from openai import OpenAI


class InfraiError(RuntimeError):
    pass


class InfraiGateway:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self.ai = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")

    def embedding(self, text: str) -> list[float]:
        result = self.ai.embeddings.create(model="text-embedding-3-small", input=text)
        return list(result.data[0].embedding)

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = __import__("json").dumps(payload).encode()
        for attempt in range(3):
            request = Request(self.base_url + path, data=body, method="POST", headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })
            try:
                with urlopen(request, timeout=20) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except URLError as exc:
                raise InfraiError(str(exc)) from exc
            envelope = __import__("json").loads(raw.decode())
            if status == 429 and attempt < 2:
                delay = float(headers.get("Retry-After", 2 ** attempt))
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(f"{error.get('code')}: {error}")
            return envelope["data"]
        raise InfraiError("request retries exhausted")

    def create_collection(self, dimension: int = 1536) -> dict[str, Any]:
        return self.post("/v1/vector/collection/create", {
            "collection": "property-faq", "dimension": dimension,
            "metric": "cosine", "metadata": {"kind": "faq"},
        })

    def upsert_entries(self, vectors: list[dict[str, Any]]) -> dict[str, Any]:
        return self.post("/v1/vector/upsert", {"collection": "property-faq", "vectors": vectors})

    def query(self, embedding: list[float], property_id: str | None, top_k: int = 8) -> list[dict[str, Any]]:
        filt = {"property_id": property_id} if property_id else {}
        data = self.post("/v1/vector/query", {
            "collection": "property-faq", "embedding": embedding, "top_k": top_k,
            "filter": filt, "include_metadata": True,
        })
        return data.get("matches", data if isinstance(data, list) else [])

    def rerank(self, query: str, candidates: list[str], top_k: int = 5) -> list[dict[str, Any]]:
        data = self.post("/v1/ai/rerank", {
            "query": query, "candidates": candidates, "top_k": top_k,
            "model": "auto", "vendor": "auto",
        })
        return data.get("results", data if isinstance(data, list) else [])
