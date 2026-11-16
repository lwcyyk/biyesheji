"""Document-only R20 review: no application imports, tests, database or OS probes."""
import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(r"D:\毕业设计")
PROJECT = ROOT / "auth-lifecycle"
BASE = ROOT / "research_g2_dsat_implementation"
OUT = BASE / "2026-11-11_r20"
R19 = BASE / "2026-11-11_r19"
PY_ROOT = Path(r"C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python")


def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


checks = []


def check(label, value, detail=None):
    checks.append({"label": label, "satisfied": bool(value), "detail": detail})


pre = load(OUT / "sources/PRECHECK_LOCK.json")
mismatches = [x["path"] for x in pre["files"] if sha(Path(x["path"])) != x["sha256"]]
check("PROTECTED_1133_FILES_UNCHANGED", len(pre["files"]) == 1133 and not mismatches, mismatches)
check("NO_CURRENT_EXISTING_SOURCE_EDIT_PERMISSION", pre["allowed_existing_edits"] == [])
inherited = load(OUT / "sources/R19_INHERITED_RECORD_REVIEW.json")
check("R19_RECORDED_68_PASS_2056_CHECKS_REUSED", inherited["counts"] == {"PASS": 68, "FAIL": 0, "ERROR": 0, "SKIP": 0} and inherited["checks"] == 2056 and inherited["all_assertion_records_satisfied"])

stdlib = []
for name, start, end, purpose in [("Lib/socketserver.py", 247, 255, "shutdown requires serve_forever in another thread"),
    ("Lib/socketserver.py", 678, 712, "request threading mixin"),
    ("Lib/http/server.py", 146, 147, "ThreadingHTTPServer is daemon threading mixin")]:
    p = PY_ROOT / name
    lines = p.read_text(encoding="utf-8").splitlines()
    stdlib.append({"path": str(p), "sha256": sha(p), "read_scope": "static text only", "line": start,
                   "through": end, "purpose": purpose, "excerpt": lines[start-1:end]})
findings = [
    {"id": "SF1", "source": "services.py", "line": 22, "finding": "SingleActive used only by Controller, not Authority", "kind": "STATIC_FACT"},
    {"id": "SF2", "source": "storage.py", "line": 60, "finding": "connection acquired before fallible SQL/log/marker/config; no constructor exception cleanup", "kind": "STATIC_CONDITIONAL_FAILURE"},
    {"id": "SF3", "source": "services.py", "line": 374, "finding": "cleanup finally covers only serve_forever, excludes earlier acquisition failures", "kind": "STATIC_CONDITIONAL_FAILURE"},
    {"id": "SF4", "source": "dsat_authority_runtime.py", "line": 340, "finding": "offline close_owned shutdown call needs different live semantics to avoid same-thread/no-loop wait", "kind": "PAPER_FAILURE_IF_LIVE_GATE_OPENED"},
    {"id": "SF5", "source": "dsat_authority_host_activation.py", "line": 289, "finding": "namespace scoped to process and connection object; lifecycle singleton/epoch rejection needed", "kind": "MODEL_PRECONDITION"},
    {"id": "SF6", "source": "run_h2_authority_service.py", "line": 17, "finding": "only offline parser exists; future six ops not executable", "kind": "STATIC_FACT"},
]
write("sources/SUPPLEMENTAL_STATIC_REVIEW.json", {"schema": "r20-static-evidence/1", "stdlib": stdlib,
    "findings": findings, "failure_injections_executed": 0, "native_Win32_calls_executed": 0,
    "future_Win32_api_prototypes": "proposed platform interfaces; B1 validation pending, no current runtime verification"})

reports = ["01_SCOPE_AND_R19_SOURCE_LOCK.md", "02_LIVE_HOST_AND_INSTANCE_IDENTITY.md", "03_INITIALIZATION_AND_RESOURCE_BUDGET.md",
    "04_LIFECYCLE_AND_FAILURE_CLEANUP.md", "05_D1B_IMPLEMENTATION_AND_TEST_PLAN.md", "06_FINAL_VERDICT_AND_AUTHORIZATION_REQUEST.md"]
