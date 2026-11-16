import os,sys,time,traceback,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from guard import ROOT,Budget,LimitReached,write,read,count,digest,proc_memory
import f1_model as M
import f1_check as F1
import compare as C

def run():
    session=sys.argv[sys.argv.index('--session')+1] if '--session' in sys.argv else '1'
    budget=Budget();start=time.perf_counter();summary={'category':'MODEL_CHECK','session':session,'F1':[],'F4':[],'F4_mutants':[],'status':'RUNNING'}
    out=ROOT/'reports'/f'MODEL_SUMMARY.{session}.json'
    run_reports=ROOT/'reports'/f'run_s{session}';run_inputs=ROOT/'inputs'/f'run_s{session}'
    C.REPORT_ROOT=run_reports;C.INPUT_ROOT=run_inputs
    base={'configs':['O','C'],'children':{'O':['C']},'limit':1,'empty':False,'allow_business':False,'abort':False,'recovery':False}
    branch={**base,'configs':['O','C','D'],'children':{'O':['C','D']}}
    jobs=[('SMOKE_UNKNOWN',base,'none'),
          ('RELEASE_EMPTY',{**base,'configs':['O'],'children':{},'empty':True,'allow_business':True},'none'),
          ('BRANCH_UNKNOWN',branch,'none')]
    mutants=['double_child','drop_rho','drop_hist','drop_dedup','stale_cache','reset_budget','ready_confusion','rollback','relabel_origin']
    jobs.extend(('M_'+m,branch if m=='double_child' else base,m) for m in mutants)
    jobs.extend([('POST_TAKEOVER_B',{**base,'allow_business':True,'business_tasks':[1],'business_after_takeover':True},'none'),
                 ('CHAIN',{**base,'configs':['O','C','E'],'children':{'O':['C'],'C':['E']}},'none'),
                 ('RECOVERY_ABORT',{**base,'abort':True,'recovery':True},'none')])
    try:
        for name,p,mutant in jobs:
            summary['current_job']='F1:'+name;write(out,summary)
            before=count();paramfile=run_inputs/'F1'/(name+'.json');write(paramfile,{'params':p,'mutant':mutant})
            result=F1.run(p,mutant,budget,soft_limit=12000 if mutant=='none' else 8000)
            result.update({'name':name,'params':p,'mutant':mutant,'category':'MUTATION_CHECK' if mutant!='none' else 'MODEL_CHECK',
                           'input_sha256':digest(paramfile)})
            if result.get('trace'):result['replay']=F1.replay(result,p,mutant,budget)
            write(run_reports/'F1'/(name+'.json'),result)
            summary['F1'].append({k:v for k,v in result.items() if k not in ('trace','params')});write(out,summary)
            print('F1',name,result['status'],result['visited'],flush=True)
            if mutant=='none' and result['status']=='COUNTEREXAMPLE_FOUND':
                summary['status']='MODEL_ERROR';return 4
            if mutant!='none' and result['status']!='COUNTEREXAMPLE_FOUND':
                summary.setdefault('coverage_gaps',[]).append(name)
        keyrows=[]
        for n,g,a,pin,weak in itertools.product((0,1,3),(False,True),(False,True),('O','C','D'),(False,True)):
            budget.visit();r=M.key_scenario(range(n),g,a,pin,weak);r.update({'governance':g,'provided_new_activate':a,'weak_epoch_only':weak});keyrows.append(r)
        write(run_reports/'F1'/'KEY_AUTH_TABLE.json',{'category':'MODEL_CHECK','rows':keyrows,
            'scope':'Exhaustive finite authentication predicates, not cryptographic execution or independent dynamic history proof',
            'rows_count':len(keyrows)})
        summary['F1_key_rows']=len(keyrows);write(out,summary)
        # Qualifier passed before entry; semantic imports/inputs are local and locked.
        data=C.fixtures()
        for d in data+C.generated():
            summary['current_job']='F4:'+d['id'];write(out,summary)
            result=C.check_case(d,budget);summary['F4'].append(result);write(out,summary)
            print('F4',d['id'],result['status'],flush=True)
            if result['status']!='PASS_BOUNDED':summary['status']='MODEL_ERROR';return 5
        byid={x['id']:x for x in data}
        mutation_jobs=[('COST1','stagewise_max'),('CE5_FULL','drop_mode'),('EMPTY_POST_INVALID','empty_post'),
            ('PARTIAL_POST_INVALID','empty_post'),('OPEN_UNKNOWN','ignore_unknown'),('NONUNIFORM','worldwise'),
            ('REAL_QUERY_COST','zero_query_cost'),('PREFIX_BAD','ignore_prefix'),('QUOTA_MODE','drop_permission'),
            ('MISSING_OBSERVATION','omit_observation')]
        for name,m in mutation_jobs:
            summary['current_job']='F4_MUTANT:'+name+':'+m;write(out,summary)
            r=C.mutant_case(byid[name],m,budget);summary['F4_mutants'].append(r);write(out,summary)
            print('F4_MUTANT',name,m,r['status'],flush=True)
        summary['status']='FINISHED'
        return 0
    except LimitReached as exc:
        summary['status']='INCONCLUSIVE_LIMIT';summary['reason']=str(exc);return 124
    except BaseException as exc:
        summary['status']='MODEL_ERROR';summary['exception']=repr(exc);summary['traceback']=traceback.format_exc();return 6
    finally:
        summary.update({'elapsed_seconds':time.perf_counter()-start,'visits_started_upper_bound':count(),'process_memory':proc_memory(),
            'program_hashes':{f.name:digest(f) for f in sorted((ROOT/'src').glob('*.py'))},'random_seed':None})
        write(out,summary);budget.close()

if __name__=='__main__':sys.exit(run())
