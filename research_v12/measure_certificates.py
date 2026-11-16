"""Cost decomposition diagnostic, separate from paired speed experiments."""
import bootstrap
import json,time,statistics
from generators import joint_cases
from kernel import Graph,Meter,control_solve
from independent import Checker
from auth_lifecycle.a.compiler import compile_model
from auth_lifecycle.a.audit import check_compilation
from resource_guard import install,peak_memory
def main():
    dest=bootstrap.ROOT/'runs/certificate_cost01';dest.mkdir(parents=True,exist_ok=False);rows=[];guard=install()
    for name,src,_ in joint_cases():
        start=time.perf_counter();comp=compile_model(src);assert check_compilation(comp.bundle)['verdict']=='ACCEPTED'
        compile_audit=time.perf_counter()-start;m=Meter();g=Graph(comp.bundle,m);ck=Checker(comp.bundle,m)
        if not g.root.knowledge:rows.append({'case':name,'status':'UNKNOWN','reason':'empty K','compile_audit_seconds':compile_audit});continue
        t=time.perf_counter();core=control_solve(g,g.root);build=time.perf_counter()-t
        t=time.perf_counter();verdict,why=ck.check_certificate(core,g.root);check=time.perf_counter()-t;assert verdict=='VALID'
        transitions=[]
        for a,cs in g.edges(g.root).items():
            for o,c in cs.items():
                t=time.perf_counter();post=ck.post(g.root,a,o);post_seconds=time.perf_counter()-t;assert post==c
                t=time.perf_counter();r=ck.transfer(core,g.root,a,o,c);transfer_seconds=time.perf_counter()-t
                transitions.append({'action':a,'observation':o,'post_seconds':post_seconds,'transfer_including_old_validation_seconds':transfer_seconds,'verdict':r['verdict']})
        rows.append({'case':name,'status':core['status'],'compile_audit_seconds':compile_audit,'control_search_plus_certificate_build_seconds':build,'new_certificate_check_seconds':check,'certificate_utf8_bytes':len(json.dumps(core,ensure_ascii=False).encode('utf-8')),'transitions':transitions,'counts':dict(m.counts),'total_seconds':compile_audit+m.elapsed()})
    out={'rows':rows,'guards':guard,'memory':peak_memory(),'pass':True,'scope':'construction includes complete control search; transfer includes full Post and old/new proof checks; not standalone serialization cost or a paired advantage measurement'}
    (dest/'result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('certificate timing rows',len(rows))
if __name__=='__main__':main()
