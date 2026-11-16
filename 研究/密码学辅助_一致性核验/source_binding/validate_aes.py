"""Independent library/KAT checks for the arithmetic AES/GCM binding layer."""
import argparse
import hashlib
import json
from pathlib import Path
import random
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from aes_field import *


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    params = derive_parameters(); ops = ClearOps(params); field = ops.f
    from field import Field
    byte_field = Field(8)
    for x in range(256):
        embedded = params['embed'][x]
        assert field.power(embedded, 256) == embedded
        reversed_byte = linearized(embedded, params['reverse_linear'], ops)
        assert reversed_byte == int(f'{x:08b}'[::-1], 2)
        inv = byte_field.power(x, 254)
        expected = inv ^ ((inv << 1 | inv >> 7) & 255) ^ ((inv << 2 | inv >> 6) & 255) ^ ((inv << 3 | inv >> 5) & 255) ^ ((inv << 4 | inv >> 4) & 255) ^ 0x63
        assert sbox(embedded, ops) == params['embed'][expected]
    for x in range(256):
        for y in range(256):
            assert field.mul(params['embed'][x], params['embed'][y]) == params['embed'][byte_field.mul(x, y)]
    rng = random.Random(2161103); records = []
    vectors = [(bytes.fromhex('000102030405060708090a0b0c0d0e0f'), bytes.fromhex('00112233445566778899aabbccddeeff'))]
    vectors += [(rng.randbytes(16), rng.randbytes(16)) for _ in range(8)]
    for key, block in vectors:
        ops = ClearOps(params)
        keys = expand_key([ops.const(x) for x in key], ops)
        encoded = encrypt_block([ops.const(x) for x in block], keys, ops)
        actual = unpack_public(pack_embedded(encoded, ops))
        expected = Cipher(algorithms.AES(key), modes.ECB()).encryptor().update(block)
        assert actual == expected
        records.append({'kind': 'AES128', 'key': key.hex(), 'plaintext': block.hex(),
                        'expected': expected.hex(), 'actual': actual.hex()})
    assert records[0]['actual'] == '69c4e0d86a7b0430d8cdb78070b4c55a'
    for aad_length in (0, 1, 16, 21):
        key, nonce, plain = rng.randbytes(16), rng.randbytes(12), rng.randbytes(16)
        aad = rng.randbytes(aad_length); encrypted = AESGCM(key).encrypt(nonce, plain, aad)
        ciphertext, tag = encrypted[:-16], encrypted[-16:]
        ops = ClearOps(params); keys = expand_key([ops.const(x) for x in key], ops)
        def aes(block): return pack_embedded(encrypt_block([ops.const(x) for x in block], keys, ops), ops)
        h = aes(bytes(16)); mask = aes(nonce + (1).to_bytes(4, 'big')); stream = aes(nonce + (2).to_bytes(4, 'big'))
        expected_tag = mask ^ ghash(h, aad, ciphertext, ops)
        recovered = unpack_public(pack_public(ciphertext) ^ stream)
        assert unpack_public(expected_tag) == tag and recovered == plain
        records.append({'kind': 'AES128_GCM_ONE_BLOCK', 'key': key.hex(), 'nonce': nonce.hex(),
                        'aad': aad.hex(), 'ciphertext': ciphertext.hex(), 'tag': tag.hex(),
                        'recomputed_tag': unpack_public(expected_tag).hex(), 'recovered': recovered.hex(),
                        'plain': plain.hex(), 'clear_product_count': ops.products})
    (out / 'parameters.json').write_text(json.dumps(params, indent=2))
    (out / 'vectors.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records))
    result = {'pass': True, 'field_embedding_products': 65536, 'sbox_cases': 256,
              'AES_vectors': 9, 'GCM_vectors': 4, 'scope': 'clear oracle checks; MPC tested separately',
              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}
    (out / 'summary.json').write_text(json.dumps(result, indent=2)); print(json.dumps(result))


if __name__ == '__main__': main()
