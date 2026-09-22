# TenderCite — Sprint V0 local spike

A thin, local-only spike for extracting mandatory requirements from government RFx PDFs and comparing them against a human-annotated gold set.

## Scope

- **CLI only** for this spike. No Next.js UI, no FastAPI server.
- **Local inference only** via Ollama (`qwen3.5:latest`). No cloud AI APIs.
- **Text-layer PDFs only**. No OCR, no scanned-image PDFs.
- **One public sample pack** is provided under `packs/nsw-asc-002-rfq-001/`.
- No outbound email, no web scraping, no AusTender calls.

## Pack

- `packs/nsw-asc-002-rfq-001/sources/rft.pdf` — the source RFx PDF.
- `packs/nsw-asc-002-rfq-001/gold-rows.csv` — founder/forge gold rows.
- `packs/nsw-asc-002-rfq-001/NOTES.md` — pack-level notes and ambiguities.

## Setup

```bash
pip install -r requirements.txt
```

Ensure Ollama is running locally and the configured model is pulled:

```bash
ollama pull qwen3.5:latest
ollama list
```

## Run

### Slice A — text-layer gate

```bash
python spike/text_gate.py --pack packs/nsw-asc-002-rfq-001
```

Refuses empty or image-only PDFs.

### Slice B — extract + cite + eval

```bash
# Extract candidates (default: fast deterministic rules; optional Ollama below)
python spike/extract_candidates.py --pack packs/nsw-asc-002-rfq-001 --out spike/candidates.csv

# Optional: attempt local Ollama inference (qwen3.5:latest) with 90s/page timeout and rule fallback
python spike/extract_candidates.py --pack packs/nsw-asc-002-rfq-001 --out spike/candidates.csv --use-ollama

# Compare against gold rows
python spike/eval_against_gold.py --candidates spike/candidates.csv --gold packs/nsw-asc-002-rfq-001/gold-rows.csv

# Spot-check 5 page citations
python spike/verify_citations.py --candidates spike/candidates.csv --pdf packs/nsw-asc-002-rfq-001/sources/rft.pdf
```

## Tests

```bash
python -m pytest spike/ -v
```

## Output schema

`spike/candidates.csv`:

| column           | description                                   |
|------------------|-----------------------------------------------|
| requirement_text | Extracted candidate requirement text          |
| source_file      | Source PDF filename                           |
| page             | 1-based viewer page index from pypdf          |
| status           | Always `pending` for this spike               |

## Notes

See `spike/NOTES.md` for model substitution, per-page timings, evaluation counts, and citation verification rules.
