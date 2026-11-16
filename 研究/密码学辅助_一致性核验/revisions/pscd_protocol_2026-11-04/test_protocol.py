"""Deterministic branch tests and lifecycle checks. Not privacy-distribution evidence."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fractions import Fraction
import copy
import json
import tempfile
from public_models import ROOT,get_model,aes_parameters,save_json
from prepare import RandomTape,prepare,consume,switch_profile,sample_r5,sample_t2,rank,multiply,r5_high,F
from check_models import verify_r5,verify_t2


class BranchTape:
    def __init__(self,values,reject=False):self.values=iter(values);self.reject=reject
    def element(self):return next(self.values)
    def below(self,limit):return limit-1 if self.reject else 0


def run_tests():
    checks=[]
    def check(name,condition):
        assert condition,name
        checks.append({'name':name,'passed':True})
    r5=get_model(8)
    embed=aes_parameters()['embed']
    identity=[1,0,0,1]
    for name,kernel,expected in [('high',[0,1,1],True),('low',[0,0,1],False)]:
        matrix,stats=sample_r5(r5,BranchTape(kernel+identity))
        check('r5_'+name+'_branch',stats['high_group']==expected and rank(matrix)==2 and all(any(multiply(matrix,v)) for v in r5['dictionary']))
    matrix,stats=sample_r5(r5,BranchTape([1,0,0,0,0,1]+identity))
    check('dictionary_kernel_rejected',stats['attempts']==2)
    matrix,stats=sample_r5(r5,BranchTape([0,0,1]+[0]*4+identity))
    check('singular_frame_rejected',stats['frame_attempts']==2)
    try:sample_r5(r5,BranchTape([0,0,1],reject=True),cap=1)
    except RuntimeError:check('sampler_budget_inconclusive',True)
    else:check('sampler_budget_inconclusive',False)
    t2_cases=[('t2_r2',[[1,2,3,0],[0,0,0,1]],True),
              ('t2_r2',[[1,2,0,0],[0,0,1,2]],False),
              ('t2_r3',[[1,0,0,0],[0,1,0,0],[0,0,1,1]],True),
              ('t2_r3',[[2,1,0,0],[4,0,1,0],[8,0,0,1]],False)]
    for variant,matrix,expected in t2_cases:
        model=get_model(5,variant)
        actual,stats=sample_t2(model,BranchTape([x for row in matrix for x in row]))
        check(variant+'_branch_'+str(expected),stats['high_group']==expected and actual==matrix and all(any(multiply(actual,v)) for v in model['dictionary']))
    for variant,n in [('r5',8),('t2_r2',5),('t2_r3',5)]:
        model=get_model(n,variant)
        for i in range(5):
            matrix,stats=(sample_r5(model,RandomTape()) if variant=='r5' else sample_t2(model,RandomTape()))
            check(f'{variant}_random_valid_{i}',rank(matrix)==model['r'] and all(any(multiply(matrix,v)) for v in model['dictionary']))
    with tempfile.TemporaryDirectory(dir=ROOT,prefix='lifecycle_test_') as temporary:
        folder=Path(temporary)
        reference={'source_id':'synthetic-frozen-input','private_input_sha256':'test-only'}
        first,_=prepare(folder/'first','P1','pscd',r5,reference)
        second,_=switch_profile(folder/'first',folder/'second','P0','pscd',r5,reference)
        check('switch_new_handle',first['handle']!=second['handle'])
        try:consume(folder/'first','P1','old')
        except FileExistsError:check('retired_handle_rejected',True)
        else:check('retired_handle_rejected',False)
        try:consume(folder/'second','P2','wrong')
        except ValueError:check('wrong_profile_rejected',True)
        else:check('wrong_profile_rejected',False)
        prepare(folder/'concurrent','P1','pscd',r5,reference)
        def use(index):
            try:consume(folder/'concurrent','P1',str(index));return True
            except FileExistsError:return False
        with ThreadPoolExecutor(max_workers=2) as pool:successes=list(pool.map(use,[0,1]))
        check('concurrent_single_use',sum(successes)==1)
    matrix,_=sample_r5(r5,RandomTape())
    first=multiply(matrix,r5['dictionary'][0]);second=[F.mul(x,9) for x in first]
    pivot=next(i for i,x in enumerate(first) if x)
    check('reuse_ratio_counterexample',F.mul(second[pivot],F.inverse(first[pivot]))==9)
    for name,change in [('U',lambda m:m.update(U=m['U']+1)),
                        ('family',lambda m:m.update(k=4)),
                        ('modulus',lambda m:m.update(modulus=0x11b)),
                        ('classifier',lambda m:m['products_by_sum'].pop('1'))]:
        broken=copy.deepcopy(r5);change(broken)
        try:verify_r5(broken,aes_parameters())
        except AssertionError:check('r5_tamper_'+name,True)
        else:check('r5_tamper_'+name,False)
    model=copy.deepcopy(get_model(5,'t2_r2'));model['paired_certificate']['delta']='0'
    try:verify_t2(model)
    except AssertionError:check('t2_certificate_tamper',True)
    else:check('t2_certificate_tamper',False)
    return {'scope':'functional branch/lifecycle/public-model checks only','fixed_branches_are_privacy_evidence':False,
            'checks':checks,'passed':len(checks),'failed':0}


if __name__=='__main__':
    result=run_tests();save_json(ROOT/'UNIT_RESULTS.json',result)
    print(json.dumps({'passed':result['passed'],'failed':result['failed']}))
