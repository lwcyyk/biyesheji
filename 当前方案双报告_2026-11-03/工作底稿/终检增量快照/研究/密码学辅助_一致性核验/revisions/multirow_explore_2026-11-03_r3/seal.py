"""Seal results and verify historical snapshots; no originality certification."""
from pathlib import Path
import hashlib,json,platform,sys,zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not (HERE/'manifest.json').exists()
    previous=[]
    for folder,manifest_name in [('structural_audit_2026-11-03_r1','delivery_manifest.json'),('novelty_search_2026-11-03_r2','manifest.json')]:
        p=HERE.parent/folder;m=json.loads((p/manifest_name).read_text())
        for record in m['files']:assert sha(p/record['path'])==record['sha256'],record['path']
        previous.append({'folder':folder,'manifest_sha256':sha(p/manifest_name),'files_verified_unchanged':len(m['files'])})
    receipt=json.loads((HERE.parent/'structural_audit_2026-11-03_r1/input_receipt.json').read_text())
    for record in receipt['inputs']:assert sha(ROOT/record['path'])==record['sha256']
    pdf=ROOT.parent/'3-3-4.pdf';pdf_hash=sha(pdf)
    assert pdf_hash=='8688a088693f77ca84525520081357cd5d838ffdb04a662c01d67a4c52668f37'
    first=json.loads((HERE/'results/representation_check01/checks.json').read_text())
    replay=json.loads((HERE/'results/representation_check02/checks.json').read_text());assert first==replay
    source_files=sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.md'))
    dependency=HERE.parent/'novelty_search_2026-11-03_r2/frontier_probe.py'
    with zipfile.ZipFile(HERE/'source_snapshot.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for p in source_files:
            info=zipfile.ZipInfo(p.name,date_time=(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,p.read_bytes())
        info=zipfile.ZipInfo('readonly_dependency/frontier_probe_r2.py',date_time=(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,dependency.read_bytes())
    import scipy,numpy,sympy
    manifest={'version':'multirow-explore-r3','date':'2026-11-03','python':sys.version,'platform':platform.platform(),
              'dependencies':{'scipy':scipy.__version__,'numpy':numpy.__version__,'sympy':sympy.__version__,'r2_field_source_sha256':sha(dependency)},
              'previous':previous,'original_ten_inputs_unchanged':True,'provided_paper':{'path':str(pdf),'sha256':pdf_hash,'previous_fulltext_gap':'CLOSED'},
              'exact_certificate_replay_identical':True,'source_snapshot_sha256':sha(HERE/'source_snapshot.zip'),
              'strong_originality_established':False,'independent_contribution_candidate':'NONUNIFORM_KERNEL_MINIMAX_AND_REPRESENTATION_SENSITIVITY',
              'proof_scope':'hand general reductions and sharp four-column bound; exact finite LP certificates for two GF7 instances',
              'new_MPC_runs':0,'deployment_security_proved':False,'auth_lifecycle_writes':False,
              'files':[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(HERE.rglob('*')) if p.is_file()]}
    with (HERE/'manifest.json').open('x') as out:json.dump(manifest,out,ensure_ascii=False,indent=2)
    with (HERE/'manifest_sha256.txt').open('x') as out:out.write(sha(HERE/'manifest.json')+'  manifest.json\n')
    print(json.dumps({'pass':True,'files_hashed':len(manifest['files']),'historical_files_unchanged':sum(x['files_verified_unchanged'] for x in previous),
                      'manifest_sha256':sha(HERE/'manifest.json'),'source_snapshot_sha256':sha(HERE/'source_snapshot.zip')}))


if __name__=='__main__':main()
