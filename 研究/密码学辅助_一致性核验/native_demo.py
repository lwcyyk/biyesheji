"""Synthetic AES-GCM linkage examples. A cleartext ORACLE, not MPC or TLS."""
import hashlib
import random
from field import Field
from kernel import run


def expected_tag_and_plaintext(key, nonce, aad, ciphertext):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if len(nonce) != 12: raise ValueError("demo only supports 96-bit nonce")
    stream = b""
    enc = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    for index in range((len(ciphertext) + 15) // 16):
        stream += enc.update(nonce + (index + 2).to_bytes(4, "big"))
    plain = bytes(a ^ b for a, b in zip(ciphertext, stream))
    reconstructed = AESGCM(key).encrypt(nonce, plain, aad)
    if reconstructed[:-16] != ciphertext: raise AssertionError("native CTR/GCM linkage")
    return reconstructed[-16:], plain


def evaluate():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import cryptography
    records = []; residuals = []; originals = []
    for index in range(4):
        key = hashlib.sha256(("SYNTHETIC-KEY-" + str(index)).encode()).digest()[:16]
        nonce = index.to_bytes(12, "big"); aad = ("SYNTHETIC-CONTEXT-" + str(index)).encode()
        plain = ("access_token=SYNTHETIC-" + str(index) + ";refresh_token=SYNTHETIC-ONLY").encode()
        encoded = AESGCM(key).encrypt(nonce, plain, aad); ciphertext, tag = encoded[:-16], encoded[-16:]
        originals.append((key, nonce, aad, ciphertext, tag, plain))
        altered = bytearray(tag)
        if index in [1, 3]: altered[-1] ^= index
        expected, decoded = expected_tag_and_plaintext(key, nonce, aad, ciphertext)
        assert decoded == plain
        residual = int.from_bytes(expected, "big") ^ int.from_bytes(altered, "big")
        residuals.append(residual)
        records.append({"record": index, "ciphertext_hex": ciphertext.hex(), "received_tag_hex": altered.hex(),
                        "expected_tag_hex": expected.hex(), "residual": residual})
    f = Field(128); rng = random.Random(20261102)
    randomness = {"gate_challenges": [[rng.randrange(1, f.q) for _ in range(3)] for _ in range(2)],
                  "gate_blind": rng.randrange(1, f.q),
                  "attempts": [{"mask": [rng.randrange(f.q), rng.randrange(f.q)],
                                "challenges": [rng.randrange(1, f.q), rng.randrange(1, f.q)],
                                "blind": rng.randrange(1, f.q)} for _ in range(2)]}
    outcome = run(f, residuals, **randomness)
    assert outcome["status"] == "LOCATED" and outcome["support"] == [1, 3]

    key, nonce, aad, ciphertext, tag, plain = originals[0]
    expected, decoded = expected_tag_and_plaintext(key, nonce, aad, ciphertext)
    forged_plaintext = bytes([plain[0] ^ 1]) + plain[1:]
    tag_difference = int.from_bytes(expected, "big") ^ int.from_bytes(tag, "big")
    binding_difference = int.from_bytes(decoded[:16], "big") ^ int.from_bytes(forged_plaintext[:16], "big")
    assert tag_difference == 0 and binding_difference != 0
    return {"mode": "CLEAR_SYNTHETIC_ORACLE_NOT_MPC_NOT_LIVE_TLS", "cryptography_version": cryptography.__version__,
            "records": records, "randomness": randomness, "kernel_result": outcome,
            "tag_only_counterexample": {"tag_residual": tag_difference, "plaintext_binding_residual": binding_difference,
                                        "tag_only_accepts_wrong_claimed_plaintext": True},
            "missing_security": "The experimenter knows all keys. Production must prove/securely compute AES output and immutable share linkage; this kernel does not provide them."}


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
