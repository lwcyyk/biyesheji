"""Seal new proof artifacts; preserve all old research material."""
from pathlib import Path
import hashlib,json,platform,sys,zipfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not (HERE/'manifest.json').exists()
    previous=[]
    for name,manifest in [('structural_audit_2026-11-03_r1','delivery_manifest.json'),('novelty_search_2026-11-03_r2','manifest.json'),('multirow_explore_2026-11-03_r3','manifest.json'),('incidence_structure_2026-11-03_r4','manifest.json')]:
        folder=HERE.parent/name;data=json.loads((folder/manifest).read_text())
        for record in data['files']:assert sha(folder/record['path'])==record['sha256'],record['path']
        previous.append({'revision':name,'files_verified':len(data['files']),'manifest_sha256':sha(folder/manifest)})
    original=json.loads((HERE.parent/'structural_audit_2026-11-03_r1/input_receipt.json').read_text())['inputs']
    for record in original:assert sha(ROOT/record['path'])==record['sha256']
    paper=ROOT.parent/'3-3-4.pdf';assert sha(paper)=='8688a088693f77ca84525520081357cd5d838ffdb04a662c01d67a4c52668f37'
    dependencies=[HERE.parent/'novelty_search_2026-11-03_r2/frontier_probe.py',HERE.parent/'multirow_explore_2026-11-03_r3/kernel_minimax.py']
    with zipfile.ZipFile(HERE/'source_snapshot.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.md'))+dependencies:
            name=path.name if path.parent==HERE else 'readonly_dependencies/'+path.parent.name+'/'+path.name
            info=zipfile.ZipInfo(name,date_time=(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,path.read_bytes())
    import scipy,numpy,sympy
    result={'version':'general-arc-r5','date':'2026-11-03','python':sys.version,'platform':platform.platform(),
            'libraries':{'scipy':scipy.__version__,'numpy':numpy.__version__,'sympy':sympy.__version__},
            'previous_revisions_unchanged':previous,'original_ten_inputs_unchanged':True,'provided_paper_unchanged':True,
            'dependencies':[{'path':str(p),'sha256':sha(p)} for p in dependencies],
            'general_scope':'n>=5, q>=16n^2, three-dimensional dictionary, two mask rows, at most three failures',
            'proof_status':'self-contained hand proof plus finite exact certificates; not externally reviewed',
            'priority_status':'UNRESOLVED_NETWORK_SEARCH_FAILED','new_MPC_runs':0,'auth_lifecycle_writes':False,
            'tests':{'prime_field_certificates':4,'prime_field_tampering':24,'binary_global_witnesses':2,'symbolic_identities':8,'positive_bounds':5,'outside_range_screen_cases':5},
            'failures_record':'FAILURES.md','source_snapshot_sha256':sha(HERE/'source_snapshot.zip'),
            'files':[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(HERE.rglob('*')) if p.is_file()]}
    with (HERE/'manifest.json').open('x') as out:json.dump(result,out,ensure_ascii=False,indent=2)
    with (HERE/'manifest_sha256.txt').open('x') as out:out.write(sha(HERE/'manifest.json')+'  manifest.json\n')
    print(json.dumps({'pass':True,'files_hashed':len(result['files']),'historical_files_unchanged':sum(x['files_verified'] for x in previous),
                      'manifest_sha256':sha(HERE/'manifest.json'),'source_snapshot_sha256':sha(HERE/'source_snapshot.zip')}))


if __name__=='__main__':main()
