"""Slice A stub: check that the source PDF has a usable text layer."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader


def gate_pack(pack_dir: Path, min_chars_per_page: int = 10) -> dict:
    """Return page count and total text length; raise ValueError if no text."""
    pack_dir = Path(pack_dir)
    pdf_paths = list(pack_dir.joinpath("sources").glob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF found in {pack_dir / 'sources'}")

    # Use the first (and usually only) PDF in the pack.
    pdf_path = pdf_paths[0]
    reader = PdfReader(str(pdf_path))

    page_stats = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        page_stats.append({"page": i, "chars": len(text)})

    total_chars = sum(s["chars"] for s in page_stats)
    empty_pages = [s["page"] for s in page_stats if s["chars"] < min_chars_per_page]

    result = {
        "pdf_path": pdf_path,
        "source_file": pdf_path.name,
        "page_count": len(reader.pages),
        "total_chars": total_chars,
        "empty_pages": empty_pages,
        "ok": total_chars > 0 and not empty_pages,
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Slice A text-layer gate for a pack")
    parser.add_argument(
        "--pack",
        type=Path,
        default=Path("packs/nsw-asc-002-rfq-001"),
        help="Path to the pack directory containing sources/*.pdf",
    )
    args = parser.parse_args(argv)

    try:
        result = gate_pack(args.pack)
    except Exception as exc:
        print(f"TEXT_GATE_FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"source_file: {result['source_file']}")
    print(f"page_count: {result['page_count']}")
    print(f"total_chars: {result['total_chars']}")
    if result["empty_pages"]:
        print(f"empty_pages: {result['empty_pages']}")

    if not result["ok"]:
        print("TEXT_GATE_FAIL: PDF has no usable text layer", file=sys.stderr)
        return 1

    print("TEXT_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
