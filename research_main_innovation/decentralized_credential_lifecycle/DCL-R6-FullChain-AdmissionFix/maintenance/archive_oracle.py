"""Independent ordinary ZIP oracle; no imports from archive_check."""
import hashlib,json,stat,struct,unicodedata,zipfile

def inspect(path,raw,cap,manifest_name='out/EVIDENCE_MANIFEST.json',binding=None):
    """Return a separate ACCEPT/REJECT, with bounded parser/index and stream IO."""
    try:
        with open(path,'rb') as f:
            f.seek(0,2);end=f.tell()
            if end<22 or end>2**25:raise ValueError('compressed length')
            f.seek(end-22);q=f.read(22)
        e=struct.unpack('<4s4H2IH',q)
        if e[0]!=b'PK\x05\x06' or any(e[k] for k in [1,2,7]) or e[3]!=e[4] or e[4]>cap or e[4]>=65535 or e[5]+e[6]+22!=end or e[5]>e[4]*1582:raise ValueError('directory')
        if len(raw)>2**22:raise ValueError('manifest bytes')
        def unique(items):
            d=dict(items)
            if len(d)!=len(items):raise ValueError('duplicate JSON')
            return d
        m=json.loads(raw,object_pairs_hook=unique)
        if binding is not None and m.get('binding')!=binding:raise ValueError('binding')
        records=m['files']
        if isinstance(records,list):
            expected={r['archive_path']:{'bytes':r['bytes'],'sha256':r['sha256']} for r in records}
            if len(expected)!=len(records):raise ValueError('duplicate manifest path')
        else:expected=dict(records)
        if manifest_name in expected:raise ValueError('self cycle')
        expected[manifest_name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        def legal(s):
            return isinstance(s,str) and 0<len(s.encode())<=1024 and not s.startswith('/') and not any(c in s for c in ['\\',':','\x00']) and all(x not in ('','.','..') for x in s.split('/')) and unicodedata.normalize('NFC',s)==s
        if not all(legal(s) for s in expected) or len(expected)>cap:raise ValueError('names')
        size_sum=0
        with zipfile.ZipFile(path) as z:
            if len(z.infolist())!=e[4] or len(z.namelist())!=len(set(z.namelist())) or set(z.namelist())!=set(expected):raise ValueError('set')
            for item in z.infolist():
                r=expected[item.filename];mode=item.external_attr>>16
                if not legal(item.filename) or item.is_dir() or stat.S_IFMT(mode) not in [0,stat.S_IFREG] or item.flag_bits&1 or item.compress_type not in [0,8] or len(item.extra)>256 or len(item.comment)>256:raise ValueError('type')
                if type(r['bytes']) is not int or not 0<=r['bytes']<=2**25 or item.file_size!=r['bytes']:raise ValueError('size')
                if 'mode' in r and stat.S_IMODE(mode)!=r['mode']:raise ValueError('mode')
                got=hashlib.sha256();item_size=0
                with z.open(item) as stream:
                    for _ in range((2**25)//32768+2):
                        block=stream.read(32768)
                        if not block:break
                        got.update(block);size_sum+=len(block);item_size+=len(block)
                        if size_sum>2**25 or item_size>r['bytes']:raise ValueError('stream bound')
                    else:raise ValueError('iterations')
                if item_size!=r['bytes'] or got.hexdigest()!=r['sha256']:raise ValueError('hash')
        return {'decision':'ACCEPT','members':len(expected),'bytes':size_sum}
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,RuntimeError,NotImplementedError) as ex:
        return {'decision':'REJECT','reason':type(ex).__name__+':'+str(ex)}
