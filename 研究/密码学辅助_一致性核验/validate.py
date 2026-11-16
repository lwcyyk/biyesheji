"""Reproducible finite algebra validation. Refuses to overwrite run directories."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import platform
import random
from time import perf_counter
import unittest
import sys
from field import Field
from kernel import (IdealArithmetic, det_circuit, rank_matrix, masked_moments, moments_naive,
                    middle_product_five, private_norm, decode, run)
import reference

ROOT = Path(__file__).resolve().parent


def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
def hashes(): return {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob("*.py"))}
def support(vector): return [i for i, x in enumerate(vector) if x]
def distribution_digest(counter): return sha256(canonical([[list(k), v] for k, v in sorted(counter.items())]).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--out", required=True); parser.add_argument("--replay-of")
    args = parser.parse_args(); out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=False)
    source = hashes(); bundle_hash = sha256(canonical(source).encode()).hexdigest(); dump(out/"source_hashes.json", source)
    dump(out/"environment.json", {"started_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
         "platform": platform.platform(), "command": [sys.executable, *sys.argv], "source_sha256": bundle_hash,
         "mode": "IDEAL_ARITHMETIC_AND_SYNTHETIC_NATIVE_FIXTURES", "real_MPC": "NOT_RUN", "general_crypto_proof": "NOT_MACHINE_CHECKED"})
    started = perf_counter(); events = []

    class Recording(unittest.TextTestResult):
        def addSuccess(self, t): super().addSuccess(t); events.append({"test": t.id(), "status": "PASS"})
        def addFailure(self, t, err): super().addFailure(t, err); events.append({"test": t.id(), "status": "FAIL", "detail": self._exc_info_to_string(err, t)})
        def addError(self, t, err): super().addError(t, err); events.append({"test": t.id(), "status": "ERROR", "detail": self._exc_info_to_string(err, t)})
        def addSkip(self, t, reason): super().addSkip(t, reason); events.append({"test": t.id(), "status": "NOT_RUN", "reason": reason})

    with (out/"unittest.log").open("w", encoding="utf-8") as log:
        tests = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Recording).run(unittest.defaultTestLoader.loadTestsFromName("tests"))
    dump(out/"tests.json", events)
    if not tests.wasSuccessful():
        dump(out/"summary.json", {"status": "FAIL_UNIT_GATE", "tests": tests.testsRun}); return 1
    mismatch = []; f = Field(4)

    # ALL 16^4 public syndrome vectors; two independently implemented decoders.
    labels = f.labels(6); table = reference.sparse_table(6, 2, labels, 4, f.modulus); decoder_count = 0
    with (out/"decoder_exhaustive.jsonl").open("w", encoding="utf-8") as log:
        for seq in product(range(16), repeat=4):
            expected = support(table[seq]) if seq in table else None
            actual = decode(f, list(seq), labels, 2); other = reference.decode_prony(list(seq), labels, 4, f.modulus)
            ok = expected == actual == other; decoder_count += 1
            if not ok: mismatch.append({"decoder": seq})
            log.write(canonical({"moments": seq, "expected": expected, "BM": actual, "Prony": other, "matches": ok}) + "\n")

    # Every 0/1/2-sparse vector in F16^4, every two-coefficient polynomial mask.
    labels = f.labels(4); masks = list(product(range(16), repeat=2)); privacy_count = 0; mask_evaluations = 0
    with (out/"mask_privacy.jsonl").open("w", encoding="utf-8") as log:
        for size in range(3):
            for indices in combinations(range(4), size):
                simul = Counter()
                for weights in product(range(16), repeat=size):
                    vector = [0] * 4
                    for i, weight in zip(indices, weights): vector[i] = weight
                    seq = reference.moments(vector, labels, 4, 4, f.modulus)
                    simul[tuple(seq)] += 16 ** (2 - size)
                for amplitudes in product(range(1, 16), repeat=size):
                    delta = [0] * 4
                    for i, amplitude in zip(indices, amplitudes): delta[i] = amplitude
                    actual = Counter(tuple(moments_naive(f, delta, labels, r, 2)) for r in masks)
                    ok = actual == simul; privacy_count += 1; mask_evaluations += len(masks)
                    if not ok: mismatch.append({"mask_privacy": delta})
                    log.write(canonical({"input": delta, "support": indices, "mask_count": len(masks), "matches": ok,
                                         "actual_distribution_sha256": distribution_digest(actual), "simulator_distribution_sha256": distribution_digest(simul)}) + "\n")

    # Gate failures at small parameters are recorded, never discarded.
    gate_inputs = gate_queries = 0; gate_stats = {}
    with (out/"gate_exhaustive.jsonl").open("w", encoding="utf-8") as log:
        for k in [1, 2]:
            degree = (k + 1) * 3 - k * (k + 1) // 2
            omega = 15 ** (k + 1); highest = 0
            for values in product(range(4), repeat=4):
                if len(support(values)) <= k: continue
                columns = {x: [f.poly(values, f.mul(f.power(3, r), x)) for r in range(k + 1)] for x in range(1, 16)}
                bad = 0
                for x in product(range(1, 16), repeat=k + 1):
                    matrix = [[columns[c][row] for c in x] for row in range(k + 1)]
                    value = det_circuit(matrix, IdealArithmetic(f)); bad += value == 0; gate_queries += 1
                gate_inputs += 1; highest = max(highest, bad)
                ok = Fraction(bad, omega) <= Fraction(degree, 15)
                if not ok: mismatch.append({"gate_bound": values, "k": k})
                log.write(canonical({"input": values, "k": k, "single_gate_challenges_enumerated": omega, "bad_single_gate_challenges": bad,
                    "single_error_fraction": str(Fraction(bad, omega)), "bound_single": str(Fraction(degree, 15)),
                    "amplified_bad_pairs_exact_product": bad * bad, "amplified_pairs_denominator": omega * omega,
                    "amplified_bound": str(Fraction(degree, 15) ** 2), "amplified_count_method": "independent Cartesian-product identity, not a second enumeration", "matches": ok}) + "\n")
            gate_stats[str(k)] = {"max_bad_single_challenges": highest, "denominator": omega, "degree_bound": degree}

    # New negative controls: global nonzero filtering and naive repeated disclosure.
    views = []
    for delta in [[1, 1, 0, 0], [1, 2, 0, 0]]:
        counts = Counter()
        for r in masks:
            if all(f.poly(r, a) != 0 for a in labels): counts[tuple(moments_naive(f, delta, labels, r, 2))] += 1
        views.append(counts)
    accepted_masks = sum(views[0].values())
    filter_tv = Fraction(sum(abs(views[0][x] - views[1][x]) for x in set(views[0]) | set(views[1])), 2 * accepted_masks)
    flags = []
    for x, y in product(range(1, 16), repeat=2):
        a = [f.poly([1, 1], c) for c in [x, y]]; b = [f.poly([1, 2], c) for c in [x, y]]
        flags.append({"challenges": [x, y], "a_partial_zeros": [v == 0 for v in a], "b_partial_zeros": [v == 0 for v in b],
                      "a_norm_zero": private_norm(IdealArithmetic(f), *a) == 0,
                      "b_norm_zero": private_norm(IdealArithmetic(f), *b) == 0})
    naive_tv = Fraction(sum(x["a_partial_zeros"] != x["b_partial_zeros"] for x in flags), len(flags))
    norm_tv = Fraction(sum(x["a_norm_zero"] != x["b_norm_zero"] for x in flags), len(flags))
    dump(out/"counterexamples.json", {"global_nonzero_filter": {"field": 16, "inputs": [[1, 1, 0, 0], [1, 2, 0, 0]],
         "accepted_masks": accepted_masks, "TV": str(filter_tv), "same_zero_positions": True},
         "repeated_checks": {"view": "conditional verification stage with candidate empty; values [1,1] vs [1,2]", "naive_two_openings_TV": str(naive_tv),
                             "norm_only_TV": str(norm_tv), "enumerated_challenge_pairs": len(flags), "rows": flags},
         "expected": "All are deliberate unsafe/reduced-privacy variants, not failures of the stated candidate."})

    # Reproducible ideal runs over three field sizes, including actual 128-bit algebra.
    rng = random.Random(20261102); trial_counts = Counter(); trials = 0
    with (out/"trials.jsonl").open("w", encoding="utf-8") as log:
        for bits, n, count in [(4, 4, 200), (8, 8, 120), (128, 8, 40)]:
            fld = Field(bits)
            for number in range(count):
                count_bad = number % 5; delta = [0] * n
                for i in rng.sample(range(n), count_bad): delta[i] = rng.randrange(1, fld.q)
                kwargs = {"gate_challenges": [[rng.randrange(1, fld.q) for _ in range(3)] for _ in range(2)],
                          "gate_blind": rng.randrange(1, fld.q),
                          "attempts": [{"mask": [rng.randrange(fld.q), rng.randrange(fld.q)],
                                        "challenges": [rng.randrange(1, fld.q), rng.randrange(1, fld.q)], "blind": rng.randrange(1, fld.q)} for _ in range(2)]}
                result = run(fld, delta, **kwargs)
                ref = reference.simulate(delta, bits=bits, modulus=fld.modulus, norm_constant=fld.norm_constant(), **kwargs)
                ref_match = (result["status"] == ref["status"] and result["support"] == ref["support"]
                             and result["transcript"]["gate_opening"] == ref["gate_opening"]
                             and result["transcript"]["attempts"] == ref["attempts"])
                if not ref_match: mismatch.append({"reference_disagreement": number, "bits": bits})
                if result["status"] in ["LOCATED", "ALL_VALID"]: correct = result["support"] == support(delta)
                elif result["status"] == "MANY": correct = count_bad > 2
                else: correct = None
                trial_counts[(bits, result["status"], str(correct))] += 1; trials += 1
                # Incorrect toy-field outputs are permitted by the quantified error;
                # retain them as observations, never silently label every run PASS.
                if bits == 128 and correct is False: mismatch.append({"128_bit_counterexample": number})
                log.write(canonical({"field_bits": bits, "input": delta, "harness_randomness": kwargs, "actual_support": support(delta),
                                     "result": result, "reference": ref, "reference_matches": ref_match,
                                     "classification_correct": correct, "secure_randomness": False}) + "\n")

    native = {"status": "NOT_RUN", "reason": "optional cryptography dependency unavailable"}
    try:
        import native_demo
        native = native_demo.evaluate(); dump(out/"native_binding.json", native)
    except ImportError: dump(out/"native_binding.json", native)

    cost_rows = []
    for bits in [4, 8, 128]:
        fld = Field(bits)
        for n in [4, 8]:
            for amplified in [False, True]:
                repeat = 2 if amplified else 1
                kwargs = {"gate_challenges": [[j + 1 + 3 * r for j in range(3)] for r in range(repeat)],
                          "gate_blind": 7, "attempts": [{"mask": [1, 0], "challenges": [8 + j for j in range(repeat)], "blind": 10}], "amplified": amplified}
                timed = perf_counter(); answer = run(fld, [1, 2] + [0] * (n - 2), **kwargs); elapsed = perf_counter() - timed
                cost_rows.append({"field_bits": bits, "n": n, "amplified": amplified, "products": answer["secret_products"],
                                  "ideal_evaluator_seconds": elapsed, "NOT_A_REAL_MPC_BENCHMARK": True})
    dump(out/"costs.json", cost_rows)
    dump(out/"finite_summary.json", {"decoder_sequences": decoder_count, "sparse_decoder_reference_vectors": len(table),
         "privacy_input_vectors": privacy_count, "mask_evaluations": mask_evaluations,
         "dense_gate_inputs": gate_inputs, "single_gate_challenge_tuples": gate_queries, "gate_stats": gate_stats,
         "trial_runs": trials, "trial_counts": [{"bits": k[0], "status": k[1], "correct": k[2], "count": v} for k, v in sorted(trial_counts.items())],
         "counterexample_filter_TV": str(filter_tv), "naive_repetition_TV": str(naive_tv), "norm_repetition_TV": str(norm_tv), "mismatches": mismatch})
    summary = {"status": "PASS_STATED_ALGEBRA_CHECKS" if not mismatch and hashes() == source else "FAIL",
         "tests": tests.testsRun, "failures": len(tests.failures), "errors": len(tests.errors), "skipped": len(tests.skipped),
         "source_sha256": bundle_hash, "source_unchanged": hashes() == source, "unexpected_mismatches": mismatch,
         "not_established": ["originality", "real malicious-MPC security", "complete TLS protocol", "runtime performance advantage"],
         "wall_seconds": perf_counter() - started}
    if args.replay_of:
        prior = Path(args.replay_of).resolve()
        names = ["source_hashes.json", "decoder_exhaustive.jsonl", "mask_privacy.jsonl", "gate_exhaustive.jsonl", "counterexamples.json", "trials.jsonl", "native_binding.json", "finite_summary.json"]
        changed = [name for name in names if not (prior/name).exists() or (prior/name).read_bytes() != (out/name).read_bytes()]
        dump(out/"replay.json", {"prior": str(prior), "files_compared": len(names), "differences": changed, "timings_excluded": True})
        summary["replay_differences"] = changed
        if changed: summary["status"] = "FAIL"
    dump(out/"summary.json", summary); print(json.dumps(summary, ensure_ascii=False))
    return int(summary["status"] == "FAIL")


if __name__ == "__main__": raise SystemExit(main())
