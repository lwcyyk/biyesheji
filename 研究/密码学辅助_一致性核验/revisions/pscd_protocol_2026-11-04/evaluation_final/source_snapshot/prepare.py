"""Trusted honest preprocessing and one-use lifecycle for synthetic PSCD tests."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import secrets
import time
from public_models import ROOT, Field, aes_parameters, save_json

F=Field(128)


class RandomTape:
    def __init__(self):
        self.bits=0
        self.field_draws=0
    def element(self):
        self.bits+=128
        self.field_draws+=1
        return secrets.randbits(128)
    def below(self, limit):
        width=limit.bit_length()
        while True:
            self.bits+=width
            value=secrets.randbits(width)
            if value<limit:
                return value
    def nonzero(self):
        value=self.element()
        while value==0:
            value=self.element()
        return value


def rank(matrix):
    data=[list(row) for row in matrix]
    pivot=0
    for column in range(len(data[0])):
        found=next((i for i in range(pivot,len(data)) if data[i][column]),None)
        if found is None:
            continue
        data[pivot],data[found]=data[found],data[pivot]
        inverse=F.inverse(data[pivot][column])
        data[pivot]=[F.mul(value,inverse) for value in data[pivot]]
        for i in range(len(data)):
            if i!=pivot and data[i][column]:
                scale=data[i][column]
                data[i]=[a^F.mul(scale,b) for a,b in zip(data[i],data[pivot])]
        pivot+=1
        if pivot==len(data):
            break
    return pivot


def multiply(matrix, vector):
    return [F.total(F.mul(a,b) for a,b in zip(row,vector)) for row in matrix]


def r5_high(kernel, model, embed):
    if kernel[0]==0:
        return kernel[1]!=0 and any(kernel[2]==embed[int(b)] for b in model['products_by_sum'])
    for total, products in model['products_by_sum'].items():
        target=kernel[2]^F.mul(embed[int(total)],kernel[1])
        if target in {embed[p] for p in products}:
            return True
    return False


def sample_r5(model, tape, cap=64):
    embed=aes_parameters()['embed']
    columns={tuple(v) for v in model['dictionary']}
    for attempt in range(1,cap+1):
        kernel=[tape.element() for _ in range(3)]
        pivot=next((i for i,x in enumerate(kernel) if x),None)
        if pivot is None:
            continue
        inverse=F.inverse(kernel[pivot])
        kernel=[F.mul(x,inverse) for x in kernel]
        if tuple(kernel) in columns:
            continue
        high=r5_high(kernel,model,embed)
        if not high and tape.below(model['D']+model['n']-3)>=model['D']:
            continue
        basis=[]
        for j in range(3):
            if j!=pivot:
                row=[0]*3
                row[j]=1
                row[pivot]=kernel[j]
                basis.append(row)
        for frame_attempt in range(1,cap+1):
            L=[[tape.element() for _ in range(2)] for _ in range(2)]
            if F.mul(L[0][0],L[1][1])^F.mul(L[0][1],L[1][0]):
                matrix=[[F.mul(row[0],basis[0][j])^F.mul(row[1],basis[1][j]) for j in range(3)] for row in L]
                return matrix,{'attempts':attempt,'frame_attempts':frame_attempt,'high_group':high}
        raise RuntimeError('PREPROCESSING_INCONCLUSIVE: frame cap')
    raise RuntimeError('PREPROCESSING_INCONCLUSIVE: kernel cap')


def kernel_one(matrix):
    # Determinantal null vector of a 3x4 matrix in characteristic two.
    def det3(a):
        return F.total([F.mul(a[0][0],F.mul(a[1][1],a[2][2])^F.mul(a[1][2],a[2][1])),
                        F.mul(a[0][1],F.mul(a[1][0],a[2][2])^F.mul(a[1][2],a[2][0])),
                        F.mul(a[0][2],F.mul(a[1][0],a[2][1])^F.mul(a[1][1],a[2][0]))])
    return [det3([[row[j] for j in range(4) if j!=i] for row in matrix]) for i in range(4)]


def sample_t2(model,tape,cap=64):
    ratio=Fraction(model['low_density'])/Fraction(model['high_density'])
    for attempt in range(1,cap+1):
        matrix=[[tape.element() for _ in range(4)] for _ in range(model['r'])]
        if rank(matrix)!=model['r']:
            continue
        outputs=[multiply(matrix,v) for v in model['dictionary']]
        if any(not any(v) for v in outputs):
            continue
        if model['r']==2:
            counts=[]
            for v in outputs:
                counts.append(sum(F.mul(v[0],w[1])==F.mul(v[1],w[0]) for w in outputs))
            high=max(counts)==3
        else:
            values=kernel_one(matrix)+[0]
            high=max(values.count(value) for value in values)==3
        if high or tape.below(ratio.denominator)<ratio.numerator:
            return matrix,{'attempts':attempt,'high_group':high}
    raise RuntimeError('PREPROCESSING_INCONCLUSIVE: matrix cap')


def prepare(directory,profile,method,model,input_reference,policy=None):
    if profile not in ('P0','P1','P2'):
        raise ValueError('unapproved profile')
    if method not in ('pscd','coordinate_nonzero','private_zero','full_shared_reference','pad_only'):
        raise ValueError('unknown method')
    policy=policy or {'gate_enabled':True,'forbidden_pairs':[]}
    directory=Path(directory).resolve()
    if not directory.is_relative_to(ROOT) or directory==ROOT:
        raise ValueError('Prepare directory must be in this revision')
    directory.mkdir(parents=True,exist_ok=False)
    tape=RandomTape()
    started=time.monotonic_ns()
    matrix=[]
    multipliers=[]
    sample_stats={}
    if profile!='P2' and method=='pscd':
        matrix,sample_stats=(sample_r5(model,tape) if model['variant']=='r5' else sample_t2(model,tape))
    if profile!='P2' and method=='coordinate_nonzero':
        multipliers=[tape.nonzero() for _ in range(model['n'])]
    payload_count=(model['r']*model['n'] if method=='pscd' else model['n'])
    pads=[tape.element() for _ in range(payload_count+1)] if profile=='P0' else []
    material=[v for row in matrix for v in row]+multipliers+pads
    material_bits=tape.bits
    shares=[[],[]]
    for value in material:
        share=tape.element()
        shares[0].append(share)
        shares[1].append(share^value)
    handle=secrets.token_hex(16)
    receipt={'handle':handle,'profile':profile,'method':method,'variant':model['variant'],
             'n':model['n'],'source_id':input_reference['source_id'],
             'public_model_sha256':hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest(),
             'policy':policy,'optimality_scope':'BASE_FAMILY' if not policy['forbidden_pairs'] else 'BASE_FAMILY_UPPER_BOUND_ONLY',
             'runtime_support_checked':policy['gate_enabled'],
             'state':'PREPARED','authorizes_real_service_action':False}
    save_json(directory/'receipt.json',receipt)
    private={'matrix':matrix,'multipliers':multipliers,'pads':pads,'material_shares':shares,
             'sampling':sample_stats,'protocol_random_bits_drawn':material_bits,
             'input_share_random_bits_drawn':tape.bits-material_bits,
             'matrix_field_elements':sum(map(len,matrix)),'coordinate_field_elements':len(multipliers),
             'pad_field_elements':len(pads),'prepare_ns':time.monotonic_ns()-started,
             'input_reference_private':input_reference}
    save_json(directory/'private_material.json',private)
    return receipt,private


def consume(directory,expected_profile,run_id,expected_policy=None):
    directory=Path(directory)
    receipt=json.loads((directory/'receipt.json').read_text(encoding='utf8'))
    if receipt['profile']!=expected_profile:
        raise ValueError('PROFILE_MISMATCH')
    if expected_policy is not None and receipt['policy']!=expected_policy:
        raise ValueError('POLICY_MISMATCH')
    with (directory/'consumed.json').open('x',encoding='utf8') as stream:
        json.dump({'handle':receipt['handle'],'run_id':run_id,'state':'CONSUMED'},stream)
    return receipt


def switch_profile(old_directory,new_directory,new_profile,method,model,input_reference,policy=None):
    old_directory=Path(old_directory)
    with (old_directory/'consumed.json').open('x',encoding='utf8') as stream:
        json.dump({'state':'RETIRED_FOR_PROFILE_SWITCH'},stream)
    return prepare(new_directory,new_profile,method,model,input_reference,policy)