structured = ["D1B_SOURCE_AND_FILE_LOCK.json", "D1B_INSTANCE_IDENTITY_CONTRACT.json", "D1B_RESOURCE_BUDGET.json",
    "D1B_LIFECYCLE_STATE_MACHINE.json", "D1B_FAILURE_AND_CLEANUP_MATRIX.json", "D1B_TEST_PLAN.json", "D1B_COMMAND_LOCK.json", "D1B_AUTHORIZATION_REQUEST.json"]
check("ALL_SIX_REPORTS_PRESENT", all((OUT / x).is_file() for x in reports))
check("ALL_STRUCTURED_CONTRACTS_PRESENT", all((OUT / x).is_file() for x in structured))
verdict = (OUT / reports[-1]).read_text(encoding="utf-8")
check("ALL_15_QUESTIONS_ANSWERED", all(re.search(r"\| Q" + str(i) + r"\b", verdict) for i in range(1, 16)))
file_lock = load(OUT / "D1B_SOURCE_AND_FILE_LOCK.json")
check("NINE_TARGETS_THREE_EXISTING_FIVE_NEW_AND_TREE", len(file_lock["targets"]) == 9 and file_lock["existing_modifications_proposed"] == 3 and file_lock["new_python_proposed"] == 5 and file_lock["new_fixture_trees_proposed"] == 1)
check("TARGETS_REMAIN_UNEDITED_AND_UNCREATED", all((sha(Path(x["path"])) == x["before_sha256"]) if x["before_sha256"] else not Path(x["path"]).exists() for x in file_lock["targets"]))
check("NO_EDIT_AUTHORIZATION_IN_FILE_LOCK", all(x["current_edit_authorized"] is False and x["actual_edit"] is False for x in file_lock["targets"]))
matrix = load(OUT / "D1B_FAILURE_AND_CLEANUP_MATRIX.json")
check("ALL_28_FAILURES_NOT_RUN", matrix["count"] == 28 and [x["id"] for x in matrix["rows"]] == ["F%02d" % i for i in range(1,29)] and all(x["status"] == "NOT_RUN" for x in matrix["rows"]))
fields = ["initial_phase", "injection_point", "created_resources", "committed_state", "cleanup_owner", "preserve", "deletable", "idempotent_recovery", "safety_postcondition", "future_test_id"]
check("FAILURE_MATRIX_ALL_RESPONSIBILITIES", all(all(x.get(k) for k in fields) for x in matrix["rows"]))
test_plan = load(OUT / "D1B_TEST_PLAN.json")
check("NEW_52_PLANNED_WITH_DISTINCT_IDS", len(test_plan["B1_new_cases"]) == len(set(x["id"] for x in test_plan["B1_new_cases"])) == 52)
check("PLANNED_120_ALL_NOT_RUN", test_plan["B1_planned_total"] == 52 + 24 + 44 and all(x["status"] == "NOT_RUN" for x in test_plan["B1_new_cases"]))
check("B2_12_ALL_NOT_RUN", len(test_plan["B2_cases"]) == 12 and all(x["status"] == "NOT_RUN" for x in test_plan["B2_cases"]))
command = load(OUT / "D1B_COMMAND_LOCK.json")
check("SIX_OPERATIONS_NO_EXECUTABLE_ARGV", set(command["operations"]) == {"prepare","initialize","start","status","stop","recover"} and all(x["actual_argv"] is None and x["command_executable"] is x["AUTHORIZED"] is x["EXECUTED"] is False and x["blocker"] == "ENTRYPOINT_NOT_IMPLEMENTED" for x in command["operations"].values()))
check("FIRST_B2_RECOVERY_NOT_INCLUDED", command["operations"]["recover"]["max_successful_attempts_first_B2"] == 0)
budget = load(OUT / "D1B_RESOURCE_BUDGET.json")
check("SQL15_PLUS7_EQUALS22_AND_ROLLBACK_CAP23", len(budget["SQLite"]["initialization_normal_SQL"]) == 15 and len(budget["SQLite"]["strict_Store_normal_SQL"]) == 7 and budget["SQLite"]["normal_total_SQL"] == 22 and budget["SQLite"]["all_path_wrapper_SQL_attempts_max"] == 23)
check("DIRECTORY_FILE_CAP_ARITHMETIC", len(budget["directory_paths_under_root"]) == budget["directories_max"] == 14 and len(budget["fixed_persistent_files"]) == budget["fixed_files_max"] == 26 and budget["maximum_path_count"] == 26+64+3+3)
check("REAL_COSTS_NOT_MEASURED", all(x["actual"] == "NOT_MEASURED" and x["B1"] == x["B2"] == "NOT_RUN" for x in budget["costs"].values()))
check("DEFAULT_P2_ZERO_RECOVERY_NARROW", budget["host"]["protected_reads"] == budget["host"]["permits"] == budget["SQLite"]["world_read_state"] == budget["SQLite"]["world_plaintext_decrypt"] == 0)
states = load(OUT / "D1B_LIFECYCLE_STATE_MACHINE.json")
check("ALL_LIFECYCLE_STATES_SPECIFIED", {x["state"] for x in states["state_rows"]} == {"NEW","PREFLIGHTED","RESOURCES_RESERVED","INITIALIZING","SEED_READY","STORE_READY","HOST_DORMANT","LISTENER_READY","SERVICE_READY","STOPPING","STOPPED","FAILED","RECOVERY_REQUIRED"})
check("NORMAL_EDGES_COMPLETE", len(states["normal_edges"]) == 10 and states["normal_edges"][0] == ["NEW","PREFLIGHTED"] and states["normal_edges"][-1] == ["STOPPING","STOPPED"])
auth = load(OUT / "D1B_AUTHORIZATION_REQUEST.json")
check("B1_AND_B2_APPROVALS_CLOSED", auth["AUTHORIZED"] is auth["EXECUTED"] is auth["B1"]["approved"] is auth["B2"]["approved"] is False)
check("LIVE_VALUES_UNINFERRED", all(load(OUT / "D1B_INSTANCE_IDENTITY_CONTRACT.json")[k] is None for k in ["actual_SID","actual_PID","actual_process_creation_FILETIME","actual_process_epoch"]))
check("DEPLOYMENT_ROOT_ABSENT_METADATA_ONLY", not (ROOT / "h2_test_runtime/h2-authority-synth-001").exists())
check("FUTURE_TEST_OUTPUT_ROOT_ABSENT", not Path(test_plan["B1_output_root"]).exists())

