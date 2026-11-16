"""Manuscript/source bookkeeping and document QA only; no cryptographic solver."""
from pathlib import Path
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"D:\毕业设计")
ROOT = BASE / "crypto_fi_research_manuscript_v1"
EV = ROOT / "evidence"
SRC = ROOT / "sources"


def readj(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def pin(p):
    p = Path(p)
    return dict(path=str(p), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def writej(p, x):
    Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


snap = readj(EV / "HISTORICAL_INPUT_SNAPSHOT.json")
assert len(snap) == 157
assert all(pin(x["path"])["sha256"] == x["sha256"] and pin(x["path"])["bytes"] == x["bytes"] for x in snap)
copies = readj(EV / "SOURCE_COPY_RECORD.json")
assert all(pin(x["source"])["sha256"] == x["sha256"] == pin(x["copy"])["sha256"] for x in copies)
mainline = readj(EV / "MAINLINE_SOURCE_LOCK.json")
assert all(pin(x["path"])["sha256"] == x["sha256"] for x in mainline["files"])
rev = readj(EV / "REVIEW_INPUT_VERIFICATION.json")
assert rev["all_match"] and rev["canonical_match"] and rev["files_checked"] == 32
round5 = readj(EV / "ROUND005_REVIEW_VERIFICATION.json")
assert all(x["all_match"] for x in round5) and sum(x["checked"] for x in round5) == 39
finite = readj(EV / "FINITE_SCALAR_CHECKS.json")
assert all(x["sum_matches"] and x["mu_matches"] and x["complete_two_term_bound"] for x in finite["certificate_rows"])
assert finite["CF128"]["correctness_check"] and finite["CF128"]["epsilon_bound_2_to_minus59"]
assert all(x["value_mod4"] == 0 for x in finite["q4_d2_full_precision_control"])

identity = dict(status="INFORMED_REVISION_PROOF_INTEGRATION_AND_ACADEMIC_WRITING",
                prior_authorship_and_reviews_visible=True, new_independent_reviews=0,
                exact_runtime_model_id=None, author_reviewer_model_separation_verified=None,
                new_subagents=0, human_peer_review=0, formal_proof_assistant=0)
actions = dict(LWE_solvers=0, attack_prototypes=0, protection_mechanism_implementations=0,
               large_cryptographic_experiments=0, project_test_reruns=0,
               native_AS_RP_requests=0, account_operations=0, author_contacts=0,
               messages_or_emails=0, private_material_decryptions=0,
               public_web_tool_calls=1, public_search_queries=3,
               public_journal_PDF_downloads=1,
               finite_scope="Exact scalar/certificate and eight q4 values; no crypto instances")

pdf_specs = [
    ("S1", "FI_journal_20261110.pdf", "FI journal current download, byte-identical arXiv2410.03948v4", "E1_PRIMARY_PDF", "Inherited matching-image scopes PDF9-15,18-20; current source/formula integration and fresh byte check; TeX locators also used"),
    ("S2", "official_frodo_2021.pdf", "FrodoKEM specification2021-06-04", "E1_PRIMARY_PDF_TARGETED", "Definitions2.7-2.9 pp12-13, Table3/4 p25, Theorems5.9/5.10 p38 and Gaussian discussion37-40 inherited scoped readings; cover author list read this turn"),
    ("S3", "KLR2019.pdf", "KLR2019 institution author version71pages", "E1_PRIMARY_PDF_TARGETED", "Inherited original images17 Def11,27 Def14,44 AppB.2; no whole-paper coverage claim"),
    ("S4", "AG2011_author.pdf", "AG-associated21page author preprint", "E1_PRIMARY_PDF_TARGETED", "Inherited text7-10 and19; images8-9; author file distinct from conference typesetting"),
    ("S6", "ACPS2009_author.pdf", "ACPS2009 author23page version", "E1_PRIMARY_PDF_TARGETED", "Inherited text6,9-10 and original images9-10, Lemma2"),
    ("S7", "Regev2009_author.pdf", "May2009 author37page version", "E1_PRIMARY_PDF_TARGETED", "Inherited p2 original model/informal Theorem1.1 and image, context5-7"),
    ("S8", "Steiner2025v3.pdf", "arXiv2402.07852v3,2025-03-29,32pages", "E1_PRIMARY_PDF_TARGETED", "Inherited pp2-3,18 and23, original image18; field model and assumptions retained"),
]
sources = {i: dict(file=pin(SRC / f), version=v, evidence_grade=g, reading_scope=s) for i, f, v, g, s in pdf_specs}
sources["S1"]["source_TeX"] = pin(SRC / "articlev08.tex")
sources["S1"]["fresh_download_URL"] = "https://fi.episciences.org/17222/pdf"
sources["S1"]["structural_preflight"] = readj(EV / "FI_JOURNAL_PREFLIGHT.json")
sources["S5"] = dict(file=pin(SRC / "CJL2025_scoped_indexed_excerpts.txt"),
                     version="Indexed primary text dated2025-05-27; current/CRYPTO2026 byte correspondence unresolved",
                     evidence_grade="E2_PRIMARY_INDEXED_SCOPED_TEXT", original_PDF_sha256=None,
                     reading_scope="Algorithm1, Lemma31/33-34, Prop53 via inherited acquired lines1192-1763 and2891 onward",
                     mathematical_role="Method attribution; manuscript AppendixA is self-contained", status="SOURCE_VERSION_UNRESOLVED")
sources["S9"] = dict(url="https://eprint.iacr.org/2021/221", version="FI-cited2024 extended Lemma5.7",
                     evidence_grade="BIBLIOGRAPHIC_AND_INHERITED_TRANSCRIPTION_ONLY",
                     reading_scope="Identity and predecessor responsibility only; exact extended formula images unavailable",
                     original_PDF_sha256=None, status="SOURCE_UNRESOLVED")
sources["S10"] = dict(url="https://github.com/microsoft/PQCrypto-LWEKE/issues/35",
                      evidence_grade="PRIMARY_MAINTAINER_STATEMENT_IN_HASH_PINNED_HISTORY",
                      historical_receipt=pin(BASE / "crypto_fi_original_game_decision/sources/web_search_4.json"),
                      reading_scope="Nov27,2024 CDF correction and last-entry explanation; inherited source read")
sources["E1"] = dict(citation=pin(BASE / "crypto_branch_monitor/round_005/THEOREM_FOR_CITATION.md"),
                     review_checks=round5, identity_scope="One two-phase AI review: phase1 no author derivation history; phase2 same reviewer author-proof comparison; N1 and H1 informed provenance separate")
sources["E2"] = dict(review_manifest=pin(BASE / "crypto_fi_lwe_independent_review/MANIFEST.json"),
                     mathematical_review=pin(BASE / "crypto_fi_lwe_independent_review/MATHEMATICAL_REVIEW.md"),
                     corrections=pin(BASE / "crypto_fi_lwe_independent_review/CORRECTIONS_AND_CLAIM_IMPACT.md"),
                     provenance=pin(BASE / "crypto_fi_lwe_independent_review/INPUT_AND_REVIEW_PROVENANCE.json"),
                     identity="AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW", independent_blind_review=False,
                     scope="LWE mathematics rederived after author proof visible; UE attack/correctness inherited only")
sources["E3"] = dict(fixed_a_proof=pin(BASE / "crypto_frodo_unconditional_support/DIRECT_PROBABILITY_PROOF.md"),
                     certificates=pin(SRC / "PARAMETER_CERTIFICATES.json"),
                     prior_application_audit=pin(BASE / "crypto_fi_original_game_decision/APPLICATION_PRIORITY_AUDIT.md"),
                     premise_audit=pin(BASE / "crypto_fi_lwe_premise_audit/VERDICT.json"),
                     reading_scope="Main prior reports, frozen source metadata and explicit scoped/inherited proof records; all directory accesses are not asserted semantic reads")
sources["E4"] = dict(source_lock=mainline, reading_scope="11 listed mainline reports full or targeted evidence paragraphs; old fixture source hash-only, only its contract projection semantically used",
                     versions=["ONLINE_TRUSTED_STATE_V1", "CASDOOR_NATIVE_ISOLATED_V1 2026-11-06", "G1-2026-11-09-r01"],
                     current_native_requests=0, current_mechanism_implementations=0)


def claim(i, title, loc, obj, quant, assumptions, deps, src, status, limits, reviewer):
    return dict(id=i, claim=title, manuscript_location=loc, precise_object=obj,
                quantifiers=quant, assumptions=assumptions, dependencies=deps,
                source_ids=src, evidence_status=status, limitations=limits,
                review_identity_and_scope=reviewer)


ue_scope = "ROUND-005 two-stage AI review as registered; current informed integration; no current human review"
lwe_scope = "Author-proof-visible targeted LWE review; current informed repair; no blind/cross-model/human certification"
claims = [
    claim("C01", "Published target identity", "§1.1", "Current FI journal download and frozen arXiv2410.03948v4", "Byte equality of464697byte files on2026-11-10", ["SHA256 byte identity; not acceptance-day manuscript identity"], [], ["S1"], "VERIFIED_SOURCE", "Future revisions separate", "Source audit"),
    claim("C02", "Ord column-count/bit-plane normalization", "§2.2", "Printed Ord definition and n-column Upd", "All C1,S of declared dimensions", ["Actual column-count overload and matching Tensor order"], ["C01"], ["S1","E1"], "EXPLICIT_TYPE_NORMALIZATION", "Literal uncompleted nbar-domain program has a type gap; behavior-changing patch separate", ue_scope),
    claim("C03", "Four-query original-game legality", "§3.1", "rand-ind-eu-cpa backward-leak game PDF9-11", "One honest parent; equal messages; zero Key/Dec/ordinaryUpd/tape queries", ["Printed interface and empty K* least closure"], ["C01"], ["S1","E1"], "PROVED_UNDER_PRINTED_GAME", "No exact external C* reconstruction needed for empty intersection", ue_scope),
    claim("C04", "Exact recovery on invertible update block", "§3.2", "Y=HP1+rP2 overZ_(2^D)", "Every valid update and invertible P2", ["Known support; public P1/P2/parent; no extra printed noise"], ["C02"], ["S1"], "PROVED_UNDER_STATED_MODEL", "No generic LWE solver or message attack claimed", ue_scope),
    claim("C05", "Real-fresh conditional anti-concentration", "§4 定理1", "First-row event exists r in support^n", "Every pre-fixed A and positive-probability P2=p", ["Independent chi calls/coordinates; fresh Enc parent; retain F1 and omit simultaneous P1/U1 conditioning"], ["C02","C04"], ["E1","E3","S1"], "PROVED_UNDER_STATED_MODEL", "Not every fixed P1 posterior; exponent n", ue_scope),
    claim("C06", "Joint one-shot advantage", "§3.2、§4 (10)", "Two original game outputs", "alpha=Pr inv; beta=fresh joint inv and E", ["Same prefix law; independent fair singular output"], ["C03","C05"], ["E1"], "PROVED_UNDER_STATED_MODEL", "Absolute gap=Delta; bias=Delta/2; success=(1+Delta)/2", ue_scope),
    claim("C07", "Adaptive first-invertible bound", "§5 定理2", "P2-only stopping with one fresh parent per boundary", "k<=T real Next; beta_selected<=p_k epsilon", ["J reads only P2 sequence; no screening by P1 or parent"], ["C03","C05"], ["E1","E3"], "PROVED_UNDER_STATED_MODEL", "More general adaptive selection needs separate analysis", ue_scope),
    claim("C08", "Common pointwise correctness", "§6.2 定理3", "CF-1 n8lambda,D8ceil(log2n),chi640,B2", "Every lambda>=2, fixed A, honest sample/message, chain<=n updates", ["Ord normalization; exact finite support; full initial residual"], ["C02"], ["S1","S2","E1","E3"], "PROVED_UNDER_STATED_MODEL", "Not author uint16 implementation equivalence", ue_scope),
    claim("C09", "CF-1 original-game near-maximal gap", "§6.3 定理4", "Same parameters/sampler as C08", "lambda grows; <=3n+1 calls; Delta>=1-(3/4)^n-epsilon_n", ["Balanced chi640 parity; gamma64<1/2; independent token calls"], ["C06","C07","C08","C10"], ["E1","E3"], "PROVED_UNDER_STATED_MODEL", "n64 epsilon can be1; syntactic domain membership does not certify hardness", ue_scope),
    claim("C10", "Finite three-table probability certificates", "§7、附录B", "Ideal independent chi640/976/correct1344 and printed UE", "Each fixed A; epsilon640<=2^-751,976<=2^-1118,1344<=2^-1532", ["Exact signed masses;64fold no merge; modular convolution contraction"], ["C05"], ["S2","S10","E1","E3"], "VERIFIED_FINITE_CERTIFICATE", "First-row event only; not correctness/failure measurement", "Three peaks/two-term bounds reviewed; N1 rank refinement informed separately"),
    claim("C11", "UE resource and sampling ledger", "§6.3 (20)", "At most k ordinary Enc/Next/token and one challenge", "CF-1 k=n, D=O(logn)", ["School arithmetic; full token read; challenge branch maximum sampled"], ["C03","C04","C07"], ["E1","E3"], "INFORMED_RESOURCE_BOUND", "Upper bounds, no optimality; final randomness branch repaired here", "Current informed cost repair R13"),
    claim("C12", "General partial recovery", "附录A.1、A.3 定理5", "Z_(2^c) form-module linearization with y0=1", "Every fixed secret; iid uniform rows; each integer error point mass>=eta", ["Independent errors; finite-difference identity; choose from full formal linearized solution space"], [], ["S4","S5","E2"], "PROVED_UNDER_STATED_MODEL", "Precision q0/gcd(d!,q0); trivial if modulus1", lwe_scope),
    claim("C13", "Total deterministic paper solver", "附录A.2", "M by N-1 affine ring system", "All well-formed inputs, including inconsistent systems", ["Fixed monomial/pivot tie order; reversible row/column operations; reduced-modulus division; final check"], ["C12"], ["E2"], "REPAIR_APPLIED", "No solver implementation executed; complete row log not retained free of cost", lwe_scope),
    claim("C14", "CF-1 shift and precision", "§8.2、附录A.4", "Exact chi640,q0=2^27,degree25", "Every lambda>=2 and positive tau", ["b+12 only training; q0 divides q; eta2^-16; v2(25!)22"], ["C12","C13"], ["S2","E2"], "PROVED_UNDER_STATED_MODEL", "M=2^20(27N+tau+1); failure<exp(-8tau)", lwe_scope),
    claim("C15", "NF complete search", "附录A.4 (A6)", "chi640 secret and error, original q", "M training samples", ["Support injection into mod32; deterministic support map/final training check"], ["C14"], ["E2"], "PROVED_UNDER_STATED_MODEL", "Search returns bottom on invalid/support/check failure", lwe_scope),
    claim("C16", "US complete search and conditioning", "附录A.4 (A6)", "Uniform or arbitrary original secret", "M+n+kappa independent samples", ["New original b/a after training; condition on fixed s/training/G; fresh mod2 rank; all new equations checked"], ["C14"], ["E2"], "PROVED_UNDER_STATED_MODEL", "Success>=1-delta-2^-kappa; G is unobservable and charged", lwe_scope),
    claim("C17", "Direct LWE decision", "附录A.4 (A7)", "Real vs uniform b rich-sample experiment", "M+t with fresh independent holdout", ["Original b no shift in validation; uniform branch conditioned only on its own training"], ["C14"], ["E2"], "PROVED_UNDER_STATED_MODEL", "Output1=realLWE; uniform accept<= (25/32)^t; train failure outputs0", lwe_scope),
    claim("C18", "General confidence and input-length cost", "附录A.2 (A2)、A.4 (A8)", "Fixed c27,d25 plus explicit raw D-bit input", "Arbitrary specified polynomial tau,t,kappa; full generic expression for larger parameters", ["Dense plan and explicit index bookkeeping"], ["C13"], ["E2"], "REPAIR_APPLIED", "M=Theta(N+tau); no unconditional n75 claim for all tau", lwe_scope),
    claim("C19", "Lambda-specialized resource/finite ledger", "附录A.4", "tau=t=kappa=lambda=n/8", "As n grows and finite n128,D56 example", ["Same confidence choice and cost model"], ["C18"], ["E2","E3"], "PROVED_UPPER_BOUND_AND_FINITE_CHECK", "n25/n75/n50 upper bounds; no practical timing or necessary cost lower bound", lwe_scope),
    claim("C20", "Rich exact LWE premise false", "§8.2、§9.2", "CF-1 exact chi640 NF and US", "All-PPT hardness allowing any polynomial fresh same-secret samples", ["Classical algorithms C15-C17; tau=t=kappa=lambda"], ["C15","C16","C17","C19"], ["E2","S4","S5"], "PROVED_UNDER_STATED_MODEL", "Also defeats corresponding QPT-hardness formulation containing classical algorithms", lwe_scope),
    claim("C21", "Fixed sample/Gaussian responsibilities", "§8.1、§9.2、A.6", "NF_n/US_3n, multi-secret views, wider Gaussian", "Exact sample, time and distribution budget", ["No supplied rich-sample simulator or matching hardness chain"], ["C20"], ["S2","S6","S7","S8","E2"], "UNRESOLVED", "No claim of security or universal impossibility of amplification", lwe_scope),
    claim("C22", "Named hybrid endpoint witness", "§9.1 (24)-(25)", "FI Hyb_i prime, Eq6/Lemma6.8", "Epoch1,b1; independent endpoints; horizon T", ["Random means independent uniform simulator output; real token endpoints; common abort kernel"], ["C03","C04"], ["S1","E3"], "PROVED_WITH_RECORDED_SEMANTICS", "Informed H1; not a separate refutation of preceding firewall scaling", "Inherited informed hybrid audit; original images bound"),
    claim("C23", "Conditional Theorem6.9 wording", "§1.3、§9.2", "H implies Sec_CF1", "Cases H_rich,H_fixed,widerGaussian", ["H_rich false; H_fixed truth/source reduction not certified"], ["C09","C20","C21","C22"], ["S1","S9","E2"], "CASE_SCOPED_CLAIM", "No certified nonempty-hardness-premise refutation", "Author-visible review consequence and current wording repair"),
    claim("C24", "Application priority", "§1.2、§10.3", "Same FI object and original-game attack", "Bounded historical search through2026-11-08", ["KLR/AG/CJL and generic algebra/probability tools acknowledged"], ["C03","C05","C09"], ["S3","E3"], "SEARCH_BOUNDED_APPLICATION_CANDIDATE", "Global first and new generic method not established", "Informed literature audit"),
    claim("C25", "Official correctness/actual implementation scope", "§7", "Official configs and author performance program", "Exact sampling/code/T/failure contract required", ["CDF event certificates do not certify accumulated decryption failure"], ["C10"], ["S1","S2","E3"], "UNRESOLVED_OUTSIDE_CERTIFIED_EVENT", "Code/config, seed law, maxT and full correctness certificate pending", "Source/parameter scope audit"),
    claim("C26", "Mainline connection", "§10.1-10.2", "ONLINE_TRUSTED_STATE_V1,M1-M6,G1-r01", "11 frozen reports, version/profile-limited historical observations", ["No mapping from service handle/audit public key to FI token or source hiding"], [], ["E4"], "INDEPENDENT_CRYPTOANALYSIS_POSITIONING", "No deployment break or native withdrawal conclusion; no new native operations", "Current informed business-evidence reconciliation"),
    claim("C27", "Review identity and source scope", "附录C", "UE two-stage flow, LWE author-visible flow and current integration", "Exact registered scopes, hashes and known identities only", ["Model/build separation unknown; no human/formal assistant review"], [], ["E1","E2","E3"], "VERIFIED_PROVENANCE_SCOPE", "CJL PDF/Nishimaki extended/author code gaps affect specified claims only", "Provenance disclosure"),
    claim("C28", "Counterexample to full-precision strengthening", "附录A.5 (A9)", "n1,q04,d2,s0,eUniform01,y=(1,2,2)", "All a inZ4 and e0/1", ["Formal coordinates, fixed y0=1"], ["C12"], ["E2"], "COUNTEREXAMPLE_TO_STRONGER_STATEMENT", "Partial mod2 theorem intact; further lifting algorithm not excluded", lwe_scope),
]
matrix = dict(schema="fi-research-manuscript/claim-evidence/1", date_asia_shanghai="2026-11-10",
              identity=identity, source_registry=sources, claims=claims,
              correction_ids=[f"R{i:02d}" for i in range(1,15)],
              manuscripts="CRYPTOANALYSIS_DRAFT.md; REVIEW_RESPONSE_AND_READINESS.md",
              core_proof_status="No registered open mathematical step inside explicit contracts; human cryptographic review pending",
              action_counts=actions, priority_search_cutoff="2026-11-08",
              new_metadata_check_date="2026-11-10")
writej(ROOT / "CLAIM_EVIDENCE_MATRIX.json", matrix)

qa = dict(json_errors=[], broken_local_links=[], forbidden_style=[],
          historical_input_files_verified=len(snap), review_files_verified=32,
          round005_review_records_verified=39, source_copies_verified=len(copies),
          mainline_reports_verified=len(mainline["files"]), citation_ids_missing=[],
          finite_checks_passed=True, corrections_missing=[])
draft = (ROOT / "CRYPTOANALYSIS_DRAFT.md").read_text(encoding="utf-8")
response = (ROOT / "REVIEW_RESPONSE_AND_READINESS.md").read_text(encoding="utf-8")
for i in range(1,15):
    if f"R{i:02d}" not in response:
        qa["corrections_missing"].append(f"R{i:02d}")
for name in ["CRYPTOANALYSIS_DRAFT.md", "REVIEW_RESPONSE_AND_READINESS.md"]:
    text = (ROOT / name).read_text(encoding="utf-8")
    if re.search("不是.{0,80}而是",text):qa["forbidden_style"].append(name)
    cleaned = re.sub(r"`[^`]*`", "", text)
    cleaned = re.sub(r"\\\[.*?\\\]", "", cleaned, flags=re.S)
    for target in re.findall(r"\]\(([^)]+)\)",cleaned):
        if not target.startswith(("https:","http:")) and not (ROOT/target).resolve().exists():
            qa["broken_local_links"].append(dict(file=name,target=target))
for source_id in re.findall(r"\[(S\d+|E\d+)\]",draft):
    if source_id not in sources:qa["citation_ids_missing"].append(source_id)
for p in list(ROOT.glob("*.json"))+list(EV.glob("*.json"))+list(SRC.glob("*.json")):
    if p.name=="MANIFEST.json":continue
    try:readj(p)
    except Exception as e:qa["json_errors"].append(dict(path=str(p),error=str(e)))
assert not any(qa[k] for k in ["json_errors","broken_local_links","forbidden_style","citation_ids_missing","corrections_missing"]),qa
assert all(pin(x["path"])["sha256"]==x["sha256"] for x in snap)
writej(EV / "DOCUMENT_QA.json",qa)
required=["CRYPTOANALYSIS_DRAFT.md","CLAIM_EVIDENCE_MATRIX.json","REVIEW_RESPONSE_AND_READINESS.md","MANIFEST.json"]
files=[pin(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
for x in files:x['path']=str(Path(x['path']).relative_to(ROOT))
manifest=dict(schema="fi-research-manuscript/manifest/1",date_asia_shanghai="2026-11-10",
              status="REPAIRS_CLOSED_RESEARCH_DRAFT_READY_FOR_HUMAN_CRYPTOGRAPHIC_REVIEW",
              root=str(ROOT),required_deliverables=required,identity=identity,
              historical_inputs_verified_unchanged=True,input_snapshot=pin(EV/'HISTORICAL_INPUT_SNAPSHOT.json'),
              review_manifest_byte_sha256=rev['manifest_byte_sha256'],
              review_manifest_payload_sha256=rev['canonical_payload_sha256'],
              mathematical_core="Under explicit printed algorithm/type-normalization/iid contracts; no registered open step; human review pending",
              source_and_external_limits=["CJL original/current PDF version identity","Nishimaki extended exact Lemma5.7","FI parameterized reduction/fixed LWE premise","Author code/seed/config and official UE correctness/maxT","Global application priority","Business-to-FI game mapping"],
              new_cost_presentation_repair="Equation20 counts the maximum fresh/update challenge chi samples; original final+mbar*n only counted update",
              action_counts=actions,qa=qa,files_exclude_manifest_itself=True,files=files,
              manifest_integrity_definition="SHA256 of UTF8 canonical JSON with manifest_integrity omitted; ensure_ascii=false,sort_keys=true,separators=(comma,colon). Payload checksum differs from file-byte hash.")
payload=json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
manifest['manifest_integrity']=dict(algorithm='sha256',canonical_payload_sha256=hashlib.sha256(payload).hexdigest())
writej(ROOT/'MANIFEST.json',manifest)
print(json.dumps(qa,ensure_ascii=False))
print('Claims:',len(claims),'manifested files:',len(files),'manifest byte SHA256:',pin(ROOT/'MANIFEST.json')['sha256'])
