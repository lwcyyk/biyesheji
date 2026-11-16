"""Exhaust every GF7 six-arc after a fixed ordered projective frame."""
from pathlib import Path
from itertools import combinations
import argparse,json
from incidence import points,is_arc,concurrence,direct_counts,compiled_counts,actions,canonical_C,encode_C


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    q=7;frame=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)];extra=[x for x in points(q) if x not in frame and is_arc(frame+[x],q)]
    all_actions=actions();rows=[];groups={}
    for a,b in combinations(extra,2):
        cols=frame+[a,b]
        if not is_arc(cols,q):continue
        C=concurrence(cols,q);actual=direct_counts(cols,q);expected=compiled_counts(q,C);assert actual==expected
        canonical,permutation=canonical_C(C,all_actions)
        groups.setdefault(str(canonical),[]).append(len(rows))
        rows.append({'columns':cols,'concurrent_perfect_matchings':C,'count':len(C),'canonical_bitmask':canonical,
                     'canonical_permutation':permutation,'signature_histogram':{str(k):sum(v for T,v in actual.items() if len(T)==k) for k in range(4)}})
    # Bind the two previously certified representatives, not just their optima.
    old=here.parent/'multirow_explore_2026-11-03_r3/results/representation_cert01';certified=[]
    for path in sorted(old.glob('certificate_*.json')):
        cert=json.loads(path.read_text());cols=[tuple(x) for x in cert['profile']['dictionary_columns']]
        C=concurrence(cols,q);key,permutation=canonical_C(C,all_actions)
        certified.append({'source_certificate':str(path),'objective':cert['objective'],'canonical_bitmask':key,
                          'concurrent_perfect_matchings':C,'canonical_permutation':permutation})
    summary={'q':q,'extra_points':len(extra),'unordered_extra_pairs_considered':len(extra)*(len(extra)-1)//2,
             'valid_normalized_six_arcs':len(rows),'concurrence_isomorphism_classes':{key:len(indices) for key,indices in groups.items()},
             'certified_representatives':certified,'pass':True,
             'class_representatives':[rows[indices[0]] for indices in groups.values()],
             'previous_two_examples_cover_all_classes':set(groups)=={str(x['canonical_bitmask']) for x in certified},
             'scope':'complete normalized GF7 incidence classification; not claiming projective-equivalence classification or other fields'}
    (out/'instances.json').write_text(json.dumps(rows,indent=2));(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
