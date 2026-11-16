"""Synthetic AES-GCM fixtures. Oracle uses cryptography, not the MPC AES code."""
from pathlib import Path
import copy
import hashlib
import json
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from public_models import ROOT, aes_field, aes_parameters, save_json


def source_for(n):
    path=ROOT/'private'/f'source_n{n}.json'
    if not path.exists():
        key=secrets.token_bytes(16)
        records=[]
        for index in range((n+1)//2):
            nonce=(index+1).to_bytes(12,'big')
            aad=b'PSCD-epoch-0001'.ljust(16,b'\0')
            plain=secrets.token_bytes(16)
            encrypted=AESGCM(key).encrypt(nonce,plain,aad)
            records.append({'nonce':nonce.hex(),'aad':aad.hex(),'ciphertext':encrypted[:-16].hex(),
                            'tag':encrypted[-16:].hex(),'plain':plain.hex()})
        save_json(path,{'kind':'SYNTHETIC_TEST_ORACLE_NOT_PRODUCTION_SECRET','key':key.hex(),'records':records})
    return json.loads(path.read_text(encoding='utf8'))


def make_input(model,repeat,case='scheduled'):
    n=model['n']
    source=source_for(n)
    records=copy.deepcopy(source['records'])
    claims=[bytes.fromhex(x['plain']) for x in records]
    failures=[]
    if case=='scheduled':
        failures=[] if repeat==0 else [1] if repeat==1 else [i for i in range(1,n,2)][:3]
    elif case=='bad_tag':
        failures=[0]
    elif case=='dense':
        failures=list(range(model['k']+1))
    elif case=='boundary':
        failures=list(range(model['k']))
    elif case not in ('valid','bad_domain'):
        raise ValueError('fixture case')
    for position in failures:
        index=position//2
        if position%2:
            value=bytearray(claims[index]);value[0]^=1;claims[index]=bytes(value)
        else:
            value=bytearray.fromhex(records[index]['tag']);value[0]^=1;records[index]['tag']=bytes(value).hex()
    key=bytes.fromhex(source['key'])
    residuals=[]
    public=[]
    for index,record in enumerate(records):
        nonce=bytes.fromhex(record['nonce']);aad=bytes.fromhex(record['aad']);cipher=bytes.fromhex(record['ciphertext'])
        encryptor=Cipher(algorithms.AES(key),modes.ECB()).encryptor()
        stream=encryptor.update(nonce+(2).to_bytes(4,'big'))
        actual=bytes(a^b for a,b in zip(cipher,stream))
        tag=AESGCM(key).encrypt(nonce,actual,aad)[-16:]
        residuals += [aes_field.pack_public(tag)^aes_field.pack_public(bytes.fromhex(record['tag'])),
                      aes_field.pack_public(actual)^aes_field.pack_public(claims[index])]
        public.append({k:v for k,v in record.items() if k!='plain'})
    residuals=residuals[:n]
    source_id='aes-'+hashlib.sha256(json.dumps(public,sort_keys=True).encode()).hexdigest()[:20]
    frozen={'key_hex':key.hex(),'claims_hex':[x.hex() for x in claims],
            'residuals':residuals,'case':case,'repeat':repeat}
    reference={'source_id':source_id,'private_input_sha256':hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()}
    return {'public_records':public,'frozen':frozen,'reference':reference}


def share_inputs(fixture,private_material):
    params=aes_parameters()
    party=[[],[]]
    for byte in bytes.fromhex(fixture['frozen']['key_hex']):
        share=secrets.randbits(8)
        party[0].append(params['embed'][share]);party[1].append(params['embed'][share^byte])
    for block in fixture['frozen']['claims_hex']:
        value=aes_field.pack_public(bytes.fromhex(block))
        share=secrets.randbits(128)
        party[0].append(share);party[1].append(share^value)
    if fixture['frozen']['case']=='bad_domain':
        party[0][0]^=2
    for p in (0,1):party[p].extend(private_material['material_shares'][p])
    return party
