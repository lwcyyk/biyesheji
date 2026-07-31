#!/usr/bin/env python3
"""Perform dependency-free structural checks on the generated thesis DOCX."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": WORD_NS, "m": MATH_NS}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("document")
    parser.add_argument(
        "--output",
        default="test-results/g7/documents/thesis-docx-validation.json",
    )
    return parser.parse_args()


def paragraph_text(paragraph: ElementTree.Element) -> str:
    nodes = paragraph.findall(".//w:t", NS) + paragraph.findall(".//m:t", NS)
    return "".join(node.text or "" for node in nodes)


def main() -> None:
    args = parse_args()
    document_path = Path(args.document)
    output_path = Path(args.output)
    required_entries = {
        "[Content_Types].xml",
        "word/document.xml",
        "word/styles.xml",
        "word/settings.xml",
        "docProps/core.xml",
    }
    required_texts = [
        "基于 VDNS 的可验证密码生命周期管理与隐私审计方法研究",
        "摘要",
        "Abstract",
        "第一章 绪论",
        "第八章 系统实现与实验评估",
        "结论",
        "参考文献",
        "AEAD 保护密码内容，VDNS 保护密码控制过程",
    ]

    with zipfile.ZipFile(document_path) as archive:
        bad_member = archive.testzip()
        names = set(archive.namelist())
        missing = sorted(required_entries - names)
        document_xml = archive.read("word/document.xml")

    root = ElementTree.fromstring(document_xml)
    paragraphs = root.findall(".//w:body/w:p", NS)
    text = "\n".join(paragraph_text(paragraph) for paragraph in paragraphs)
    missing_text = [value for value in required_texts if value not in text]
    headings = [
        paragraph
        for paragraph in paragraphs
        if paragraph.find("./w:pPr/w:pStyle", NS) is not None
        and (
            paragraph.find("./w:pPr/w:pStyle", NS).get(f"{{{WORD_NS}}}val", "")
            .lower()
            .startswith("heading")
        )
    ]
    tables = root.findall(".//w:tbl", NS)
    equations = root.findall(".//m:oMath", NS) + root.findall(".//m:oMathPara", NS)
    drawings = root.findall(".//w:drawing", NS)
    page_size = root.find(".//w:sectPr/w:pgSz", NS)
    page_width = page_size.get(f"{{{WORD_NS}}}w") if page_size is not None else None
    page_height = page_size.get(f"{{{WORD_NS}}}h") if page_size is not None else None
    unresolved_placeholders = re.findall(r"_{5,}|TODO|TBD|待补充", text)

    passed = (
        bad_member is None
        and not missing
        and not missing_text
        and len(headings) >= 30
        and len(tables) >= 6
        and len(equations) >= 10
        and len(drawings) >= 3
        and page_width in {"11906", "11907"}
        and page_height in {"16838", "16839", "16840"}
        and not unresolved_placeholders
    )
    result = {
        "schemaVersion": "1.0.0",
        "result": "PASSED" if passed else "FAILED",
        "document": str(document_path),
        "bytes": document_path.stat().st_size,
        "sha256": hashlib.sha256(document_path.read_bytes()).hexdigest(),
        "zipIntegrity": "PASSED" if bad_member is None else f"FAILED:{bad_member}",
        "missingRequiredEntries": missing,
        "missingRequiredText": missing_text,
        "headingCount": len(headings),
        "tableCount": len(tables),
        "equationCount": len(equations),
        "drawingCount": len(drawings),
        "pageSizeTwips": {"width": page_width, "height": page_height},
        "unresolvedPlaceholders": unresolved_placeholders,
        "validationMode": "OOXML_STRUCTURE_ONLY",
        "limitation": (
            "LibreOffice/Word rendering is unavailable; pagination, font substitution, "
            "cross-references and final school-template compliance require visual review."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not passed:
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print("thesis-docx-validation-ok")


if __name__ == "__main__":
    main()
