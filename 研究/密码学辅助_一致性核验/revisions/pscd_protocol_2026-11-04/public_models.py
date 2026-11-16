"""Public model compilation only. Secret sampling lives in prepare.py."""
from pathlib import Path
from fractions import Fraction
from math import comb
import hashlib
import importlib.util
import json
import os
import sys
import threading
import time
import numpy as np

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE/'source_binding'))
import aes_field
from field import Field


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary=path.with_name(path.name+f'.tmp-{os.getpid()}-{threading.get_ident()}')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')
    temporary.replace(path)


def aes_parameters():
    path = ROOT/'public/aes_parameters.json'
    if not path.exists():
        started = time.monotonic_ns()
        params = aes_field.derive_parameters()
        save_json(path, params)
        save_json(ROOT/'public/aes_parameters_build.json', {
            'elapsed_ns': time.monotonic_ns()-started,
            'legacy_source': str(BASE/'source_binding/aes_field.py'),
            'legacy_sha256': hashlib.sha256((BASE/'source_binding/aes_field.py').read_bytes()).hexdigest()})
    return json.loads(path.read_text(encoding='utf8'))


def build_r5(n):
    if n not in range(5,257):
        raise ValueError('R5 implementation supports 5<=n<=256')
    started = time.monotonic_ns()
    params = aes_parameters()
    embed = params['embed']
    field8 = Field(8)
    table = np.array([[field8.mul(i,j) for j in range(256)] for i in range(256)], dtype=np.int64)
    counts = np.zeros(256*256+256, dtype=np.int64)
    xs = np.arange(256, dtype=np.int64)
    products = {}
    for left in range(n):
        for right in range(left+1,n):
            product = int(table[left,right])
            total = left ^ right
            counts[xs*256 + (table[total] ^ product)] += 1
            counts[65536+total] += 1
            products.setdefault(str(total), []).append(product)
    for label in range(n):
        counts[label*256+int(table[label,label])] = 0
    histogram = {str(int(k)): int(v) for k,v in zip(*np.unique(counts[counts>0],return_counts=True))}
    intersection_loss = sum((int(k)-1)*v for k,v in histogram.items())
    q = 1 << 128
    U = comb(n,2)*(q-1)-intersection_loss
    N = q*q+q+1-n
    O = N-U
    m = n-3
    D = U-3*(q-1)
    Z = (q-1)*U-3*O
    high = Fraction(D+m,(q-1)*Z)
    low = Fraction(D,(q-1)*Z)
    assert U*high+O*low == 1
    model = {
        'variant': 'r5', 'q': q, 'n': n, 'd': 3, 'k': 3, 'r': 2,
        'field_bits': 128, 'modulus': (1<<128)|0x87,
        'dictionary': [[1,embed[i],embed[int(table[i,i])]] for i in range(n)],
        'labels': embed[:n], 'subfield_size': 256,
        'subfield_histogram': histogram, 'intersection_loss': intersection_loss,
        'U': U, 'O': O, 'D': D, 'Z': Z,
        'high_density': str(high), 'low_density': str(low), 'delta': str(m*low),
        'products_by_sum': {key: sorted(set(values)) for key,values in products.items()},
        'proof_rule': 'R5_GENERAL_THEOREM_INSTANCE',
        'proof_source_sha256': hashlib.sha256((BASE/'revisions/general_arc_2026-11-03_r5/GENERAL_THEOREM.md').read_bytes()).hexdigest(),
        'proof_status': 'HAND_PROOF_PENDING_EXTERNAL_REVIEW',
        'scope': 'PUBLIC_MODEL_ONLY', 'authorizes_execution': False,
        'structure_compile_ns': time.monotonic_ns()-started}
    return model


def build_t2(row_limit):
    if row_limit not in (2,3):
        raise ValueError('T2 row budget')
    q=1<<128
    Q=q-1
    T=q*q+q-3
    if row_limit==2:
        Z=3*q**4+3*q**3-4*q*q-7*q+3
        low=Fraction(3,Z)
        high=low*(1+Fraction(T,6*Q*Q))
        delta=T*low
    else:
        Z=2*q**3+2*q*q+2*q-3
        low=Fraction(2,Z)
        high=low*(1+Fraction(1,4*Q))
        delta=low
    solver_path=BASE/'revisions/final_closure_2026-11-04/solve_exact.py'
    specification=importlib.util.spec_from_file_location('archived_exact_lp',solver_path)
    solver=importlib.util.module_from_spec(specification)
    specification.loader.exec_module(solver)
    paired_certificate,_=solver.solve(q,row_limit)
    assert paired_certificate['delta']==str(delta)
    return {'variant':f't2_r{row_limit}','q':q,'n':5,'d':4,'k':4,'r':row_limit,
            'field_bits':128,'modulus':(1<<128)|0x87,
            'dictionary':[[int(i==j) for j in range(4)] for i in range(4)]+[[1]*4],
            'high_density':str(high),'low_density':str(low),'delta':str(delta),
            'paired_certificate':paired_certificate,
            'proof_rule':'T2_CANONICAL_FRAME_CHAR2_EXTENSION',
            'proof_status':'HAND_PROOF_EXTENSION_PENDING_EXTERNAL_REVIEW',
            'proof_source_sha256':hashlib.sha256((BASE/'revisions/final_closure_2026-11-04/MODEL_REDUCTION.md').read_bytes()).hexdigest(),
            'scope':'PUBLIC_MODEL_ONLY','authorizes_execution':False}


def get_model(n, variant='r5'):
    path=ROOT/'public'/f'model_{variant}_n{n}.json'
    if not path.exists():
        model=build_r5(n) if variant=='r5' else build_t2(int(variant[-1]))
        if model['n']!=n:
            raise ValueError('MODEL_NOT_APPLICABLE: T2 requires n=5')
        save_json(path,model)
    elif variant!='r5' and 'paired_certificate' not in json.loads(path.read_text(encoding='utf8')):
        save_json(path,build_t2(int(variant[-1])))
    return json.loads(path.read_text(encoding='utf8'))


if __name__=='__main__':
    for n in [8,64,256]:
        model=get_model(n)
        print(json.dumps({'n':n,'J':model['intersection_loss'],'delta':model['delta']}),flush=True)
    for variant in ['t2_r2','t2_r3']:
        get_model(5,variant)
