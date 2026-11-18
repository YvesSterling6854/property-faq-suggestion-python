from property_faq.service import FaqEntry, FaqQuery, FaqSuggestionService


class FakeGateway:
    def embedding(self, text):
        return [0.1, 0.2]

    def query(self, embedding, property_id, top_k):
        return [{"metadata": {"question": "When should I report a water leak?", "answer": "Call maintenance.", "kind": "maintenance"}}, {"metadata": {"question": "When is the next inspection?", "answer": "See your reminder.", "kind": "inspection"}}]

    def rerank(self, query, candidates, top_k):
        return [{"document": candidates[0]}]


def test_maintenance_question_prioritizes_related_faq():
    result = FaqSuggestionService(FakeGateway()).suggest(FaqQuery("water leak in kitchen"))
    assert result == [FaqEntry("When should I report a water leak?", "Call maintenance.", "maintenance")]

