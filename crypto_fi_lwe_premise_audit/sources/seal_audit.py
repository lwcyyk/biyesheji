"""Hash/source and scalar-evidence bookkeeping. No LWE solver or protocol implementation."""
from pathlib import Path
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"D:\毕业设计")
ROOT = BASE / "crypto_fi_lwe_premise_audit"
SRC = ROOT / "sources"


def readj(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def pin(path):
    p = Path(path)
    return dict(path=str(p), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def writej(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


locks = readj(SRC / "INPUT_LOCK.json")
assert all(pin(r["path"])["sha256"] == r["sha256"] for r in locks)
identity = dict(status="INFORMED_ASSUMPTION_AND_PAPER_REDUCTION_AUDIT",
                prior_derivation_and_review_context_visible=True,
                new_independent_reviews=0, human_reviews_this_turn=0,
                new_subagents=0, formal_proof_assistant=False)
actions = dict(protection_mechanism_implementations=0, LWE_solvers=0,
               cryptographic_attack_prototypes=0, large_crypto_experiments=0,
               author_contacts=0, emails=0, native_AS_RP_requests=0,
               finite_checks="Scalar finite-difference polynomial at degree25, factorial valuations, combination/resource counts, hashes and PDF structure")
specs = [
    ("FI_v4.pdf", "FI_v4", "E1_FROZEN_PDF_AND_TEX", "Current text sections3 and5-6, PDF5-7/16/19-20 and TeX LWE occurrence inventory. Hash-matched original-image readings PDF9-15/18-20 inherited from prior task; current source theorem anchors unchanged."),
    ("official_frodo_2021.pdf", "official_frodo_2021", "E1_PRIMARY_PDF_TARGETED", "Current text PDF12-13 Definitions2.7-2.9, PDF37-40 and bibliography50; original images12,13,38 inspected; Gaussian/worst-case images39-40 inherited through identical bytes."),
    ("AG2011_author.pdf", "AG2011_author", "E1_AUTHOR_FULL_PDF_TARGETED", "Full21page author file acquired; current section3 PDF7-10 and AppendixD/PDF19 text; original images8-9. Original sign/probability presentation issues recorded; current proof uses b-a.x and exact table probabilities."),
    ("ACPS2009_author.pdf", "ACPS2009_author", "E1_AUTHOR_FULL_PDF_TARGETED", "Full23page author file acquired; current PDF6 context and9-10 Lemma2 text; original images9-10. Source oracle conversion distinguished from later finite sample-count refinement."),
    ("Steiner2025v3.pdf", "Steiner2025v3", "E1_ARXIV_FIXED_VERSION_PDF_TARGETED", "Full32page v3 acquired; current PDF1-3 and Definition15/Theorem16 text, PDF18 small-secret/small-error paragraph and theorem23, PDF23 finite-estimate discussion; original image18."),
    ("Regev2009_author.pdf", "Regev2009_author", "E1_AUTHOR_FULL_PDF_TARGETED", "Full37page May2009 author file acquired; current p2 original LWE model and informal Theorem1.1, p5-7 context text; original image2. No whole-paper reading claim."),
]
primary = []
for file, slug, grade, scope in specs:
    p = SRC / file
    pf = readj(SRC / (slug + "_preflight.json"))
    assert pf["verdict"] == "PASS" and pf["sha256"] == pin(p)["sha256"]
    primary.append(dict(pin(p), evidence_grade=grade, reading_scope=scope,
                        preflight=pin(SRC / (slug + "_preflight.json"))))
assert pin(SRC / "FI_v4.pdf")["sha256"] == "bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4"

record = {
    "schema": "fi-lwe-premise-audit/source-and-reading/1",
    "date_asia_shanghai": "2026-11-09", "identity": identity,
    "skills": ["academic-research-suite: scoped primary-source and assumption audit, performed inline", "pdf: read-only structural preflight and original-image checks"],
    "historical_inputs": locks,
    "mathematical_input": "ROUND-005 reviewed citation theorem and FI-AFFINE-SUPPORT-PUBLISHED-1.0; A/B/D inherited with their original hypotheses and provenance",
    "historical_inputs_modified": False,
    "primary_PDFs": primary,
    "source_TeX": dict(pin(SRC / "articlev08.tex"), scope="Definition inventory, parameter/algorithm sampling, Lemma6.8/Theorem6.9, stated references; source has no parameterized LWE experiment"),
    "normal_form_actual_sources": {
        "Frodo2021": "Definitions2.7-2.9 pp12-13; Theorems5.9-5.10 p38; quantified m+n+k source samples and2^-k loss for power-of-two q",
        "ACPS2009": "Lemma2 pp9-10: prime-power oracle transformation; preliminary O(n^2) sampling discussion in original, distinct from later tight sample refinement",
        "historical_hand_instantiation": pin(BASE / "crypto_frodo_common_parameter_closure/CORRECTNESS_ATTACK_COMPATIBILITY.md"),
    },
    "CJL_composite_source": {
        "title": "Learning with Alternating Moduli, Arora-Ge over Composite Moduli, and Weak PRFs",
        "authors": ["Yilei Chen", "Liheng Ji", "Wenjie Li"],
        "landing": "https://eprint.iacr.org/2025/968",
        "current_landing_metadata": "Last revision2026-09-09, three revisions, minor revision of CRYPTO2026 publication",
        "conference_metadata": "CRYPTO2026 PartIII, LNCS16802, pp201-231, DOI10.1007/978-3-032-35377-1_7; conference program paperId10/pubkey37375/pages31",
        "indexed_primary_version_date": "2025-05-27",
        "indexed_channel_total_lines": 4025,
        "read_scope": "Lemma5-6, section4 Algorithm1/Lemma31/Corollary32 and Lemmas33-34/proof, AppendixA Proposition53; exact acquired excerpts retained",
        "excerpts": pin(SRC / "CJL2025_scoped_indexed_excerpts.txt"),
        "evidence_grade": "E2_PRIMARY_INDEXED_SCOPED_TEXT",
        "original_pdf_bytes_obtained": False, "original_images_obtained": False,
        "source_obstruction": "Direct PDF/screenshot403; indexed text is dated2025, current/accepted PDF correspondence unresolved",
        "mathematical_treatment": "Current informed self-contained finite-difference/union-bound/ring-solve proof establishes used claim independently of missing images; method attributed to AG/CJL, no new generic-method claim",
    },
    "retrieval_routes": [
        {"source": "AG2011", "basis": "New author-host PDF located by exact-title search", "result": "Web fetch403, native HTTPS download200 and complete byte hash/preflight"},
        {"source": "CJL", "basis": "New exact composite-modulus title/ePrint ID", "result": "Landing200; direct native/web PDF403; new indexed search-reference succeeds with dated primary text; screenshot still403"},
        {"source": "CJL versions", "basis": "Landing revision link and exploratory timestamp form", "result": "Version archive403; unverified timestamp-form test supplied no version evidence and is excluded from version attribution"},
        {"source": "CJL conference", "basis": "Author outputs link and official program JavaScript/XHR URLs observed in HTML", "result": "Official program and currentProgram JSON200, exact title/authors/DOI/ePrint metadata; referenced CryptoDB pubkey endpoint unavailable; no paper PDF obtained"},
        {"source": "ACPS2009", "basis": "Frodo Theorem5.10 reference15 and new author-host title search", "result": "MIT author-host PDF200, complete bytes/preflight/images"},
        {"source": "Steiner", "basis": "Exact algebraic LWE title from targeted search", "result": "Fixed arXiv v3 PDF200, metadata and targeted read"},
        {"source": "Regev2009", "basis": "FI citation and exact-title author search", "result": "NYU author-host PDF200, targeted original model/main-theorem read"},
    ],
    "web_receipts": [pin(p) for p in sorted(SRC.glob("WEB_*.json"))],
    "source_URLs": {
        "AG2011": "https://users.cs.duke.edu/~rongge/LPSN.pdf",
        "AG_ECCC_metadata": "https://eccc.weizmann.ac.il/report/2010/066/",
        "ACPS2009": "https://people.csail.mit.edu/cpeikert/pubs/kdm-learning.pdf",
        "Regev2009": "https://cims.nyu.edu/~regev/papers/qcrypto.pdf",
        "Steiner_v3": "https://arxiv.org/pdf/2402.07852v3",
        "CJL_author_metadata": "https://www.chenyilei.net/outputs.html",
        "CJL_conference_program": "https://crypto.iacr.org/2026/program.php",
    },
    "finite_evidence": [pin(SRC / "SCALAR_COUNTS.json"), pin(SRC / "FINITE_DIFFERENCE_CHECK.json")],
    "proof_status": {
        "normal_form_count": "Source-verified with informed paper instantiation",
        "composite_bounded_error_mapping": "Informed self-contained paper proof; min atom, finite-difference identity, union bound, prime-power linear solving and fresh-sample lifting explicit",
        "finite_checks": "Finite evidence only, no general theorem certification or solver experiment",
        "independent_review_of_current_paper_proof": "Pending; none commissioned/executed this turn",
    },
    "exact_obstructions": [
        "FI omitted parameterized Lemma6.8 reduction: exact same-secret sample and time budget cannot be uniquely recovered",
        "No proven simulation turning n/3n sample input or actual FI multi-secret views into required rich independent samples",
        "No current fixed-sample hardness theorem/solver established for exact CF-1 tuple",
        "CJL original/current/formal PDF version correspondence and images missing; used mathematics separately proved",
    ],
    "action_counts": actions,
    "local_source_inventory": [pin(p) for p in sorted(SRC.iterdir()) if p.is_file() and p.name != "SEAL_VALIDATION.json"],
}
writej(ROOT / "SOURCE_AND_READING_RECORD.json", record)

verdict = {
    "schema": "fi-lwe-premise-audit/verdict/1", "date_asia_shanghai": "2026-11-09",
    "overall": "RICH_SAMPLE_PREMISE_COVERED_FIXED_SAMPLE_PREMISE_UNRESOLVED_CLAIM_NARROWED",
    "overall_chinese": "丰富同秘密样本前提已被成熟算法覆盖；固定样本前提与源定理对应未决；构造不安全性保持，条件定理主张收窄",
    "identity": identity,
    "frozen_family": {"n": "8lambda", "D": "8ceil(log2n)", "q": "2^D", "chi": "exact fixed chi640 on[-12,12]", "mbar": 8, "nbar": 8, "T": "n", "minimum_error_atom": "1/65536"},
    "source_assumption": {"unique_exact_FI_LWE_tuple_recovered": False, "missing": ["m per secret", "sample/time quantifiers", "full auxiliary-view simulation", "explicit QPT experiment"], "printed_formula_locations": ["FI PDF19 Lemma6.8", "FI PDF20 Theorem6.9"], "formal_completions_separately_labeled": True},
    "exact_problems": {
        "NF_n": {"distribution": "A uniform n by n; s,e independent chi640^n; b=A s+e modq vs uniform", "status": "ASSUMPTION_NOT_SETTLED_BY_THIS_AUDIT"},
        "US_3n": {"distribution": "A uniform3n by n; s uniformZq^n; e iid chi640; b=A s+e vs uniform", "status": "ASSUMPTION_NOT_SETTLED_BY_THIS_AUDIT"},
        "normal_form_relation": "Adv_NF(n,m)<=Adv_US(n,m+n+k)+2^-k; m=n,k=n gives3n",
        "NF_US_polynomial_new_samples": {"status": "COVERED_BY_KNOWN_METHOD_WITH_INFORMED_SELF_CONTAINED_PROOF", "model": "one fixed secret, fresh independent uniform coefficient vectors, fresh independent exact chi errors", "classic_algorithm": True, "method": "AG linearization with CJL prime-power precision loss; finite-difference proof and ring elimination", "parameters": {"d": 25, "eta": "2^-16", "q0": "2^27 divides q", "gcd_d_factorial_q0": "2^22", "recovered_modulus": 32, "N": "binom(n+25,25)", "M": "2^20*(27*N+tau+1)", "training_failure": "<exp(-8*tau)"}, "search": {"NF_samples": "M", "US_samples": "M+n+kappa", "US_success": ">=1-exp(-8*tau)-2^-kappa"}, "decision": {"samples": "M+t", "gap": ">=1-exp(-8*tau)-(25/32)^t", "choice": "tau=t=lambda"}, "cost_upper_bounds": {"sample_order": "Theta(n^25)", "dense_bit_time": "O(n^75) with fixed q0/d; original input reading O(M*n*D) included", "dense_storage": "O(n^50)", "optimality_or_lower_bound_claimed": False}},
    },
    "claims_A_to_E": {
        "A": {"status": "VERIFIED_INHERITED", "claim": "CF-1 original UE game efficient affine-support distinguisher", "hardness_assumptions": 0},
        "B": {"status": "VERIFIED_INHERITED", "claim": "CF-1 common pointwise correctness for n updates"},
        "C": {"rich_samples": "VERIFIED_BY_INFORMED_PAPER_PROOF", "fixed_n_or_3n": "NEEDS_CLARIFICATION"},
        "D": {"status": "VERIFIED_WITH_RECORDED_SEMANTICS_INHERITED", "gap": "T/(T+1)^2*alpha*(1-theta)", "scope": "independent uniform random-ciphertext interpretation, independent firewall endpoints and shared abort response kernel"},
        "E": {"status": "CASE_DEPENDENT", "rich_same_chi_assumption": "Premise false in CF-1, so conditional implication may be vacuous there", "fixed_sample_assumption": "Nonempty-hardness premise and precise source reduction not certified", "wider_Gaussian_assumption": "Distribution/parameter reduction to exact chi640 missing", "counterexample_under_certified_true_hardness_premise": False},
    },
    "finite_instance": {"n": 128, "D": 56, "lambda": 16, "UE_calls_max": 385, "UE_gap": ">=1-(3/4)^128-2^-59", "rich_M": "949649364703984072529574454995451904", "rich_M_log2_interval": "(119,120)", "fixed_NF_samples": 128, "fixed_US_samples": 384, "practical_LWE_break_claimed": False},
    "official_configs": {"640": "Affine-support game bound inherited; current rich algebraic precision modulus1, no guarantee from this route", "976": "Same distinction; current rich algebraic precision modulus1", "1344": "Rich sample algorithm applies using d13, v2(13!)10, q0=2^14 and recovered modulus16; actual fixed sample/UE correctness/author implementation separate", "complete_UE_correctness_and_maxT": "Unresolved as previously recorded"},
    "source_limit": "CJL scoped indexed2025 text available; original/current/formal PDF bytes/images unavailable. Used ring claim has current self-contained proof; publication-version mapping unresolved.",
    "contribution": {"paper_wording_adjustment_required": True, "retained": "Specific UE source-hiding cryptanalysis, parameter/sample quantifier boundary and hybrid-proof audit; independent cryptanalysis core candidate", "new_generic_algebraic_method_claimed": False, "certified_nonempty_LWE_hardness_domain_refutation_of_Theorem6_9": False, "global_priority_or_implementation_upgrade": False},
    "minimum_decision_changing_evidence": ["Complete FI Lemma6.8 parameterized reduction specifying m(n), distributions, shared-A view and runtime", "Exact fixed-sample CF-1 solver or matching hardness-source reduction for NF_n/US_3n", "CJL original/current accepted PDF and version correspondence", "Concrete counterexample to current paper proof under its actual uniform/independent rich sample hypotheses"],
    "action_counts": actions,
    "protection_implementation_separation_gate_satisfied": False,
    "deliverables": ["EXACT_LWE_ASSUMPTIONS.md", "BOUNDED_ERROR_ALGORITHM_MAPPING.md", "THEOREM_IMPACT_AND_CLAIM_WORDING.md", "SOURCE_AND_READING_RECORD.json", "VERDICT.json"],
}
writej(ROOT / "VERDICT.json", verdict)

checks = dict(historical_inputs_unchanged=True, historical_input_count=len(locks),
              pdf_preflights_pass=6, finite_scalar_identity=readj(SRC / "FINITE_DIFFERENCE_CHECK.json")["exact_verified"],
              json_errors=[], broken_local_links=[], forbidden_style=[], deliverables=[])
for name in verdict["deliverables"]:
    p = ROOT / name
    checks["deliverables"].append(pin(p))
    if p.suffix == ".md":
        t = p.read_text(encoding="utf-8")
        if re.search("不是.{0,80}而是", t):
            checks["forbidden_style"].append(name)
        cleaned = re.sub(r"`[^`]*`", "", t)
        cleaned = re.sub(r"\\\[.*?\\\]", "", cleaned, flags=re.S)
        for target in re.findall(r"\]\(([^)]+)\)", cleaned):
            if not target.startswith(("http:", "https:")) and not (p.parent / target).resolve().exists():
                checks["broken_local_links"].append(dict(file=name, target=target))
for p in list(ROOT.glob("*.json")) + list(SRC.glob("*.json")):
    try:
        readj(p)
    except Exception as e:
        checks["json_errors"].append(dict(path=str(p), error=str(e)))
assert all(pin(r["path"])["sha256"] == r["sha256"] for r in locks)
writej(SRC / "SEAL_VALIDATION.json", checks)
assert not checks["json_errors"] and not checks["broken_local_links"] and not checks["forbidden_style"]
assert checks["finite_scalar_identity"]
print(json.dumps({k: v for k, v in checks.items() if k != "deliverables"}, ensure_ascii=False))
print("Five requested deliverables sealed; history remains read-only.")
