"""Evidence acquisition and local PDF inspection only. No protocol implementation."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parent


def save_response(folder, request_id, suffix, payload):
    output = folder / (request_id + suffix)
    if output.exists():
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        output = folder / (request_id + '_' + stamp + suffix)
    with output.open('xb') as stream:
        stream.write(payload)
    return output


def fetch(item):
    folder = ROOT / 'http'
    folder.mkdir(exist_ok=True)
    record = dict(item, started_utc=datetime.now(timezone.utc).isoformat())
    request = urllib.request.Request(item['url'], headers={'User-Agent': 'Academic-source-audit/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=22) as response:
            payload = response.read()
            record.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type'), bytes=len(payload))
            suffix = '.pdf' if payload.startswith(b'%PDF') else '.body'
            output = save_response(folder, item['id'], suffix, payload)
            record.update(saved=str(output.relative_to(ROOT)), sha256=hashlib.sha256(payload).hexdigest())
    except urllib.error.HTTPError as error:
        payload = error.read()
        output = save_response(folder, item['id'], '.error', payload)
        record.update(status=error.code, error=str(error), saved=str(output.relative_to(ROOT)),
                      bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    except Exception as error:
        record.update(status=None, error=type(error).__name__ + ': ' + str(error))
    record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    return record


def inspect_pdf(path):
    from pypdf import PdfReader
    reader = PdfReader(path)
    folder = ROOT / 'readings'
    folder.mkdir(exist_ok=True)
    pages = [page.extract_text() or '' for page in reader.pages]
    (folder / (path.stem + '.txt')).write_text('\n'.join(
        f'\n=== PDF PAGE {i + 1} ===\n' + page for i, page in enumerate(pages)), encoding='utf8')
    preflight = Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\scripts\pdf_read_preflight.py')
    result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(preflight), str(path)],
                            capture_output=True, text=True, encoding='utf8')
    (folder / (path.stem + '.preflight.json')).write_text(result.stdout, encoding='utf8')
    if result.stderr:
        (folder / (path.stem + '.preflight.stderr.txt')).write_text(result.stderr, encoding='utf8')
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                pages=len(pages), metadata={str(k): str(v) for k, v in (reader.metadata or {}).items()},
                preflight_returncode=result.returncode, first_page=pages[0])


if __name__ == '__main__':
    mode, input_path = sys.argv[1:3]
    items = json.loads(Path(input_path).read_text(encoding='utf-8-sig'))
    if mode == 'fetch_serial':
        for item in items:
            record = fetch(item)
            with (ROOT / 'HTTP_REQUESTS.jsonl').open('a', encoding='utf8') as log:
                log.write(json.dumps(record, ensure_ascii=False) + '\n')
            print(json.dumps(record, ensure_ascii=False), flush=True)
            time.sleep(3.2)
    elif mode == 'fetch':
        with ThreadPoolExecutor(max_workers=4) as executor:
            for record in executor.map(fetch, items):
                with (ROOT / 'HTTP_REQUESTS.jsonl').open('a', encoding='utf8') as log:
                    log.write(json.dumps(record, ensure_ascii=False) + '\n')
                print(json.dumps(record, ensure_ascii=False), flush=True)
    elif mode == 'inspect':
        results = [inspect_pdf(Path(path)) for path in items]
        (ROOT / (Path(input_path).stem + '_inventory.json')).write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding='utf8')
        for record in results:
            print(json.dumps({k: v for k, v in record.items() if k != 'first_page'}, ensure_ascii=False))
