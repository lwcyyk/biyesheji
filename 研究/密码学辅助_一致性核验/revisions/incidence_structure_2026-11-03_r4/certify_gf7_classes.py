"""New full-kernel witnesses for all three classes; previous r3 files read only."""
from fractions import Fraction as F
from pathlib import Path
import argparse,hashlib,json,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'multirow_explore_2026-11-03_r3'))
from certify_representation import build
from check_representation_cert import check


def main():
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    out=(HERE/args.out).resolve();assert out.is_relative_to(HERE);out.mkdir(parents=True,exist_ok=False)
    reps=json.loads((HERE/'results/classify02/summary.json').read_text())['class_representatives'];records=[]
    for rep in reps:
        cols=rep['columns'];rows,eq,n,ep,fixed=build(cols)
        def sparse(rs):
            triples=[(i,j,float(v)) for i,row in enumerate(rs) for j,v in row]
            return coo_matrix(([v for i,j,v in triples],([i for i,j,v in triples],[j for i,j,v in triples])),shape=(len(rs),n)).tocsr()
        c=np.zeros(n);c[ep]=1;bounds=[(0,None)]*n
        for i in fixed:bounds[i]=(0,0)
        solved=linprog(c,A_ub=sparse(rows),b_ub=np.zeros(len(rows)),A_eq=sparse(eq),b_eq=np.ones(len(eq)),bounds=bounds,method='highs');assert solved.success
        rational=lambda xs:[str(F(float(x)).limit_denominator(10000000)) for x in xs]
        profile={'q':7,'field':'prime_mod_7','dictionary_columns':cols,'rows':2,'allowed_supports':'all_size_at_most_3',
                 'amplitudes':'arbitrary_nonzero_independent_coordinates','mask':'input_independent','erasure':'probability_zero_all_columns',
                 'observation':'indexed_masked_columns','metric':'worst_support_minimax_simulator_TV','scope':'PUBLIC_ALGEBRA_ONLY'}
        cert={'profile':profile,'profile_sha256':hashlib.sha256(json.dumps(profile,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
              'primal':rational(solved.x),'dual_inequality':rational(solved.ineqlin.marginals),'dual_equality':rational(solved.eqlin.marginals),
              'objective':str(F(float(solved.fun)).limit_denominator(10000000)),'authorizes_execution':False,'priority_verified':False}
        result=check(cert);assert result['status']=='VERIFIED',result
        name=f"class_{rep['canonical_bitmask']}.json";(out/name).write_text(json.dumps(cert,indent=2))
        records.append({'class':rep['canonical_bitmask'],'t':rep['count'],'file':name,'independent_full_kernel_check':result})
    (out/'summary.json').write_text(json.dumps(records,indent=2));print(json.dumps(records))


if __name__=='__main__':main()