statuses = ["D1A_IMPLEMENTED", "D1A_SYNTHETIC_TESTS_PASSED", "D1B_IDENTITY_CONTRACT_READY", "D1B_INITIALIZATION_BUDGET_READY", "D1B_FAILURE_CLEANUP_SPEC_READY", "D1B_COMMAND_SPEC_READY", "D1B1_READY_FOR_IMPLEMENTATION_REVIEW", "D1B1_AUTHORIZATION_PENDING", "D1B2_NOT_AUTHORIZED", "P1A_NOT_AUTHORIZED", "P1B_NOT_AUTHORIZED", "P2_NOT_AUTHORIZED", "S3B2_NOT_AUTHORIZED", "S5_NOT_AUTHORIZED", "SOURCE_OR_REFINEMENT_GAP", "TYPED_O_NOT_IMPLEMENTED", "O_REVISION_NOT_IMPLEMENTED", "ANALYSIS_ONLY"]
write("FINAL_STATUS.json", {"schema":"r20-final-status/1","statuses":statuses,"ready_meaning":"specification only; no code/testing/deployment qualification inferred",
    "project_source_edits":0,"project_tests_executed":0,"native_OS_identity_queries":0,"file_SQLite_connections":0,"real_service_key_material_generated_or_read":0,"real_services_started_stopped_restarted":0,"socket_calls":0,"real_P1_P2_calls":0,
    "inherited_R19_cases":68,"inherited_R19_checks":2056,"planned_B1_cases":120,"planned_B2_cases":12,
    "DEPLOYMENT_PREPARED":"OFFLINE_ONLY_INHERITED_R19","INSTANCE_RUNNING":False,"actual_argv":None,"command_executable":False,
    "unique_next_action":"D1B1_NINE_TARGET_CODE_AND_SCOPED_OFFLINE_FAULT_TEST_AUTHORIZATION"})

