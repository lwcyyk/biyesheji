"""Fetch public source copies; failed access remains an explicit unresolved item."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import urllib.request

REV = Path(__file__).resolve().parent
SOURCES = [
    ('oxley', 'https://www.math.ens.psl.eu/~benoist/refs/Oxley.pdf'),
    ('nissim_weinreb', 'https://www.iacr.org/archive/tcc2006/38760526/38760526.pdf'),
    ('nissim_weinreb_mirror', 'https://citeseerx.ist.psu.edu/document?doi=71ff34d99e6ce5153af88a06477efdd8fa06917c&repid=rep1&type=pdf'),
    ('arithmetic_sketching', 'https://ntt-research.com/wp-content/uploads/2023/08/Arithmetic-Sketching.pdf'),
    ('decode_2026', 'https://eprint.iacr.org/2026/946.pdf')]


def fetch(item):
    key, url = item
    record = {'id': key, 'url': url, 'version': 'unverified until content inspection'}
    try:
        with urllib.request.urlopen(url, timeout=25) as response: data = response.read()
        if not data.startswith(b'%PDF'): raise ValueError('response is not a PDF')
        target = REV / 'sources' / (key + '.pdf')
        with target.open('xb') as f: f.write(data)
        record.update(status='DOWNLOADED_NOT_YET_READ', bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as error: record.update(status='UNRESOLVED_ACCESS', error=str(error))
    return record


if __name__ == '__main__':
    (REV / 'sources').mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool: records = list(pool.map(fetch, SOURCES))
    with (REV / 'sources/access_log.json').open('x') as f: json.dump(records, f, indent=2)
    print(json.dumps(records))
