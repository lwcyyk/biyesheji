"""Build an isolated, reproducible synthetic native-record binding experiment."""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import random
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import aes_field as aes

ROOT = aes.ROOT


def flip(data): return bytes([data[0] ^ 1]) + data[1:]


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(216110303); key = rng.randbytes(16); params = aes.derive_parameters()
    originals = []
    for i in range(2):
        nonce = (i + 1).to_bytes(12, 'big'); aad = f'AI-record={i};key-epoch=7'.encode()
        plain = rng.randbytes(16); encrypted = AESGCM(key).encrypt(nonce, plain, aad)
        originals.append({'nonce': nonce, 'aad': aad, 'ciphertext': encrypted[:-16], 'tag': encrypted[-16:], 'plain': plain})
    case_names = ['valid', 'bad_tag0', 'wrong_claim0', 'bad_tag_and_claim0', 'swapped_claims',
                  'changed_ciphertext0', 'changed_aad1', 'three_failures']
    public_cases = []; claims = []; expected = []
    for index, name in enumerate(case_names):
        records = [{k: v for k, v in r.items() if k != 'plain'} for r in originals]
        claimed = [r['plain'] for r in originals]
        if index in (1, 3, 7): records[0]['tag'] = flip(records[0]['tag'])
        if index in (2, 3, 7): claimed[0] = flip(claimed[0])
        if index == 4: claimed.reverse()
        if index == 5: records[0]['ciphertext'] = flip(records[0]['ciphertext'])
        if index == 6: records[1]['aad'] = flip(records[1]['aad'])
        if index == 7: records[1]['tag'] = flip(records[1]['tag'])
        support = []
        # Oracle decrypts CTR with library AES and recomputes native tag; this
        # path is independent of the arithmetic AES and row-space implementation.
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        for i, record in enumerate(records):
            stream = Cipher(algorithms.AES(key), modes.ECB()).encryptor().update(record['nonce'] + (2).to_bytes(4, 'big'))
            plain = bytes(x ^ y for x, y in zip(record['ciphertext'], stream))
            tag = AESGCM(key).encrypt(record['nonce'], plain, record['aad'])[-16:]
            if tag != record['tag']: support.append(2 * i)
            if plain != claimed[i]: support.append(2 * i + 1)
        expected.append({'status': 2 if len(support) > 2 else int(bool(support)), 'support': [] if len(support) > 2 else support})
        public_cases.append(records); claims.append(claimed)
    party_inputs = [[], []]
    for byte in key:
        share = rng.randrange(256)
        party_inputs[0].append(params['embed'][share]); party_inputs[1].append(params['embed'][share ^ byte])
    for pair in claims:
        for block in pair:
            share = rng.getrandbits(128)
            party_inputs[0].append(share); party_inputs[1].append(share ^ aes.pack_public(block))
    fixture = {'kind': 'SYNTHETIC_AES_GCM_RECORD_BINDING_NOT_TLS_HANDSHAKE', 'batches': len(case_names),
               'n': 4, 'case_names': case_names, 'party_inputs': party_inputs, 'expected': expected,
               'test_oracle_key_hex': key.hex(), 'oracle_plaintexts_hex': [r['plain'].hex() for r in originals],
               'public_records': [{k: v.hex() for k, v in r.items() if k != 'plain'} for r in originals]}
    (out / 'fixture.json').write_text(json.dumps(fixture, indent=2))
    invalid = json.loads(json.dumps(fixture)); invalid['kind'] += '_INVALID_SUBFIELD_INPUT'
    invalid['party_inputs'][0][0] = 2
    assert aes.Field(128).power(2, 256) != 2
    (out / 'invalid_fixture.json').write_text(json.dumps(invalid, indent=2))
    base_path = ROOT / 'mpc/rowspace2.mpc'; base = base_path.read_text()
    marker = '@for_range(batches)\ndef batch(index):\n'
    assert base.count(marker) == 1
    prefix, driver = base.split(marker)
    body = '    determinants = []' + driver.split('    determinants = []', 1)[1]
    body = body.split("\ncheck_point()\nprint_ln('ATTEMPT_KIND", 1)[0]
    diagnostic = '\ndef diagnose(index, values):\n    check_point()\n' + body + '\n'
    library = '\n'.join(inspect.getsource(f) for f in (aes.linearized, aes.sbox, aes.expand_key,
                             aes.encrypt_block, aes.pack_embedded, aes.pack_public, aes.ghash))
    program = prefix + '\n# Generated standard AES arithmetic; no novel cipher claim.\n' + library
    program += '\nPARAMS = ' + repr(params) + '\nPUBLIC_CASES = ' + repr(public_cases) + '\n'
    program += '''
class MPCOps:
    params = PARAMS
    def add(self, a, b): return a + b
    def total(self, values): return sum(values)
    def mul(self, a, b): return a * b
    def public(self, a, b): return cgf2n(a) * b
    def const(self, byte): return cgf2n(PARAMS['embed'][byte])

ops = MPCOps()
left = [sgf2n.get_input_from(0) for _ in range(16)]
right = [sgf2n.get_input_from(1) for _ in range(16)]
claims = [[sgf2n.get_input_from(0) + sgf2n.get_input_from(1) for _ in range(2)] for _ in PUBLIC_CASES]
check_point()
# Validate both parties' AES-byte subfield inputs; honest-domain openings are
# always zero. Invalid-party inputs abort before any AES or diagnostic output.
for value in left + right:
    power256 = value
    for _ in range(8): power256 = power256 * power256
    valid_opening = blind_open(power256 + value)
    runtime_error_if(valid_opening != cgf2n(0), 'INPUT_DOMAIN_INVALID')
key = [a + b for a, b in zip(left, right)]
keys = expand_key(key, ops)
def aes_packed(block):
    return pack_embedded(encrypt_block([ops.const(x) for x in block], keys, ops), ops)
h = aes_packed(bytes(16))
tag_masks = [aes_packed(r['nonce'] + (1).to_bytes(4, 'big')) for r in PUBLIC_CASES[0]]
streams = [aes_packed(r['nonce'] + (2).to_bytes(4, 'big')) for r in PUBLIC_CASES[0]]
residuals = Array(len(PUBLIC_CASES) * 4, sgf2n)
for case_index, records in enumerate(PUBLIC_CASES):
    for record_index, record in enumerate(records):
        assert record['nonce'] == PUBLIC_CASES[0][record_index]['nonce']
        assert len(record['ciphertext']) == 16 and len(record['tag']) == 16
        tag = tag_masks[record_index] + ghash(h, record['aad'], record['ciphertext'], ops)
        actual_plaintext = streams[record_index] + cgf2n(pack_public(record['ciphertext']))
        residuals[4 * case_index + 2 * record_index] = tag + cgf2n(pack_public(record['tag']))
        residuals[4 * case_index + 2 * record_index + 1] = actual_plaintext + claims[case_index][record_index]
check_point()
'''
    program += diagnostic
    program += '''
@for_range(len(PUBLIC_CASES))
def binding_case(index):
    diagnose(index, [residuals[4 * index + j] for j in range(4)])
check_point()
print_ln('BINDING_SCOPE AES128_GCM_96BIT_NONCE_TWO_SINGLE_BLOCK_RECORDS')
print_ln('PROTOCOL_DONE')
'''
    (out / 'bind_gcm.mpc').write_text(program)
    metadata = {'base_rowspace_sha256': hashlib.sha256(base.encode()).hexdigest(),
                'generated_source_sha256': hashlib.sha256(program.encode()).hexdigest(),
                'case_names': case_names, 'expected': expected,
                'scope': 'record-layer binding with a pre-established authenticated key/context; not TLS handshake'}
    (out / 'build.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata))


if __name__ == '__main__': main()
