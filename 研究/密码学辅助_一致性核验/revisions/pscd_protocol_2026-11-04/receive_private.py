"""P0 recipient boundary. The decode command reads no test oracle or source key."""
from pathlib import Path
import argparse
import hashlib
import json
from public_models import ROOT,save_json
from prepare import F,multiply
from run_protocol import public_reply


def export_for_receiver(run):
    run=Path(run)
    receipt=json.loads((run/'prepare/receipt.json').read_text())
    if receipt['profile']!='P0':raise ValueError('P0 only')
    material=json.loads((run/'prepare/private_material.json').read_text())
    context=json.loads((run/'public_context.json').read_text())
    keys={'matrix':[[format(value,'032x') for value in row] for row in material['matrix']],
          'multipliers':[format(value,'032x') for value in material['multipliers']],
          'pads':[format(value,'032x') for value in material['pads']],
          'codec':'GF128_FIXED_32_HEX'}
    keys.update(handle=receipt['handle'],profile='P0',method=receipt['method'],
                public_model_sha256=receipt['public_model_sha256'])
    directory=run/'recipient_package'
    save_json(directory/'private_receiver_material.json',keys)
    save_json(directory/'public_reply.json',public_reply(run))
    save_json(directory/'public_model.json',context['model'])
    return directory


def decode(reply,keys,model):
    if reply['state']!='COMMITTED':raise ValueError('uncommitted output')
    receipt=reply['receipt'];transcript=reply['profile_output']
    if receipt['profile']!='P0' or keys['profile']!='P0':raise ValueError('wrong profile')
    digest=hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest()
    if keys['handle']!=receipt['handle'] or digest!=keys['public_model_sha256'] or digest!=receipt['public_model_sha256']:
        raise ValueError('recipient/model binding mismatch')
    if transcript['public_status'] is not None:raise ValueError('unexpected public status')
    if keys.get('codec')!='GF128_FIXED_32_HEX':raise ValueError('fixed-width recipient encoding required')
    def field_word(value):
        if not isinstance(value,str) or len(value)!=32:raise ValueError('field word width')
        return F.element(int(value,16))
    matrix=[[field_word(value) for value in row] for row in keys['matrix']]
    multipliers=[field_word(value) for value in keys['multipliers']]
    pads=[field_word(value) for value in keys['pads']]
    values=[int(x,16) for x in transcript['field_output']]
    if len(values)!=len(pads):raise ValueError('ciphertext length')
    clear=[a^b for a,b in zip(values,pads)]
    if clear[-1] not in (0,1):raise ValueError('invalid private status')
    if clear[-1]==0:return {'accepted':False,'support':None,'residuals':None}
    decoded=[];n=model['n']
    for i in range(n):
        if keys['method']=='pscd':
            weights=multiply(matrix,model['dictionary'][i])
            if not any(weights):raise ValueError('erased position')
            pivot=next(j for j,w in enumerate(weights) if w)
            value=F.mul(clear[pivot*n+i],F.inverse(weights[pivot]))
            if any(F.mul(w,value)!=clear[j*n+i] for j,w in enumerate(weights)):raise ValueError('row inconsistency')
        elif keys['method']=='coordinate_nonzero':
            value=F.mul(clear[i],F.inverse(multipliers[i]))
        else:value=clear[i]
        decoded.append(value)
    return {'accepted':True,'residuals':decoded,'support':[i for i,x in enumerate(decoded) if x]}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['export','decode']);parser.add_argument('directory');args=parser.parse_args()
    directory=Path(args.directory)
    if args.operation=='export':
        package=export_for_receiver(directory);print(json.dumps({'recipient_package':str(package)}))
    else:
        result=decode(json.loads((directory/'public_reply.json').read_text()),
                      json.loads((directory/'private_receiver_material.json').read_text()),
                      json.loads((directory/'public_model.json').read_text()))
        print(json.dumps(result))
