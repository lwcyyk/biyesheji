import sys,json,time,hashlib,argparse,traceback
from pathlib import Path
from dataclasses import asdict
from resource_guard import install,peak_memory
guard=install()
from common import Meter,Cutoff
from auth_lifecycle.a import compiler,audit,runtime,joint_reference
from auth_lifecycle.b import search,baselines,reference,checker as bc
from auth_lifecycle import checker,reference as ri
from a_ab_search import solve
from b_units import solve as bsolve,check_lower_bound

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);ap.add_argument('--method',required=True);ap.add_argument('--kind',required=True);ap.add_argument('--limit',type=int,default=1_000_000);a=ap.parse_args()
 meter=Meter(limit=a.limit);spec=json.loads(Path(a.input).read_text(encoding='utf-8'));row={'method':a.method,'kind':a.kind,'guards':guard};t0=time.perf_counter()
 try:
  if a.kind=='A':
   c=compiler.compile_model(spec);meter.tick('compiled_nodes',c.nodes)
   if c.status!='COMPILED':row.update(status=c.status,reason=c.reason)
   else:
    audit_result=audit.check_compilation(c.bundle);meter.tick('audit_call')
    if audit_result['verdict']!='ACCEPTED':raise RuntimeError('source compilation audit failed')
    if a.method=='R-J':answer=joint_reference.solve(c.bundle)
    else:answer=solve(c.bundle,mode='AB2' if a.method in ['AB_OFF','AB_ON','GENERIC_DRD'] else a.method,feedback=a.method in ['AB_ON','GENERIC_DRD'],meter=meter)
    meter.tick('solve_completed');ev=runtime.evaluate(c.bundle,answer);meter.tick('independent_evaluation')
    row.update(status=answer.status,result=asdict(answer),evaluation=ev,compile_nodes=c.nodes,audit=audit_result)
  else:
   if a.method in ['B2','GENERIC_BB']:res=bsolve(spec,method=a.method,meter=meter)
   elif a.method=='B_OLD':res=asdict(search.solve(spec,limit=a.limit))
   elif a.method=='B-B':res=asdict(baselines.solve(spec,limit=a.limit))
   else:res=asdict(reference.solve(spec,limit=a.limit))
   meter.tick('solve_completed')
   ck=bc.check_delivery(spec,res['delivery']) if res.get('delivery') else None
   bound=check_lower_bound(spec,res['certificate'],meter) if res.get('certificate') else None
   meter.tick('independent_check')
   row.update(status=res['status'],result=res,delivery_check=ck,lower_bound_check=bound)
 except Cutoff as e:row.update(status='INCONCLUSIVE',reason=str(e),U=0)
 except Exception as e:row.update(status='ERROR',error=str(e),traceback=traceback.format_exc())
 row.update(total_wall_seconds=meter.elapsed(),total_cpu_seconds=time.process_time()-meter.cpu_start,peak_memory=peak_memory(),meter=dict(meter.counts))
 if row['total_wall_seconds']>30:row['status']='TIMEOUT';row['U']=0
 Path(a.out).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