source_lock = {"schema":"r20-source-lock/1","date_china":"2026-11-11","request":next(x for x in pre["files"] if 'adec8766-64e5-42cd-ba03-e437268dfb44' in x["path"]),
    "R19_final_source_lock":{"path":str(R19/'SOURCE_LOCK.json'),"sha256":sha(R19/'SOURCE_LOCK.json')},
    "confirmed_parameters":{"path":str(BASE/'2026-11-11_r18_parameter_confirmation/H2_ENVIRONMENT_CONFIG_CONFIRMED.json'),"sha256":sha(BASE/'2026-11-11_r18_parameter_confirmation/H2_ENVIRONMENT_CONFIG_CONFIRMED.json')},
    "inherited_protection_rows":1441,"protected_unique_files":len(pre["files"]),"protected_precheck":"sources/PRECHECK_LOCK.json","protected_precheck_sha256":sha(OUT/'sources/PRECHECK_LOCK.json'),
    "historical_mismatches":mismatches,"source_review_locations":"sources/SOURCE_LOCATIONS.json","supplemental_static_review":"sources/SUPPLEMENTAL_STATIC_REVIEW.json",
    "current_existing_source_edits":[],"project_modules_imported":False,"project_tests_run":0,"deployment_actions":0,
    "evidence_provenance":"informed model-assisted static review and paper contract; external independent validation pending",
    "future_code_targets":"D1B_SOURCE_AND_FILE_LOCK.json","future_authorization_request":"D1B_AUTHORIZATION_REQUEST.json",
    "reports":[{"path":str(OUT/x),"sha256":sha(OUT/x)} for x in reports],
    "structured_contracts":[{"path":str(OUT/x),"sha256":sha(OUT/x)} for x in structured],
    "self_hash_policy":"SOURCE_LOCK listed in final DELIVERY_QA manifest; QA excludes itself"}
write("SOURCE_LOCK.json",source_lock)

canary_inputs = [PROJECT/'tests/fixtures'/x/'CANARIES.json' for x in ['dsat_authority_runtime','dsat_authority_host_activation','dsat_authority_read_host']]
values = set(v for p in canary_inputs for v in load(p)["values"].values())
needles = [needle for v in values for needle in [v.encode('utf-8'),json.dumps(v,ensure_ascii=True)[1:-1].encode('ascii')]]
files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'DELIVERY_QA.json')
hits=[];parse_errors=[];style_errors=[]
for p in files:
    raw=p.read_bytes()
    if any(v in raw for v in needles):hits.append(str(p))
    if p.suffix=='.json':
        try:load(p)
        except Exception:parse_errors.append(str(p))
    if p.suffix=='.md' and '不是' in raw.decode('utf-8-sig'):style_errors.append(str(p))
check("PUBLIC_CANARY_SCAN_CLEAN",not hits,hits)
check("ALL_JSON_VALID",not parse_errors,parse_errors)
check("PROSE_STYLE_BOUNDARY",not style_errors,style_errors)
check("FINAL_PROTECTED_RECHECK",all(sha(Path(x['path']))==x['sha256'] for x in pre['files']))
review={"schema":"r20-document-delivery-qa/1","reviewed_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "kind":"DOCUMENT_AND_INTEGRITY_REVIEW_ONLY","passed":all(x['satisfied'] for x in checks),"checks":checks,
    "project_tests_executed":0,"new_failure_injections":0,"new_service_runtime_probes":0,
    "files":[{"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size} for p in files],
    "canary_scan":{"status":"CLEAN" if not hits else 'FAIL',"input_hashes":[{"path":str(p),"sha256":sha(p)} for p in canary_inputs],"unique_values":len(values)},
    "actual_open_blockers":["B1 independent authorization","future Win32 implementation/prototype/platform tests","actual SID/source/config and supported argv after B1","independent B2/P1/P2 approvals"],
    "self_excluded":True}
write('sources/DELIVERY_QA.json',review)
print(json.dumps({'document_review_passed':review['passed'],'review_items':len(checks),'protected_unique_files':len(pre['files']),'new_delivery_files':len(files),'source_edits':0,'project_tests_executed':0,'failed':[x['label'] for x in checks if not x['satisfied']]}))
raise SystemExit(0 if review['passed'] else 1)
