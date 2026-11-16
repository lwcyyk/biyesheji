from pathlib import Path
import json,hashlib,zipfile
from docx import Document
BASE=Path(__file__).resolve().parents[1];MAIN=Path('D:/毕业设计/研究/算法机制重构与原创性验证_2026-11-03')
SRC=MAIN/'A、B与AB三项算法原创性突破及优势验证研究报告_v1.0.docx'
d=Document(SRC);s=d.sections[0]
parts={}
with zipfile.ZipFile(SRC) as z:
 for name in z.namelist():parts[name]=hashlib.sha256(z.read(name)).hexdigest()
(BASE/'working/source_package.json').write_text(json.dumps(parts,indent=2),encoding='utf-8')
text=f'''# Reference and edit contract

Reference: {SRC}
SHA256: {hashlib.sha256(SRC.read_bytes()).hexdigest()}
Previously rendered and all 11 pages reviewed in this conversation; final prior images: {MAIN}/working/qa.
One portrait section; page {s.page_width.inches} x {s.page_height.inches} inches.
Margins top/bottom/left/right: {s.top_margin.inches}/{s.bottom_margin.inches}/{s.left_margin.inches}/{s.right_margin.inches} inches.
Header/footer distances: {s.header_distance.inches}/{s.footer_distance.inches} inches.
Normal: 11 pt Songti, Latin Times New Roman, black, 1.25 line spacing, 7 pt after.
Heading 1/2: existing black Heiti 16/12 pt. Title existing 23 pt two-line form.
Tables: visible D9D9D9 borders, DCE6EE header, alternating F5F7F9; 10 pt; repeated header; no fixed height.

Editable slots: subtitle, version paragraph, scope note; four local source-section boundary notes; append chapters 13–19 after original references. Existing first 12 chapters and experiment tables remain historical content. No existing algorithms/results or crypto audit originals changed.
Preserve-only: all package parts except word/document.xml, word/_rels/document.xml.rels, docProps/core.xml; geometry, styles, numbering, header/footer and original links retained.
Append uses existing paragraph styles and source-derived table pattern; math remains native OMML. Update PAGE through read-only Word PDF export, no source save.
Canonical LibreOffice renderer unavailable on this host; record actual fallback Word COM + PDFium. Inspect every final page.
'''
(BASE/'working/artifact.md').write_text(text,encoding='utf-8')
print('Reference edit contract prepared; no DOCX modified')
