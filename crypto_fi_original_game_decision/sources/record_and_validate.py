"""Source/manifest and finite-evidence bookkeeping only; no cryptographic implementation."""
from pathlib import Path
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"D:\毕业设计")
OUT = BASE / "crypto_fi_original_game_decision"
SRC = OUT / "sources"


def readj(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def pin(path):
    path = Path(path)
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def writej(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


primary_specs = [
    (SRC / "FI_v4_frozen.pdf", "E1_PRIMARY_PDF", "FI pp9-15 and18-20 original images; p8 text and targeted algorithms/game/parameter/theorem text. Full23page file obtained; reading targeted."),
    (SRC / "publisher_current.pdf", "E1_PUBLISHER_BYTE_MATCH", "Fresh publisher retrieval and exact comparison with v4. Image/text reading transferred only through identical bytes."),
    (SRC / "articlev08.tex", "E1_SOURCE_TEX", "Game L332-483; parameters L493-499; Frodo/UE algorithms, Ord/Tensor, correctness, Hyb_i/Eq6/Lemma6.8/Theorem6.9 and implementation paragraph."),
    (SRC / "KLR2019_ORBilu_frozen.pdf", "E1_PRIMARY_PDF_TARGETED", "71page file obtained; current original images/text PDF17 Def11,27 Def14,44 AppB.2 and adjacent paragraphs. Whole-paper coverage not asserted."),
    (BASE / "crypto_frodo_common_parameter_closure/sources/official_frodo_2021_frozen.pdf", "E1_PRIMARY_PDF_TARGETED", "Current section2.2/PDF14 text, PDF15 and25 original images; inherited exact sampler and convolution-section reading."),
    (BASE / "crypto_frodo_priority_audit/sources/frodo_2025_correct_url.pdf", "E1_PRIMARY_TABLE_IMAGE", "Current PDF16/printed12 TableA.4 image through historical render; remaining paper not reread this turn."),
    (BASE / "crypto_rtr_priority_decision/sources/HRA_PRE_CiC2025.pdf", "E1_PRIMARY_PDF_SCOPED", "Current text PDF7-8 Def7-8 and28-29 AppendixB; matching original-image record inherited from RtR audit."),
    (BASE / "crypto_rtr_priority_decision/sources/DDLM_Cloudflare.pdf", "E1_INHERITED_SCOPED_READING", "Inherited RtR scope Fig5/Def8, PDF16-17 and algorithms. Current attribution uses scoped record; no fresh full-paper reading."),
    (BASE / "crypto_rtr_priority_decision/sources/LM_NSF.pdf", "E1_INHERITED_SCOPED_READING", "Inherited RtR scope section4.1/PDF18 and section6/PDF26-27, including earlier images. Current comparison uses method attribution."),
    (BASE / "crypto_rtr_priority_decision/sources/Cohen_PKC2019_indexed_transcription.txt", "E2_PRIMARY_INDEXED_TRANSCRIPTION", "Current targeted persistent/ephemeral and Thm4 text; inherited Def7/Thm5 aux comparison. PDF bytes/images missing."),
]
primary = [dict(pin(p), evidence_grade=grade, read_scope=scope) for p, grade, scope in primary_specs]
target_hash = "bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4"
publisher_match = (SRC / "publisher_current.pdf").read_bytes() == (SRC / "FI_v4_frozen.pdf").read_bytes()
assert publisher_match and pin(SRC / "publisher_current.pdf")["sha256"] == target_hash

review = readj(SRC / "review_integrity_check.json")
assert all(r["all_match"] for r in review) and sum(r["checked"] for r in review) == 39
finite = readj(SRC / "finite_certificate_recheck.json")
assert all(r["two_term_bound_verified"] and r["file_sha256_match"] for r in finite["rows"])
restoration = readj(SRC / "historical_restoration_recheck.json")
assert len(restoration) == 5 and all(r["match"] for r in restoration)
historical = readj(SRC / "historical_source_lock.json")
for r in historical:
    assert pin(r["path"])["sha256"] == r["sha256"]

identity = {
    "status": "INFORMED_SOURCE_AND_CONTRIBUTION_AUDIT",
    "prior_attack_derivations_and_reviews_visible": True,
    "informed_prior_participation": True,
    "new_independent_reviews": 0, "new_subagents": 0,
    "human_peer_reviews_this_turn": 0, "formal_proof_assistant_used": False,
}
actions = {
    "protection_mechanism_implementations": 0,
    "cryptographic_attack_prototypes": 0,
    "large_parameter_crypto_experiments": 0,
    "author_contacts": 0, "emails": 0, "native_AS_RP_requests": 0,
    "finite_check_scope": "Hashes, scalar coefficient/probability certificates and integer parameter inequalities only",
}
record = {
    "schema": "fi-original-game-decision/source-and-reading/1",
    "date_asia_shanghai": "2026-11-08", "identity": identity,
    "skills": ["academic-research-suite: inline source verification and literature synthesis", "pdf: read-only preflight and original-image inspection"],
    "mathematical_baseline": "ROUND-005 reviewed THEOREM_FOR_CITATION.md; alpha*epsilon and p_k*epsilon joint bounds authoritative; earlier LWE-conditional statements historical",
    "primary_sources": primary,
    "publisher_attribution": {
        "url": "https://fi.episciences.org/17222",
        "download_url": "https://fi.episciences.org/17222/pdf",
        "fresh_download": pin(SRC / "publisher_current.pdf"),
        "frozen_v4_bytes_equal": publisher_match,
        "publisher_online_date": "2026-01-11", "accepted_date": "2025-08-08",
        "submitted_date": "2024-10-10", "printed_PDF_year": 2025,
        "v4_date": "2025-12-29", "accepted_day_manuscript_byte_identity_claimed": False,
    },
    "source_archive": {
        "url": "https://arxiv.org/src/2410.03948v4", "file": pin(SRC / "FI_v4_source.tar"),
        "members": ["00_my_def.tex", "00README.json", "articlev08.bbl", "articlev08.tex", "fundam.bst", "fundam.cls"],
        "author_benchmark_code_members": 0,
    },
    "review_integrity": review,
    "review_identity_scope": "One two-stage AI review: phase1 source-only/no author derivation history; phase2 same reviewer informed comparison. N1 and H1 keep inherited informed provenance. Current audit is informed.",
    "finite_checks": finite, "historical_source_locks": historical,
    "historical_restoration": {"incident_historical": True, "rechecked_files": restoration, "historical_files_written_this_turn": 0},
    "incremental_search": {
        "receipts": ["web_search_1.json", "web_search_2.json", "web_search_3.json", "web_search_4.json", "openalex_doi.json", "crossref_doi.json"],
        "basis": "Publisher DOI links, current arXiv ID/version table, newly queried Crossref/OpenAlex DOI endpoints, exact title/ID/DOI and object-specific attack/correction/code search combinations",
        "older_receipts": ["crypto_frodo_priority_audit/sources/Q1.json..Q22.json", "crypto_frodo_unconditional_support/sources/P1.json..P6.json"],
        "same_object_public_attack_located": False, "global_first_established": False,
        "openalex_cited_by_count": readj(SRC / "openalex_doi.json").get("cited_by_count"),
        "crossref_citation_count": readj(SRC / "crossref_doi.json")["message"].get("is-referenced-by-count"),
        "zero_index_counts_are_not_exhaustiveness_evidence": True,
        "Nishimaki_blocked_endpoints_retried": 0,
    },
    "unresolved": {
        "author_program": ["code/commit", "D/B/CDF/T", "secret-noise seed joint law, domain separation and reuse", "filters/retries, modular encoding/overflow and failure semantics"],
        "official_configuration_correctness": ["joint accumulated residual law per depth", "full-coordinate failure bound", "maximum T and failure budget"],
        "Nishimaki2024": "Exact extended section5/Lemma5.7, formula images and conference-version mapping; affects predecessor inheritance/priority, not direct FI theorem dependencies",
        "Cohen": "Original PDF bytes/images and early preprint correspondence; complete primary indexed text exists",
    },
    "mainline": {"contract": "ONLINE_TRUSTED_STATE_V1", "reading_scope": "Contract projection fields only", "business_to_FI_game_mapping_present": False},
    "action_counts": actions,
    "local_source_inventory": [pin(p) for p in sorted(SRC.iterdir()) if p.is_file() and p.name not in ("SOURCE_AND_READING_RECORD.json", "DELIVERY_VALIDATION.json")],
}
writej(SRC / "SOURCE_AND_READING_RECORD.json", record)

findings = [
    ("V1", "VERIFIED", "Current publisher/v4 byte identity and exact object", "PUBLISHED_TARGET_AND_GAME.md sections1-2", "Accepted-day manuscript byte identity unclaimed"),
    ("V2", "VERIFIED", "Four-query original-game witness and <=3k+1 adaptive permissions", "PUBLISHED_TARGET_AND_GAME.md sections3-4", "Empty K* makes final C* intersection empty for every source closure"),
    ("V3", "VERIFIED", "Affine-support algebra and fixed-A real-fresh bound", "FINAL_THEOREM_AND_CONTRIBUTION.md sections1-2; review_integrity_check.json", "Independent sampling and P2-only stopping explicit; N1 identity separately inherited"),
    ("V4", "VERIFIED", "CF-1 in printed domain: common pointwise correctness and PPT near-maximal gap", "PARAMETER_SCOPE_AND_CORRECTNESS.md sections1-4", "Strict official D<=16 is extended-model interpretation; exact LWE hardness premise not certified"),
    ("V5", "VERIFIED", "Three official finite-distribution game-event certificates", "sources/finite_certificate_recheck.json", "Exponent n; complete UE correctness/maxT separate"),
    ("V6", "NEEDS_CLARIFICATION", "Official configurations complete UE correctness and maximum update budget", "PARAMETER_SCOPE_AND_CORRECTNESS.md section5", "Actual joint residual probabilities per depth, coordinate failure union and T/failure budget needed"),
    ("V7", "SOURCE_UNRESOLVED", "Author performance implementation equivalence", "PARAMETER_SCOPE_AND_CORRECTNESS.md section6", "Program/config and secret-noise seed law missing"),
    ("V8", "VERIFIED", "Specific-object application value within checked literature; mature tools acknowledged", "APPLICATION_PRIORITY_AUDIT.md", "Global first remains bounded-search priority question"),
    ("V9", "SOURCE_UNRESOLVED", "Exact predecessor Lemma5.7 and full priority closure", "APPLICATION_PRIORITY_AUDIT.md section5", "Nishimaki2024 exact full text/images; not a direct FI theorem dependency"),
    ("V10", "COUNTEREXAMPLE", "Named FI hybrid uniformization endpoint has non-negligible event gap under recorded semantics", "APPLICATION_PRIORITY_AUDIT.md section4; PDF18-19 Eq6/Lemma6.8", "Independent-uniform random output context, independent endpoints and shared abort kernel explicit; informed H1"),
]
verdict = {
    "schema": "fi-original-game-decision/verdict/1", "date_asia_shanghai": "2026-11-08",
    "overall_category": "可认证的具体方案原游戏密码分析",
    "scope": "Current journal/arXiv v4 printed formulas with explicit Ord column-count type normalization; ideal independent finite-chi sampling. Author benchmark equivalence unclaimed.",
    "identity": identity, "mathematics_version": "ROUND-005 post-review citation theorem",
    "target": {"doi": "10.46298/fi.14425", "arxiv": "2410.03948v4", "pdf_sha256": target_hash, "publisher_bytes_equal": True, "security_theorem": "Theorem6.9 PDF20", "game": "rand-ind-eu-cpa backward-leak uni-directional PDF9-11"},
    "findings": [dict(id=i, status=t, claim=c, evidence=e, remaining=r) for i, t, c, e, r in findings],
    "probabilities": {
        "one_shot_signed_gap": "alpha-beta >= alpha(1-epsilon_n)",
        "adaptive_signed_gap": "p_k-beta_selected >= p_k(1-epsilon_n)",
        "paper_advantage": "absolute signed gap", "success": "(1+Delta)/2", "bias": "Delta/2",
        "CF1": "Delta_n >= [1-(1-p_n)^n](1-epsilon_n) >= 1-(3/4)^n-epsilon_n = 1-negl(lambda)",
        "finite_gaps": {"640": "p_640*(1-2^-751)", "976": "p_976*(1-2^-1118)", "1344": "L_1344*(1-2^-1532)"},
    },
    "CF1": {"lambda": "integer>=2", "n": "8lambda", "D": "8ceil(log2n)", "q": "2^D", "chi": "exact independent chi640", "mbar": 8, "nbar": 8, "B": 2, "Next_transitions_max": "n", "epochs": "n+1", "single_chain_updates_max": "n", "queries": "<=3n+1", "correctness": "B0+nW<q/8 pointwise", "attack_hardness_assumptions": 0, "exact_family_LWE_hardness_verified": False},
    "contribution": {"thesis_level": "独立密码分析核心候选", "central_value": "Specific published UE source-hiding failure, original game, fixed-A direct bound, finite certificates and common correct family", "new_generic_method_claimed": False, "same_object_prior_found": False, "global_first_established": False, "author_benchmark_broken_established": False, "human_domain_review_pending": True, "mainline_business_mapping": "Separate evidence required; default independent cryptanalysis positioning", "RtR": "B archive retained"},
    "minimum_decision_changing_evidence": ["Dated same-FI-object original-game public attack", "Formal formula/game/parameter-domain correction", "Author UE commit/config/noise flow and finite correctness certificate", "Concrete counterexample under frozen theorem hypotheses", "Nishimaki2024 exact Lemma5.7 for predecessor attribution"],
    "protection_implementation_separation_gate_satisfied": False, "action_counts": actions,
    "deliverables": ["PUBLISHED_TARGET_AND_GAME.md", "PARAMETER_SCOPE_AND_CORRECTNESS.md", "APPLICATION_PRIORITY_AUDIT.md", "FINAL_THEOREM_AND_CONTRIBUTION.md", "VERDICT.json"],
}
writej(OUT / "VERDICT.json", verdict)

# Final artifacts: source locks, parseable JSON, local Markdown targets, style and byte manifests.
validation = {"historical_locks_unchanged": True, "review_records_verified": 39,
              "publisher_bytes_match": publisher_match, "finite_certificates_verified": 3,
              "json_parse_errors": [], "broken_local_links": [], "forbidden_style_hits": [], "deliverables": []}
for name in verdict["deliverables"]:
    p = OUT / name
    validation["deliverables"].append(pin(p))
    if p.suffix == ".json":
        readj(p)
    else:
        text = p.read_text(encoding="utf-8")
        if re.search("不是.{0,80}而是", text):
            validation["forbidden_style_hits"].append(name)
        link_text = re.sub(r"`[^`]*`", "", text)
        link_text = re.sub(r"\\\[.*?\\\]", "", link_text, flags=re.S)
        for target in re.findall(r"\]\(([^)]+)\)", link_text):
            if target.startswith(("http:", "https:")):
                continue
            dest = (p.parent / target).resolve()
            if not dest.exists():
                validation["broken_local_links"].append({"file": name, "target": target})
for p in SRC.glob("*.json"):
    try:
        readj(p)
    except Exception as e:
        validation["json_parse_errors"].append({"path": str(p), "error": str(e)})
writej(SRC / "DELIVERY_VALIDATION.json", validation)
print(json.dumps({k: v for k, v in validation.items() if k != "deliverables"}, ensure_ascii=False))
print("Five deliverables and source-reading record sealed.")
