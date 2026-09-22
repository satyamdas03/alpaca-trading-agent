"""Tests for the Slice A text-layer gate."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_text_gate_cli_pass():
    """The real pack PDF must pass the text gate."""
    result = subprocess.run(
        [sys.executable, "spike/text_gate.py", "--pack", "packs/nsw-asc-002-rfq-001"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "TEXT_GATE_PASS" in result.stdout
    assert "page_count: 10" in result.stdout


def test_text_gate_refuses_empty(tmp_path):
    """A synthetic empty PDF must be refused by the gate."""
    from pypdf import PdfWriter

    pack = tmp_path / "empty-pack"
    sources = pack / "sources"
    sources.mkdir(parents=True)
    pdf_path = sources / "empty.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(str(pdf_path))

    import text_gate
    result = text_gate.gate_pack(pack)
    assert not result["ok"]
