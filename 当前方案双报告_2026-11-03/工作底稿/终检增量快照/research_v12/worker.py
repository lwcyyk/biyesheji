import bootstrap
import json,time,sys,argparse,traceback
from pathlib import Path
from dataclasses import asdict
from types import SimpleNamespace
from resource_guard import install,peak_memory
guard=install()
from kernel import Meter,Cutoff
from auth_lifecycle.a import compiler,audit,runtime
from auth_lifecycle.checker import check_policy
from auth_lifecycle.b import reference as rb,checker as bc
from auth_lifecycle.schema import ModelError

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);ap.add_argument('--method',required=True);ap.add_argument('--kind',required=True);a=ap.parse_args()
    meter=Meter();row={'kind':a.kind,'method':a.method,'guards':guard};t0=time.perf_counter()
    spec=json.loads(Path(a.input).read_text(encoding='utf-8'))
    try:
        if a.kind=='J':
            t=time.perf_counter();comp=compiler.compile_model(spec);meter.tick('compiled_states',comp.nodes);row['compile_seconds']=time.perf_counter()-t
            if comp.status!='COMPILED':row.update(status=comp.status,reason=comp.reason)
            else:
                t=time.perf_counter();row['audit']=audit.check_compilation(comp.bundle);row['audit_seconds']=time.perf_counter()-t;meter.tick('audit_completed')
                if row['audit']['verdict']!='ACCEPTED':raise AssertionError(row['audit'])
                t=time.perf_counter()
                if a.method.startswith('F'):
                    from joint import solve
                    aa,bb,ab=map(int,a.method[1:]);ans=solve(comp.bundle,a4=bool(aa),bmethod='B4' if bb else 'B2',ab=bool(ab),meter=meter)
                elif a.method in ['RJ_FRESH','RJ_MEMO']:
                    from independent import exact
                    ans=exact(comp.bundle,meter=meter,cache=a.method=='RJ_MEMO')
                elif a.method=='Z3_INCREMENTAL':
                    from smt_joint import Incremental
                    solver=Incremental(comp.bundle,meter);ans=solver.solve()
                    ans['query_schedule']='single root; identical dynamic sequences measured separately'
                elif a.method in ['GENERIC_REPLAY','GENERIC_ABSTRACTION']:
                    from joint import solve
                    ans=solve(comp.bundle,ab=a.method=='GENERIC_REPLAY',a4=a.method=='GENERIC_ABSTRACTION',meter=meter)
                    ans['equivalence_control']='same fully disclosed proof mechanism supplied to generic method'
                else:
                    from a_ab_search import solve
                    mode={'OLD_AB2':'AB2','OLD_A2':'A2','OLD_A3':'A_QUOTIENT'}[a.method]
                    old=solve(comp.bundle,mode=mode,feedback=a.method=='OLD_AB2',meter=meter)
                    ans={'status':'IMPOSSIBLE_IN_MODEL' if old.status=='IMPOSSIBLE' else old.status,'value':old.worst_requests,'policy':old.policy,'stats':old.stats,'legacy_adapter':True,'policy_class':'early_commit' if mode!='AB2' else 'joint'}
                row['solve_seconds']=time.perf_counter()-t;meter.tick('solve_finished');row['result']=ans;row['status']=ans['status']
                status='IMPOSSIBLE' if ans['status']=='IMPOSSIBLE_IN_MODEL' else ans['status']
                t=time.perf_counter();row['evaluation']=runtime.evaluate(comp.bundle,SimpleNamespace(status=status,policy=ans.get('policy')));row['check_score_seconds']=time.perf_counter()-t;meter.tick('scoring_finished')
        else:
            t=time.perf_counter()
            if a.method in ['B4','GENERIC_PRESOLVE']:
                from b4 import solve,check_compression
                ans=solve(spec,meter)
                if ans.get('certificate'):row['compression_check']=check_compression(spec,ans['certificate'])
            elif a.method in ['B2','GENERIC_BB']:
                from b_units import solve
                ans=solve(spec,method=a.method,meter=meter)
            elif a.method=='B3':
                from b_components import solve
                ans=solve(spec,meter)
            elif a.method=='Z3_OPTIMIZE':
                from smt_comparator import solve
                ans=solve(spec,meter)
            else:ans=asdict(rb.solve(spec))
            meter.tick('solve_finished');row['solve_seconds']=time.perf_counter()-t
            row['status']='IMPOSSIBLE_IN_MODEL' if ans['status']=='IMPOSSIBLE' else ans['status'];row['result']=ans
            t=time.perf_counter()
            if ans.get('delivery'):row['delivery_check']=bc.check_delivery(spec,ans['delivery'])
            row['check_score_seconds']=time.perf_counter()-t;meter.tick('checking_finished')
    except ModelError as e:row.update(status='UNKNOWN',reason=str(e))
    except Cutoff as e:row.update(status='INCONCLUSIVE',reason=str(e))
    except Exception as e:row.update(status='ERROR',reason=str(e),traceback=traceback.format_exc())
    row.update(total_seconds=meter.elapsed(),cpu_seconds=time.process_time()-meter.cpu_start,memory=peak_memory(),counts=dict(meter.counts))
    if row['total_seconds']>30:row['status']='TIMEOUT'
    Path(a.out).write_text(json.dumps(row,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
if __name__=='__main__':main()
