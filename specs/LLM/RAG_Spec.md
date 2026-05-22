# RAG Specification – LFP Classification Assistant

## Approved Sources
- Institutional knowledge base: `kb/lfp_age_classification/`
  - `age_group_patterns.md` – describes typical LFP patterns by age group
  - `methodology.md` – explains preprocessing and model architecture
  - `faq.md` – frequently asked questions about the system
- Public neuroscience references (approved, read-only)
  - `pubmed/` – relevant peer-reviewed articles on LFP and age

## Chunking Strategy
- **Chunk size**: 300 tokens (±50)
- **Overlap**: 50 tokens (approximately 17%)
- **Chunk metadata fields**: `source`, `title`, `date_ingested`, `access_level`

## Retrieval Method
- **Primary**: Hybrid (vector + keyword) using sentence embeddings (all-MiniLM-L6-v2) and BM25
- **Reranker**: Cross-encoder (ms-marco-MiniLM-L-12-v2) – applied to top 20 candidates, returns top 5
- **Filter**: Apply access_level filter before retrieval; only return chunks with `access_level` ≤ user's role
- **Top-K**: default 5

## Grounding Rules
1. Every claim in the `answer` field must be supported by at least one source from the retrieval results.
2. If no relevant chunk is found (empty retrieval), set `requires_human_review = true` and respond with "I cannot find supporting information."
3. The model must never fabricate citations; all `sources` entries must correspond to actually retrieved document IDs.
4. Responses based only on model parametric knowledge (no retrieved evidence) are prohibited when answering about specific data or policies.

## Injection Protection
- All retrieved text is wrapped in `<retrieved>` tags in the prompt template.
- System instructions are placed in `<system>` tags.
- The prompt template explicitly distinguishes the two sections.
- No instruction-like patterns from retrieved text are passed to the model without sanitization.