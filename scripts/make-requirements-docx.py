#!/usr/bin/env python3
"""Render the requirements markdown into a .docx the Intent composer can attach.

The original VD-4319 defect began with a Word upload, so the fixture has to be a
real .docx: the agent's document-reading path (and the sign-off table it lifted
text from) is part of what is under test. python-docx is not a dependency here —
a .docx is a zip of OOXML parts, and the three parts below are enough for the
readers in play.

Only the constructs the document actually uses are supported: headings, body
paragraphs, bullet lists, and pipe tables. Tables matter most; the sign-off block
at the end of the document is a table, and that is the text that leaked into the
Intent's own Approvals section in the original bug.

Usage:
    python3 scripts/make-requirements-docx.py            # writes alongside the .md
    python3 scripts/make-requirements-docx.py --check    # verify without writing
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

DOCS = Path(__file__).resolve().parent.parent / "docs"
SOURCE = DOCS / "REV-2026-014-Revenue-Reporting-Requirement.md"
TARGET = DOCS / "REV-2026-014-Revenue-Reporting-Requirement.docx"

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def para(text: str, style: str | None = None) -> str:
    props = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{props}<w:r><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r></w:p>"


def table(rows: list[list[str]]) -> str:
    # A minimal grid: Word tolerates an absent tblGrid, but readers that walk
    # cells are happier with explicit borders and a width per column.
    borders = (
        "<w:tblBorders>"
        + "".join(
            f'<w:{edge} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
            for edge in ("top", "left", "bottom", "right", "insideH", "insideV")
        )
        + "</w:tblBorders>"
    )
    width = max((len(r) for r in rows), default=1)
    grid = "<w:tblGrid>" + '<w:gridCol w:w="3000"/>' * width + "</w:tblGrid>"
    body = []
    for row in rows:
        cells = "".join(
            f'<w:tc><w:tcPr><w:tcW w:w="3000" w:type="dxa"/></w:tcPr>{para(cell)}</w:tc>'
            for cell in row
        )
        body.append(f"<w:tr>{cells}</w:tr>")
    return f"<w:tbl><w:tblPr>{borders}</w:tblPr>{grid}{''.join(body)}</w:tbl>"


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def render(markdown: str) -> str:
    blocks: list[str] = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = split_row(lines[i])
                if not is_separator(cells):
                    rows.append(cells)
                i += 1
            if rows:
                blocks.append(table(rows))
            continue

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            blocks.append(para(stripped[level:].strip(), f"Heading{min(level, 3)}"))
        elif re.match(r"^[-*]\s+", stripped):
            blocks.append(para(re.sub(r"^[-*]\s+", "", stripped), "ListParagraph"))
        elif re.match(r"^\d+\.\s+", stripped):
            blocks.append(para(re.sub(r"^\d+\.\s+", "", stripped), "ListParagraph"))
        elif stripped:
            blocks.append(para(re.sub(r"[`*]", "", stripped)))
        i += 1

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}"><w:body>' + "".join(blocks) + "</w:body></w:document>"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate without writing")
    args = ap.parse_args()

    if not SOURCE.exists():
        print(f"missing source: {SOURCE}", file=sys.stderr)
        return 1

    document = render(SOURCE.read_text(encoding="utf-8"))

    # The properties the runbook depends on. A silently-empty render would make
    # the AC4 check vacuous, so fail loudly instead.
    for needle in ("Approved for build", "VP, Revenue Operations", "Chief Financial Officer"):
        if escape(needle) not in document:
            print(f"render lost a required fixture property: {needle!r}", file=sys.stderr)
            return 1

    if args.check:
        print(f"render OK ({len(document)} bytes of document.xml)")
        return 0

    with zipfile.ZipFile(TARGET, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/document.xml", document)
    print(f"wrote {TARGET.relative_to(TARGET.parent.parent)} ({TARGET.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
