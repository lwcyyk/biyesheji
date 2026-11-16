"""Reproducibility receipt; no claim that hashing proves mathematical novelty."""
import hashlib
import json
from pathlib import Path
import platform
import sys
import zipfile

REV=Path(__file__).resolve().parent
ROOT=REV.parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def normalize(value):
    if isinstance(value,dict):return {k:normalize(v) for k,v in value.items() if k!='solver_seconds'}
    if isinstance(value,list):return [normalize(v) for v in value]
    return value


def main():
    assert not (REV/'manifest.json').exists()
    old=REV.parent/'structural_audit_2026-11-03_r1'
    expected='11b3958fddce906dccc11c7827ab00ab522a19935794443723fa2901e8c33abe'
    assert sha(old/'delivery_manifest.json')==expected
    old_manifest=json.loads((old/'delivery_manifest.json').read_text())
    for item in old_manifest['files']:assert sha(old/item['path'])==item['sha256'],item['path']
    originals=json.loads((old/'input_receipt.json').read_text())['inputs']
    for item in originals:assert sha(ROOT/item['path'])==item['sha256'],item['path']
    replay=[]
    for left,right in [('probe01','probe02'),('minimax01','minimax02')]:
        for name in ('raw.json','summary.json'):
            a=json.loads((REV/'results'/left/name).read_text());b=json.loads((REV/'results'/right/name).read_text())
            assert normalize(a)==normalize(b)
            replay.append({'left':left+'/'+name,'right':right+'/'+name,'mathematical_results_identical':True,'excluded_fields':['solver_seconds']})
    source_paths=sorted(p for p in REV.iterdir() if p.is_file() and p.suffix in ('.py','.md'))
    snapshot=REV/'source_snapshot.zip'
    with zipfile.ZipFile(snapshot,'x',zipfile.ZIP_DEFLATED) as archive:
        for p in source_paths:
            info=zipfile.ZipInfo(p.name,date_time=(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,p.read_bytes())
    files=[{'path':str(p.relative_to(REV)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(REV.rglob('*')) if p.is_file()]
    import scipy,numpy
    manifest={'version':'novelty-search-r2','date':'2026-11-03','environment':{'python':sys.version,'platform':platform.platform(),'scipy':scipy.__version__,'numpy':numpy.__version__},
              'preserved_r1_manifest_sha256':expected,'preserved_r1_files':len(old_manifest['files']),'preserved_requested_originals':len(originals),
              'replay':replay,'files':files,'source_snapshot_sha256':sha(snapshot),
              'new_results':['single-row simulation minimax under explicit model','three-column epsilon/eta exact frontier hand proof','subfield sampler mathematical proposal'],
              'novelty_status':'NOT_ESTABLISHED_STANDARD_TOOL_COMBINATION_RISK_HIGH',
              'new_MPC_runs':0,'auth_lifecycle_writes':False,
              'unresolved':['exact priority','general multirow frontier','efficient authenticated sampler','malicious composition','full cost comparison'],
              'tests':{x:json.loads((REV/'results'/x/'summary.json').read_text()) for x in ('probe02','minimax02','boundaries01')}}
    with (REV/'manifest.json').open('x') as out:json.dump(manifest,out,ensure_ascii=False,indent=2)
    with (REV/'manifest_sha256.txt').open('x') as out:out.write(sha(REV/'manifest.json')+'  manifest.json\n')
    print(json.dumps({'pass':True,'files_hashed':len(files),'r1_files_preserved':len(old_manifest['files']),
                     'originals_preserved':len(originals),'replay_pairs':len(replay),'manifest_sha256':sha(REV/'manifest.json')}))


if __name__=='__main__':main()
