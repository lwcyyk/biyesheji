"""Shared fixed-profile circuit. No secret gate/status is opened in P0."""
import json
import os
from Compiler.types import sgf2n, cgf2n, Array
from Compiler.library import print_ln, check_point, for_range, runtime_error_if, start_timer, stop_timer
from aes_shared import expand_key, encrypt_block, pack_embedded, pack_public


def secret_inputs(count):
    values=Array(count,sgf2n)
    @for_range(count)
    def read(i):
        values[i]=sgf2n.get_input_from(0)+sgf2n.get_input_from(1)
    return values


def nonzero_bit(value):
    # Exponent 2^128-1 by doubling the exponent window. Entire result stays secret.
    result=value
    width=1
    for _ in range(7):
        lifted=result
        for _ in range(width):lifted=lifted*lifted
        result=lifted*result
        width*=2
    return result


def product(values):
    values=list(values)
    while len(values)>1:
        values=[values[i]*values[i+1] if i+1<len(values) else values[i] for i in range(0,len(values),2)]
    return values[0]


class Ops:
    def __init__(self,params,size=1):self.params=params;self.size=size
    def add(self,a,b):return a+b
    def total(self,values):return sum(values)
    def mul(self,a,b):return a*b
    def public(self,a,b):return cgf2n(a,size=b.size)*b
    def const(self,byte):return cgf2n(self.params['embed'][byte],size=self.size)


def record_residuals(context):
    model=context['model'];n=model['n'];records=context['public_records'];count=len(records)
    params=context['aes_parameters'];embed=params['embed']
    left=[sgf2n.get_input_from(0) for _ in range(16)]
    right=[sgf2n.get_input_from(1) for _ in range(16)]
    claims=secret_inputs(count)
    check_point()
    all_bytes=sgf2n.concat(left+right)
    lifted=all_bytes
    for _ in range(8):lifted=lifted*lifted
    invalid=nonzero_bit(lifted+all_bytes)
    domain_ok=product(1-invalid[i] for i in range(32))
    scalar_ops=Ops(params)
    keys=expand_key([a+b for a,b in zip(left,right)],scalar_ops)
    h=pack_embedded(encrypt_block([scalar_ops.const(0)]*16,keys,scalar_ops),scalar_ops)
    vector_keys=[[value.expand_to_vector(count) for value in row] for row in keys]
    vector_ops=Ops(params,count)
    nonces=[bytes.fromhex(record['nonce']) for record in records]
    def encrypted_counter(counter):
        blocks=[nonce+counter.to_bytes(4,'big') for nonce in nonces]
        values=[cgf2n([embed[block[j]] for block in blocks]) for j in range(16)]
        return pack_embedded(encrypt_block(values,vector_keys,vector_ops),vector_ops)
    tag_mask=encrypted_counter(1)
    stream=encrypted_counter(2)
    cipher=[bytes.fromhex(record['ciphertext']) for record in records]
    aad=[bytes.fromhex(record['aad']) for record in records]
    assert all(len(x)==16 for x in cipher+aad)
    a=cgf2n([pack_public(x) for x in aad])
    c=cgf2n([pack_public(x) for x in cipher])
    length=cgf2n(pack_public((128).to_bytes(8,'big')*2),size=count)
    hv=h.expand_to_vector(count)
    tag=((a*hv+c)*hv+length)*hv+tag_mask
    expected_tag=cgf2n([pack_public(bytes.fromhex(record['tag'])) for record in records])
    tag_delta=tag+expected_tag
    claim_delta=stream+c+claims.get_vector()
    values=Array(n,sgf2n)
    for i in range(n):values[i]=tag_delta[i//2] if i%2==0 else claim_delta[i//2]
    check_point()
    return values,domain_ok


def support_gate(values,domain_ok,context):
    n=context['model']['n'];k=context['model']['k']
    bits=Array(n,sgf2n)
    bits.assign_vector(nonzero_bit(values.get_vector()))
    if not context.get('gate_enabled',True):return domain_ok,bits
    states=Array(k+1,sgf2n)
    states.assign_all(0);states[0]=1
    @for_range(n)
    def step(i):
        bit=bits[i]
        for j in range(k,0,-1):states[j]=states[j]+bit*(states[j]+states[j-1])
        states[0]=states[0]+bit*states[0]
    accepted=domain_ok*sum(states[j] for j in range(k+1))
    for i,j in context.get('forbidden_pairs',[]):accepted*=1-bits[i]*bits[j]
    check_point()
    return accepted,bits


def emit(values):
    for i,value in enumerate(values):print_ln('PSCD_OUT index=%s value=%s',i,value)


def run(profile):
    with open(os.environ['PSCD_PUBLIC_CONTEXT']) as stream:context=json.load(stream)
    model=context['model'];n=model['n'];d=model['d'];rows=model['r'];method=context['method']
    assert context['profile']==profile
    runtime_error_if(cgf2n(1<<127)*cgf2n(2)!=cgf2n(0x87),'FIELD_MODULUS_MISMATCH')
    start_timer(1)
    values,domain_ok=record_residuals(context)
    stop_timer(1)
    start_timer(2)
    accepted,bits=support_gate(values,domain_ok,context)
    stop_timer(2)
    matrix=[];rho=None
    if profile!='P2' and method=='pscd':
        matrix=secret_inputs(rows*d)
    if profile!='P2' and method=='coordinate_nonzero':rho=secret_inputs(n)
    payload_size=rows*n if method=='pscd' else n
    pads=secret_inputs(payload_size+1) if profile=='P0' else None
    check_point()
    start_timer(3)
    source=values.get_vector()
    output=[]
    if profile=='P0':
        if method=='pscd':
            for row in range(rows):
                coefficients=[(accepted*matrix[row*d+j]).expand_to_vector(n) for j in range(d)]
                weight=sum(coefficients[j]*cgf2n([v[j] for v in model['dictionary']]) for j in range(d))
                block=(weight*source+pads.get_vector(row*n,n)).reveal()
                output.extend(block[i] for i in range(n))
        elif method=='coordinate_nonzero':
            block=(source*rho.get_vector()*accepted.expand_to_vector(n)+pads.get_vector(0,n)).reveal()
            output.extend(block[i] for i in range(n))
        else:
            block=(source*accepted.expand_to_vector(n)+pads.get_vector(0,n)).reveal()
            output.extend(block[i] for i in range(n))
        output.append((accepted+pads[payload_size]).reveal())
    else:
        public_ok=accepted.reveal()
        print_ln('PSCD_STATUS value=%s',public_ok)
        public_factors=Array(n,cgf2n)
        for i in range(n):public_factors[i]=public_ok
        clean=source*public_factors.get_vector()
        if profile=='P2':
            block=clean.reveal()
            output.extend(block[i] for i in range(n))
        elif method=='pscd':
            for row in range(rows):
                weight=sum(matrix[row*d+j].expand_to_vector(n)*cgf2n([v[j] for v in model['dictionary']]) for j in range(d))
                block=(weight*clean).reveal()
                output.extend(block[i] for i in range(n))
        elif method=='coordinate_nonzero':
            block=(rho.get_vector()*clean).reveal()
            output.extend(block[i] for i in range(n))
        else:
            for begin in range(0,n,128):
                packed=sum(bits[i]*cgf2n(1<<(i-begin)) for i in range(begin,min(begin+128,n)))
                output.append((packed*public_ok).reveal())
    check_point()
    emit(output)
    stop_timer(3)
    check_point()
    print_ln('PSCD_DONE')
