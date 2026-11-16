"""Snapshot this local revision and verify all earlier revision manifests."""
from pathlib import Path
import hashlib,json,platform,sys,zipfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not (HERE/'manifest.json').exists()
    previous=[]
    for name,manifest in [('structural_audit_2026-11-03_r1','delivery_manifest.json'),('novelty_search_2026-11-03_r2','manifest.json'),('multirow_explore_2026-11-03_r3','manifest.json')]:
        folder=HERE.parent/name;data=json.loads((folder/manifest).read_text())
        for item in data['files']:assert sha(folder/item['path'])==item['sha256'],item['path']
        previous.append({'revision':name,'files_checked':len(data['files']),'manifest_sha256':sha(folder/manifest)})
    original=json.loads((HERE.parent/'structural_audit_2026-11-03_r1/input_receipt.json').read_text())['inputs']
    for item in original:assert sha(ROOT/item['path'])==item['sha256']
    paper=ROOT.parent/'3-3-4.pdf';assert sha(paper)=='8688a088693f77ca84525520081357cd5d838ffdb04a662c01d67a4c52668f37'
    dependencies=[HERE.parent/'novelty_search_2026-11-03_r2/frontier_probe.py']+[HERE.parent/'multirow_explore_2026-11-03_r3'/name for name in ('kernel_minimax.py','certify_representation.py','check_representation_cert.py')]
    with zipfile.ZipFile(HERE/'source_snapshot.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.md'))+dependencies:
            name=path.name if path.parent==HERE else 'readonly_dependencies/'+path.parent.name+'/'+path.name
            info=zipfile.ZipInfo(name,date_time=(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,path.read_bytes())
    import scipy,numpy,sympy
    manifest={'version':'incidence-structure-r4','date':'2026-11-03','python':sys.version,'platform':platform.platform(),
              'libraries':{'scipy':scipy.__version__,'numpy':numpy.__version__,'sympy':sympy.__version__},
              'previous_revisions_unchanged':previous,'specified_ten_original_inputs_unchanged':True,'provided_paper_unchanged':True,
              'dependencies':[{'path':str(p),'sha256':sha(p)} for p in dependencies],
              'results':{'general_theorem':'q>=13, six-arc, two-row input-independent zero-erasure mask class',
                         'optimal_kernel_marginal':'unique; not claiming unique frame distribution',
                         'infinite_separation':'GF(7^m)', 'global_representation_extrema':'GF(16^m)',
                         'GF7_normalized_cases':70,'GF7_concurrence_classes':3,'extension_and_endpoint_certificates':8,'tampering_checks':48},
              'limits':['hand general proof, not proof-assistant verified','new priority search failed with transport errors','no deployment security proof','no end-to-end MPC value claim'],
              'strong_originality_established':False,'new_MPC_runs':0,'auth_lifecycle_writes':False,
              'initial_failures':'INITIAL_FAILURES.md','source_snapshot_sha256':sha(HERE/'source_snapshot.zip'),
              'files':[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(HERE.rglob('*')) if p.is_file()]}
    with (HERE/'manifest.json').open('x') as out:json.dump(manifest,out,ensure_ascii=False,indent=2)
    with (HERE/'manifest_sha256.txt').open('x') as out:out.write(sha(HERE/'manifest.json')+'  manifest.json\n')
    print(json.dumps({'pass':True,'files_hashed':len(manifest['files']),'historical_files_unchanged':sum(x['files_checked'] for x in previous),
                      'manifest_sha256':sha(HERE/'manifest.json'),'snapshot_sha256':sha(HERE/'source_snapshot.zip')}))


if __name__=='__main__':main()
