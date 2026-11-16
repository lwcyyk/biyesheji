"""Read-only remote acquisition; append a new access ledger in this revision."""
from pathlib import Path
import hashlib
import json
import urllib.request

REV = Path(__file__).resolve().parent
items = [
    ('vavilov', 'https://www.mathnet.ru/php/getFT.phtml?jrnid=aa&option_lang=eng&paperid=122&what=fullt'),
    ('reflection_tori', 'https://www.cambridge.org/core/services/aop-cambridge-core/content/view/E482441E1C778AB599846D116B87D92A/S0008414X00008154a.pdf/linear-groups-generated-by-reflection-tori.pdf')]


def main():
    records = []
    for name, url in items:
        row = {'name': name, 'url': url, 'retrieved_date': '2026-11-03'}
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=25) as response: data = response.read()
            if not data.startswith(b'%PDF'): raise ValueError('not PDF')
            with (REV / 'sources' / (name + '.pdf')).open('xb') as stream: stream.write(data)
            row.update(status='DOWNLOADED', bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        except Exception as error: row.update(status='UNAVAILABLE_LOCALLY', error=str(error), web_read='selected text accessible via web tool')
        records.append(row)
    with (REV / 'sources/additional_access_log.json').open('x') as stream: json.dump(records, stream, indent=2)
    print(json.dumps(records))


if __name__ == '__main__': main()
