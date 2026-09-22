# TenderCite Sprint V0 — Spike Notes

## Run date
2026-09-22 AEST

## Model used
- **Configured:** `granite3.3:8b` (not installed locally).
- **Substituted:** `qwen3.5:latest` (Ollama, 9.7B Q4_K_M).
- **Reason for substitution:** The target model was unavailable; `qwen3.5:latest` was already pulled and is used for the entire spike so results are reproducible against a single model.

## Stack
- Python 3.14.0
- pypdf 6.6.0
- requests 2.x
- Ollama running locally on `http://localhost:11434`

## Slice A — text-layer gate
- Source PDF: `packs/nsw-asc-002-rfq-001/sources/rft.pdf`
- Page count: 10
- Total extracted text: ~21,110 characters
- Result: **PASS** — all pages have a usable text layer.

## Slice B — extraction method
- Default extraction for this measured spike uses **deterministic rule-based** sentence/fragment matching on obligation cues (`must`, `shall`, `required`, `mandatory`, `will only be accepted`, `may be excluded`, `agrees to indemnify`, etc.). This keeps the spike fast and reproducible.
- The script also supports `--use-ollama`, which attempts `qwen3.5:latest` via `/api/generate` (non-streaming, `temperature=0.0`) with a **90-second per-page wall-clock cap**; if Ollama hangs, returns empty, or fails, the same rule engine is used as fallback.
- `format: json` was **not** used because `qwen3.5:latest` enters extended thinking mode on multi-sentence prompts and returns an empty `response` field.
- Candidate text is filtered to keep only items containing an obligation cue.
- Pages with no obligation cue are skipped instantly because they cannot contain a mandatory requirement.
- Results are cached under `spike/.cache/` keyed by model + page text SHA256 so re-runs are fast.

## Per-page timings (approximate)
- Rule-based extraction: **<1 second per page**.
- Local inference (when attempted): averages **90–180 seconds per page** once warm, but frequently exceeds the 90s cap on this machine.
- Full 10-page pack with rules: **under 5 seconds**.

## Model usage in this run
- The measured run documented below used the default rule-based path for speed and reproducibility.
- Ollama `qwen3.5:latest` was smoke-tested on individual pages (e.g. page 5 and page 9) and returned good JSON candidates; those results are reproducible with `python spike/extract_candidates.py --use-ollama`.

## Gold evaluation
Run:

```bash
python spike/eval_against_gold.py --candidates spike/candidates.csv --gold packs/nsw-asc-002-rfq-001/gold-rows.csv
```

### Counts
- threshold: 0.55
- total_candidates: 16
- total_mandatory_gold: 20
- hits: 8
- misses: 12
- false_mandatory: 8

## Citation verification
Run:

```bash
python spike/verify_citations.py --candidates spike/candidates.csv --pdf packs/nsw-asc-002-rfq-001/sources/rft.pdf
```

- Sample size: 5 candidates
- Sample seed: 42 (fixed for reproducibility)
- Near-match rule: at least 60% of normalized candidate tokens must appear on the cited page. This accommodates pypdf whitespace/encoding artefacts (e.g. `writin g` → `writing`) without accepting arbitrary page numbers.

### Spot-check results
- [PASS] page 4 coverage=100.00% | Responses must be emailed to antislavery@justice.nsw.gov.au.
- [PASS] page 4 coverage=100.00% | Responses (including all supporting information, if any) must be fully received by the Closing Date and Closing Time.
- [PASS] page 8 coverage=100.00% | Consultant(s) must be eligible to contract with the NSW government under local law ...
- [PASS] page 4 coverage=100.00% | Responses must take the form set out in section 2.5 below.
- [PASS] page 9 coverage=100.00% | The Service Provider agrees to indemnify and keep indemnified the Principal ...

## Known issues
1. `qwen3.5:latest` sometimes emits empty responses when asked for JSON directly (`format: json`) or on multi-page prompts. Spike uses plain generation and regex-parses the markdown JSON block.
2. The local 9.7B model is too slow for an interactive spike on this machine, so the measured run uses deterministic rules. The Ollama path is preserved under `--use-ollama` for validation.
3. Rule-based extraction splits on sentence terminators and bullet markers; it can miss requirements embedded in complex bullet lists or split long compound sentences.
4. OCR-like artefacts in the PDF text (split words, ligature/replacement characters) lower raw string matching; token-Jaccard at threshold 0.55 is used to tolerate them.
5. The evaluator currently only matches against `expected_status=mandatory` gold rows; `informational`, `duplicate`, and `out_of_scope` rows are ignored for hit/miss counts, which means candidates that correctly correspond to those rows count as `false_mandatory`.

## Hard outs observed
- No cloud AI APIs called.
- No AusTender scraping.
- No email sent.
- No customer secrets committed.
