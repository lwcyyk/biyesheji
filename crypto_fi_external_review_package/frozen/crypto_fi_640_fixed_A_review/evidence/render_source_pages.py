"""Render only four source pages; source PDFs are opened read-only."""
from pathlib import Path
import hashlib
import json
import fitz

OUT = Path(__file__).resolve().parent
BASE = OUT.parents[1]
SOURCES = BASE / 'crypto_fi_640_correctness_audit' / 'sources'
records = []
for filename, pages, prefix in [
    ('FI_journal_20261110.pdf', [12, 14], 'FI'),
    ('official_frodo_2021.pdf', [10, 25], 'OFFICIAL'),
]:
    source = SOURCES / filename
    with fitz.open(source) as pdf:
        for page in pages:
            target = OUT / (prefix + '_p' + str(page) + '.png')
            pdf[page-1].get_pixmap(matrix=fitz.Matrix(1.25, 1.25), alpha=False).save(target)
            records.append({'source': str(source),
                            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                            'page_one_based': page, 'pdf_page_count': len(pdf),
                            'rendered_png': str(target),
                            'rendered_sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
(OUT/'SOURCE_PAGE_RENDERING.json').write_text(json.dumps(
    {'schema': 'fi640-fixed-A-review/source-rendering/1', 'pymupdf': fitz.VersionBind,
     'source_writes': 0, 'records': records}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Rendered four source pages from read-only PDFs.')
