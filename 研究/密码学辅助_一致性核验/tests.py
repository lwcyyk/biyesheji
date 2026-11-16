import itertools
import random
import unittest
from collections import Counter
from fractions import Fraction
from field import Field
import reference
from kernel import (FrozenBatch, Session, IdealArithmetic, det_circuit, private_norm,
                    masked_moments, moments_naive, middle_product_five, decode, run)


def args():
    return {"gate_challenges": [[1, 2, 3], [4, 5, 6]], "gate_blind": 7,
            "attempts": [{"mask": [1, 0], "challenges": [8, 9], "blind": 10}]}


class KernelTests(unittest.TestCase):
    def test_independent_field_multiplication(self):
        for bits in [4, 8]:
            f = Field(bits)
            for a in range(f.q):
                for b in range(f.q): self.assertEqual(f.mul(a, b), reference.mul(a, b, bits, f.modulus))
        f = Field(128); rng = random.Random(17)
        for _ in range(64):
            a, b = rng.getrandbits(128), rng.getrandbits(128)
            self.assertEqual(f.mul(a, b), reference.mul(a, b, 128, f.modulus))

    def test_cached_values_do_not_accept_booleans(self):
        f = Field(4); f.mul(1, 1); f.mul(0, 1)
        for a, b in [(True, 1), (False, 1), (1, True), (0, False)]:
            with self.assertRaises(ValueError): f.mul(a, b)

    def test_norm_has_no_nontrivial_zero(self):
        f = Field(4); self.assertEqual(1, f.trace(f.norm_constant()))
        for a, b in itertools.product(range(16), repeat=2):
            arithmetic = IdealArithmetic(f)
            self.assertEqual(a == b == 0, private_norm(arithmetic, a, b) == 0)
            self.assertEqual(3, arithmetic.products)

    def test_determinant_against_leibniz(self):
        f = Field(4); rng = random.Random(19)
        for n in [2, 3]:
            for _ in range(256):
                matrix = [[rng.randrange(16) for _ in range(n)] for _ in range(n)]
                arithmetic = IdealArithmetic(f)
                self.assertEqual(reference.determinant(matrix, 4, f.modulus), det_circuit(matrix, arithmetic))
                self.assertEqual({2: 2, 3: 9}[n], arithmetic.products)

    def test_middle_product_bilinear_basis(self):
        for bits in [4, 8, 128]:
            f = Field(bits)
            for i, j in itertools.product(range(2), range(5)):
                r = [0, 0]; s = [0] * 5; r[i] = s[j] = 1
                arithmetic = IdealArithmetic(f)
                actual = middle_product_five(arithmetic, r, s)
                expected = [f.mul(r[0], s[k]) ^ f.mul(r[1], s[k + 1]) for k in range(4)]
                self.assertEqual(expected, actual); self.assertEqual(5, arithmetic.products)

    def test_fast_masking_matches_direct(self):
        f = Field(8); labels = f.labels(6); rng = random.Random(23)
        for _ in range(256):
            d = [rng.randrange(256) for _ in labels]; r = [rng.randrange(256) for _ in range(2)]
            arithmetic = IdealArithmetic(f)
            self.assertEqual(moments_naive(f, d, labels, r, 2), masked_moments(arithmetic, d, labels, r))
            self.assertEqual(5, arithmetic.products)

    def test_decoder_all_small_sparse_vectors(self):
        f = Field(4); labels = f.labels(6)
        table = reference.sparse_table(6, 2, labels, 4, f.modulus)
        for fingerprint, vector in table.items():
            expected = [i for i, x in enumerate(vector) if x]
            self.assertEqual(expected, decode(f, list(fingerprint), labels, 2))
            self.assertEqual(expected, reference.decode_prony(list(fingerprint), labels, 4, f.modulus))

    def test_two_faults_and_product_counts(self):
        f = Field(4); a = args()
        out = run(f, [1, 2, 0, 0], **a)
        self.assertEqual("LOCATED", out["status"]); self.assertEqual([0, 1], out["support"])
        self.assertEqual(31, out["secret_products"])

    def test_mask_drop_requires_verification(self):
        f = Field(4)
        session = Session(f, FrozenBatch("x", ("epoch", 1), (1, 2, 0, 0)), 2, max_attempts=2)
        session.gate([[1, 2, 3], [4, 5, 6]], 7, batch_id="x", context=("epoch", 1))
        self.assertEqual([1], session.propose([1, 1]))
        self.assertNotEqual(0, session.verify([8, 9], 10)); self.assertEqual("READY", session.phase)
        self.assertEqual([0, 1], session.propose([1, 0]))
        self.assertEqual(0, session.verify([8, 9], 11)); self.assertEqual("LOCATED", session.finish()["status"])
        self.assertEqual(40, session.finish()["secret_products"])

    def test_retry_exhaustion_is_inconclusive(self):
        f = Field(4); a = args(); a["attempts"][0]["mask"] = [1, 1]
        out = run(f, [1, 2, 0, 0], **a)
        self.assertEqual("INCONCLUSIVE", out["status"])
        self.assertIsNone(out["support"])

    def test_input_and_context_replacement(self):
        f = Field(4); s = Session(f, FrozenBatch("x", ("epoch", 1), (1, 2, 0, 0)), 2)
        with self.assertRaises(ValueError): s.gate([[1, 2, 3], [4, 5, 6]], 7, batch_id="x", context=("epoch", 2))
        s.batch = FrozenBatch("x", ("epoch", 1), (0, 0, 0, 0))
        with self.assertRaises(ValueError): s.gate([[1, 2, 3], [4, 5, 6]], 7, batch_id="x", context=("epoch", 1))

    def test_single_use_and_phase_order(self):
        f = Field(4); s = Session(f, FrozenBatch("x", (), (0, 0, 0, 0)), 2)
        with self.assertRaises(ValueError): s.propose([1, 1])
        s.gate([[1, 2, 3], [4, 5, 6]], 7, batch_id="x", context=())
        with self.assertRaises(ValueError): s.gate([[1, 2, 3], [4, 5, 6]], 7, batch_id="x", context=())
        s.propose([0, 0]); s.verify([1, 2], 3)
        with self.assertRaises(ValueError): s.propose([1, 1])

    def test_global_nonzero_mask_filter_leaks(self):
        f = Field(4); labels = f.labels(4); views = []
        for delta in [[1, 1, 0, 0], [1, 2, 0, 0]]:
            counts = Counter()
            for r in itertools.product(range(16), repeat=2):
                if all(f.poly(r, a) != 0 for a in labels):
                    counts[tuple(moments_naive(f, delta, labels, r, 2))] += 1
            views.append(counts)
        total = sum(views[0].values()); self.assertEqual(total, sum(views[1].values()))
        tv = Fraction(sum(abs(views[0][x] - views[1][x]) for x in set(views[0]) | set(views[1])), 2 * total)
        self.assertGreater(tv, 0)

    def test_repetition_hides_partial_failures_only_with_norm(self):
        f = Field(4); raw_diff = norm_diff = 0
        for x, y in itertools.product(range(1, 16), repeat=2):
            u = [f.poly([1, 1], t) for t in [x, y]]
            v = [f.poly([1, 2], t) for t in [x, y]]
            raw_diff += [a == 0 for a in u] != [a == 0 for a in v]
            norm_diff += (private_norm(IdealArithmetic(f), *u) == 0) != (private_norm(IdealArithmetic(f), *v) == 0)
        self.assertEqual(56, raw_diff); self.assertEqual(2, norm_diff)

    def test_native_tag_does_not_bind_claimed_plaintext(self):
        try:
            import native_demo
            result = native_demo.evaluate()
        except ImportError:
            self.skipTest("optional cryptography package unavailable")
        self.assertEqual([1, 3], result["kernel_result"]["support"])
        self.assertTrue(result["tag_only_counterexample"]["tag_only_accepts_wrong_claimed_plaintext"])

    def test_full_reference_seeded(self):
        f = Field(4); rng = random.Random(41)
        for _ in range(100):
            delta = [rng.randrange(16) for _ in range(4)]
            kw = {"gate_challenges": [[rng.randrange(1, 16) for _ in range(3)] for _ in range(2)],
                  "gate_blind": rng.randrange(1, 16), "attempts": [{"mask": [rng.randrange(16), rng.randrange(16)],
                  "challenges": [rng.randrange(1, 16), rng.randrange(1, 16)], "blind": rng.randrange(1, 16)} for _ in range(2)]}
            out = run(f, delta, **kw)
            ref = reference.simulate(delta, bits=4, modulus=f.modulus, norm_constant=f.norm_constant(), **kw)
            self.assertEqual((ref["status"], ref["support"]), (out["status"], out["support"]))
            self.assertEqual(ref["gate_opening"], out["transcript"]["gate_opening"])
            self.assertEqual(ref["attempts"], out["transcript"]["attempts"])


if __name__ == "__main__": unittest.main(verbosity=2)
