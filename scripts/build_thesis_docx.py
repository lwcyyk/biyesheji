#!/usr/bin/env python3
"""Build and style the editable VDNS-PM thesis DOCX from Markdown."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

import pypandoc
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt


TITLE = "基于 VDNS 的可验证密码生命周期管理与隐私审计方法研究"
BODY_EAST_ASIA_FONT = "宋体"
HEADING_EAST_ASIA_FONT = "黑体"
LATIN_FONT = "Times New Roman"
MONO_FONT = "Noto Sans Mono CJK SC"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="docs/论文/VDNS-PM研究生毕业论文.md",
        help="Markdown thesis source",
    )
    parser.add_argument(
        "--output",
        default="docs/论文/VDNS-PM研究生毕业论文.docx",
        help="DOCX output",
    )
    return parser.parse_args()


def set_run_font(run, latin: str, east_asia: str, size: Pt | None = None) -> None:
    run.font.name = latin
    if size is not None:
        run.font.size = size
    properties = run._element.get_or_add_rPr()
    fonts = properties.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        properties.insert(0, fonts)
    fonts.set(qn("w:ascii"), latin)
    fonts.set(qn("w:hAnsi"), latin)
    fonts.set(qn("w:eastAsia"), east_asia)
    fonts.set(qn("w:cs"), latin)


def set_style_font(style, latin: str, east_asia: str, size: Pt) -> None:
    style.font.name = latin
    style.font.size = size
    properties = style.element.get_or_add_rPr()
    fonts = properties.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        properties.insert(0, fonts)
    fonts.set(qn("w:ascii"), latin)
    fonts.set(qn("w:hAnsi"), latin)
    fonts.set(qn("w:eastAsia"), east_asia)
    fonts.set(qn("w:cs"), latin)


def add_page_field(paragraph) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    value = OxmlElement("w:t")
    value.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, value, end])
    set_run_font(run, LATIN_FONT, BODY_EAST_ASIA_FONT, Pt(9))


def configure_sections(document: Document) -> None:
    for section in document.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(25.4)
        section.bottom_margin = Mm(25.4)
        section.left_margin = Mm(30)
        section.right_margin = Mm(25.4)
        section.header_distance = Mm(12)
        section.footer_distance = Mm(12)

        header = section.header
        header.is_linked_to_previous = False
        header_paragraph = header.paragraphs[0]
        header_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        header_paragraph.text = TITLE
        for run in header_paragraph.runs:
            set_run_font(run, LATIN_FONT, BODY_EAST_ASIA_FONT, Pt(8))
            run.font.color.rgb = None

        footer = section.footer
        footer.is_linked_to_previous = False
        footer_paragraph = footer.paragraphs[0]
        footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_page_field(footer_paragraph)


def configure_styles(document: Document) -> None:
    normal = document.styles["Normal"]
    set_style_font(normal, LATIN_FONT, BODY_EAST_ASIA_FONT, Pt(12))
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.first_line_indent = Pt(24)

    style_specs = {
        "Title": (HEADING_EAST_ASIA_FONT, Pt(22)),
        "Subtitle": (HEADING_EAST_ASIA_FONT, Pt(13)),
        "Heading 1": (HEADING_EAST_ASIA_FONT, Pt(16)),
        "Heading 2": (HEADING_EAST_ASIA_FONT, Pt(14)),
        "Heading 3": (HEADING_EAST_ASIA_FONT, Pt(12)),
        "Heading 4": (HEADING_EAST_ASIA_FONT, Pt(12)),
        "Caption": (BODY_EAST_ASIA_FONT, Pt(10.5)),
    }
    for name, (east_asia, size) in style_specs.items():
        if name not in document.styles:
            continue
        style = document.styles[name]
        set_style_font(style, LATIN_FONT, east_asia, size)
        style.paragraph_format.first_line_indent = Pt(0)
        style.paragraph_format.space_before = Pt(6)
        style.paragraph_format.space_after = Pt(6)

    for code_style in ("Source Code", "Verbatim Char"):
        if code_style not in document.styles:
            continue
        set_style_font(document.styles[code_style], MONO_FONT, MONO_FONT, Pt(9))


def is_chapter_heading(text: str) -> bool:
    stripped = text.strip()
    return (
        (stripped.startswith("第") and "章" in stripped[:8])
        or stripped in {"结论", "参考文献"}
        or stripped.startswith("附录 ")
    )


def style_paragraphs(document: Document) -> None:
    title_seen = False
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        style_name = paragraph.style.name if paragraph.style is not None else ""

        if text == TITLE and not title_seen:
            paragraph.style = document.styles["Title"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_before = Pt(72)
            paragraph.paragraph_format.space_after = Pt(30)
            title_seen = True
        elif style_name.startswith("Heading"):
            paragraph.paragraph_format.first_line_indent = Pt(0)
            if is_chapter_heading(text):
                paragraph.paragraph_format.page_break_before = True
            if style_name == "Heading 1":
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif style_name in {"Caption"} or text.startswith(("图 ", "表 ")):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = Pt(0)
        elif style_name in {"Source Code", "Compact"}:
            paragraph.paragraph_format.first_line_indent = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.0
        elif text:
            paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            paragraph.paragraph_format.space_after = Pt(0)

        for run in paragraph.runs:
            if style_name in {"Source Code", "Verbatim Char"}:
                set_run_font(run, MONO_FONT, MONO_FONT, Pt(9))
            elif style_name.startswith("Heading") or style_name == "Title":
                set_run_font(
                    run,
                    LATIN_FONT,
                    HEADING_EAST_ASIA_FONT,
                    paragraph.style.font.size,
                )
            else:
                set_run_font(run, LATIN_FONT, BODY_EAST_ASIA_FONT)


def style_tables(document: Document) -> None:
    for table in document.tables:
        try:
            table.style = "Table Grid"
        except KeyError:
            pass
        for row_index, row in enumerate(table.rows):
            for cell in row.cells:
                cell.vertical_alignment = 1
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.first_line_indent = Pt(0)
                    paragraph.paragraph_format.line_spacing = 1.0
                    paragraph.paragraph_format.space_after = Pt(0)
                    if row_index == 0:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        set_run_font(
                            run,
                            LATIN_FONT,
                            HEADING_EAST_ASIA_FONT if row_index == 0 else BODY_EAST_ASIA_FONT,
                            Pt(9.5),
                        )
                        if row_index == 0:
                            run.bold = True


def build(source: Path, output: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="vdns-pm-docx-") as temp_directory:
        intermediate = Path(temp_directory) / "thesis.docx"
        pypandoc.convert_file(
            str(source),
            "docx",
            format=(
                "markdown+tex_math_dollars+tex_math_single_backslash"
                "+fenced_code_blocks+pipe_tables+link_attributes"
            ),
            outputfile=str(intermediate),
            extra_args=[
                "--standalone",
                "--toc",
                "--toc-depth=3",
                "--metadata=lang:zh-CN",
                "--metadata=toc-title:目录",
                f"--resource-path={source.parent}{os.pathsep}{Path.cwd()}",
            ],
        )
        document = Document(intermediate)
        document.core_properties.title = TITLE
        document.core_properties.subject = "VDNS-PM 研究生毕业设计论文"
        document.core_properties.author = "待按学校模板填写"
        document.core_properties.keywords = "密码管理器; VDNS; 可验证生命周期; 隐私审计"
        document.core_properties.comments = (
            "由 scripts/build-thesis-docx.sh 从冻结 Markdown 源生成。"
        )

        configure_styles(document)
        configure_sections(document)
        style_paragraphs(document)
        style_tables(document)
        document.save(output)


def main() -> None:
    args = parse_args()
    build(Path(args.input).resolve(), Path(args.output).resolve())
    print(f"thesis-docx-ok output={args.output}")


if __name__ == "__main__":
    main()
