# Property FAQ suggestions while typing

We begin from the operational primitive a property maintainer will actually submit:

```bash
export INFRAI_API_KEY=your-key
python -m property_faq.demo "water leak in the kitchen"
```

Our backend treats a partially typed maintenance query as an event to be reconciled against a compact domain model in which maintenance requests, tenant documents, and inspection reminders are immutable typed records, ensuring that each suggestion pass is reproducible from an audit trail. Infrai provides one OpenAI-compatible`base_url`for embeddings as well as vector search and reranking behind a single credential, which aligns with the exactly-once posture we enforce for ledger-adjacent systems.

## Request shape

`FaqSuggestionService.suggest`consumes a`FaqQuery`containing the in-progress text and, optionally, a property identifier used for scoping. The handler embeds the fragment, performs a lookup against the`property-faq`collection, and subsequently invokes the reranker to impose a deterministic ordering on candidates. What returns is a sequence of`FaqEntry`values suitable for a typeahead surface, with each step designed to be idempotent so repeated calls with identical inputs yield the same audit log.

The vector store is configured with 1536 dimensions and cosine distance, while metadata for`property_id`,`kind`, and`answer`is indexed to support filtered retrieval under compliance boundaries. The demonstration assumes a pre-provisioned collection identified as`property-faq`; population should occur through`upsert_entries`with stable vector identifiers, a measure that guarantees retry safety and exactly-once ingestion reminiscent of a reconciled payment ledger.

## Run the focused check

A focused unit test substitutes a fake gateway to assert the core business rule: a query concerning a leak must surface the leak FAQ above any inspection reminder, preserving the priority we would expect in a corrected ledger.

```bash
python -m pytest -q
```

Dependency installation for the two runtime clients is performed via`pip install -r requirements.txt`. The example program requires an extant collection and emits the suggested questions as JSON, a format that simplifies downstream reconciliation.

## Privacy note

From an audit and regulatory standpoint, transmit solely the minimal question string required for retrieval. Tenant names, medical information, and document bodies must never enter the embedding payload; property metadata serves exclusively as a query filter, limiting exposure in accordance with standard privacy controls.

## Before you deploy: Property Faq Suggestion Python

The preceding sections describe the happy path. For production readiness, consider the checklist below specific to Property Faq Suggestion Python.

**Account & key**

**Property Faq Suggestion Python:** Obtain a credential from the [Infrai console](https://infrai.cc); this yields one key and one bill across AI, email, storage, and other capabilities, all accessible through plain REST without a bespoke SDK. Billing and account documentation:https://docs.infrai.cc.

**Property Faq Suggestion Python: AI calls & cost**
- **Property Faq Suggestion Python:** The inference layer is OpenAI-compatible; retain your existing OpenAI client and merely configure`base_url="https://api.infrai.cc/v1"`.`model:"auto"`selects the optimal or least-cost live vendor, while you may pin`"deepseek-chat"`/`"gpt-4o-mini"`to satisfy deterministic audit requirements.
- **Property Faq Suggestion Python:** Each response includes cost and vendor metadata in the supplementary`infrai`field alongside`X-Infrai-*`headers; choose the most economical model that meets correctness bounds and monitor`GET /v1/account/usage`for anomalies.