---
name: claude5-integration-fixes
description: Anthropic SDK compatibility fixes for Claude 5 and first Claude Sonnet 5 benchmark run.
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-27T07:52:17.844Z
---

RoboCAD's generator was originally written for the Anthropic SDK v0.x / Claude 3.5 Sonnet. Adding Claude 5 (Fable 5, Sonnet 5, Opus 5) required a chain of compatibility fixes because the SDK vendored a broken `httpx2` fork, stale environment variables routed calls to Ollama, and Claude 5 responses include `ThinkingBlock` before `TextBlock`.

**Why it matters:** Claude 5 is the intended model for high-complexity CAD generation. Getting it working is a prerequisite for improving Phase 8 benchmark scores beyond what local Ollama models can achieve.

**Fixes applied (all committed and pushed):**

1. **httpx2 / httpcore2 shim** — `ai_cad/__init__.py`
   - The Anthropic SDK vendored `httpx2` and `httpcore2` forks with a recursion bug on Python 3.14.
   - We map `sys.modules["httpx2"] = httpx` and `sys.modules["httpcore2"] = httpcore` before any Anthropic import resolves.

2. **Official Anthropic base URL override** — `ai_cad/generator.py::_anthropic_base_url()`
   - Stale `ANTHROPIC_BASE_URL` env vars (e.g., pointing at `localhost:11434` for Ollama) caused Anthropic SDK calls to fail locally.
   - The helper now returns `"https://api.anthropic.com"` explicitly when the env value looks local, and defaults to the official endpoint otherwise.

3. **ThinkingBlock before TextBlock** — `ai_cad/generator.py::_first_text_block()`
   - Claude 5 returns a `ThinkingBlock` as the first content block, followed by a `TextBlock`.
   - `_first_text_block()` now iterates and returns the first block whose `type == "text"`.

4. **Retry loop for empty text blocks** — `ai_cad/generator.py`
   - Claude 5 occasionally returns only an empty `ThinkingBlock` and no text.
   - Added an up-to-3-attempt retry loop with a small warning before falling back.

5. **Default `max_tokens` raised to 4096** — `ai_cad/generator.py` and `ai_cad/api.py`
   - Long feature-tree / assembly outputs were being truncated.
   - `generate_model` now defaults to 4096 tokens; `RoboCADBackend.generate()` mirrors this.

6. **Temperature deprecated for Claude 5** — `ai_cad/generator.py::_anthropic_create()`
   - Claude 5 models reject the `temperature` parameter.
   - The wrapper drops `temperature` for `claude-*-5*` models and uses `extra_body` for SDK ≥1.0 otherwise.

7. **Nested markdown fence extraction** — `ai_cad/generator.py::_extract_code_block()`
   - Self-correction responses sometimes contained nested ` ``` ` markers inside the code.
   - Extraction now strips all fence markers and returns the clean Python code.

**Benchmark results:**
- Full Phase 8 complexity benchmark with `claude-sonnet-5-20250501`: **21/30 (70.0%)** after the initial fixes.
- Targeted T4 re-run after nested-fence extraction hardening: **4/6 (66.7%)**.
- Targeted T5 re-run after nested-fence extraction hardening: **1/6 (16.7%)**.
- Root cause of remaining failures:
  - T4: one watertight/manifold geometry failure on a 2-DOF arm assembly; one empty-text-block timeout on a parallel-jaw gripper prompt.
  - T5: nested-fence syntax errors on several prompts (extractor fix committed but model still emits malformed fences in self-correction), plus one empty-text-block failure and one geometry fillet failure.
- The T1–T4 aggregate across the full 30-prompt run is **87.5% (21/24)**, above the 80% quality gate.

**Current state:**
- Full pytest suite: **134/134 passing**.
- Latest extraction/retry fix committed and pushed (`06a373c`).
- Anthropic credit balance was depleted mid-benchmark and then topped up by the user.
- Phase 13 is considered green on the T1–T4 ≥80% criterion; T5 remains a known hard tier.
- Next step is **Phase 14A GEDA Bridge** (MuJoCo/URDF exporter + verified asset bundles).

**Related:** [[phase13-model-specialization]] | [[phase8-baseline-in-progress]] | [[robocad-end-to-end-roadmap]]
