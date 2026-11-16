"""R20 documentation assembly only: JSON/Markdown, hashes, AST. No app imports."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(r"D:\毕业设计")
PROJECT = ROOT / "auth-lifecycle"
BASE = ROOT / "research_g2_dsat_implementation"
OUT = BASE / "2026-11-11_r20"
R19 = BASE / "2026-11-11_r19"
DEPLOY = ROOT / "h2_test_runtime/h2-authority-synth-001"
PYTHON = r"C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
CONFIRMED = BASE / "2026-11-11_r18_parameter_confirmation/H2_ENVIRONMENT_CONFIG_CONFIRMED.json"
B1_OUTPUT = BASE / "2026-11-11_r21_d1b1_offline"
B2_EVIDENCE = BASE / "2026-11-11_r22_d1b2"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def put(name, value):
    p = OUT / name
    data = value.strip() + "\n" if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    p.write_text(data, encoding="utf-8")


pre = load(OUT / "sources/PRECHECK_LOCK.json")
assert not pre["mismatches"]
assert all(sha(Path(x["path"])) == x["sha256"] for x in pre["files"])
loc = load(OUT / "sources/SOURCE_LOCATIONS.json")
positions = {Path(x["path"]).name: {s["name"]: s["line"] for s in x["symbols"]} for x in loc["files"]}

tasks = [
    ("services.py", "src/auth_lifecycle/online_state/services.py", "MODIFY_PROPOSED", ["serve live-context dispatch", "bounded_authority_listener factory"],
     "保留原default/offline分支；为经过接纳的独立LiveContext提供单Store、延迟bind的同步TLS listener工厂；原Controller/Provider行为保留", ["F15", "F16", "F17", "F18", "T36", "T48", "T52"]),
    ("storage.py", "src/auth_lifecycle/online_state/storage.py", "MODIFY_PROPOSED", ["AuthorityStore.__init__(..., bootstrap_context=None)"],
     "可选严格Schema2预置模式、连接创建后立即登记拥有者、构造异常关闭连接、有界telemetry；原参数默认语义保持；业务mutator/read_state/migration文件保留", ["F07", "F08", "F09", "F15", "T34", "T35", "T48"]),
    ("launcher", "scripts/run_h2_authority_service.py", "MODIFY_PROPOSED", ["strict operation parser", "offline plan compatibility", "preflight before production imports"],
     "保留R19离线接口；新增尚未实现的六操作语义和内部owned-child入口；分开部署批准与P2许可；参数仅路径/非秘密ID", ["T29", "T30", "T49", "T50", "T52"]),
    ("live admission", "src/auth_lifecycle/online_state/dsat_authority_live.py", "NEW_PROPOSED", ["LiveDeploymentIssuer", "LiveAuthorityContext", "validate_live_entry", "bind_dormant_store"],
     "可信bootstrap接纳、source/OS/epoch/DB绑定；仅发行部署能力，P2 API固定拒绝；进程内唯一context/store", ["F26", "F27", "F28", "T31", "T38", "T45", "T46", "T47"]),
    ("lifecycle", "src/auth_lifecycle/online_state/dsat_authority_lifecycle.py", "NEW_PROPOSED", ["OwnedResources", "prepare", "initialize_fresh_seed", "start_owned", "status_record", "stop_owned", "recover_classify"],
     "完整资源栈/阶段账本、15条初始化SQL、单Store启动、同步轮询服务、限制恢复及幂等清理；新库为合成数据", ["F01-F28", "T33", "T37", "T40", "T42", "T43", "T44"]),
    ("Windows host provider", "src/auth_lifecycle/online_state/dsat_windows_runtime.py", "NEW_PROPOSED", ["self_process_facts", "verify_target_handle", "open_owned_file", "reserve_instance", "launch_owned_child", "signal_owned_stop"],
     "惰性ctypes Win32适配：Token SID/创建时点/image、文件ID/最终路径/DACL、独占非继承锁及显式子进程句柄传递、命名Event；无系统扫描/现有实例查询", ["F02", "F05", "F24", "F25", "T32", "T39", "T41", "T50"]),
    ("new tests", "tests/test_dsat_authority_live_lifecycle.py", "NEW_PROPOSED", ["F01-F28 fault cases", "T29-T52 contract cases"],
     "52个新离线测试；纯替身、公开向量文件SQLite与限定合成子进程；live网络为拒绝钩子", ["F01-F28", "T29-T52"]),
    ("new runner", "scripts/run_dsat_authority_live_lifecycle_tests.py", "NEW_PROPOSED", ["suite=new52", "suite=r19_24", "suite=legacy44"],
     "分域runner与新版本差异映射；加载旧测试类而不改旧runner/锁；只写专用输出树", ["T48", "T49", "T50", "T51", "T52"]),
    ("new fixtures", "tests/fixtures/dsat_authority_live_lifecycle", "NEW_SUBTREE_PROPOSED", ["frozen scenario/schema/ownership/canary/public-vector inputs"],
     "本轮未来测试合同的合成输入；原R19夹具和哨兵保持；包含旧epoch/clone/partial-init反例", ["F01-F28", "T29-T52"]),
]
file_rows = []
for key, rel, action, functions, purpose, tests in tasks:
    p = PROJECT / rel
    file_rows.append({"id": key, "path": str(p), "action": action, "exists_now": p.exists(),
        "before_sha256": sha(p) if p.is_file() else None, "proposed_symbols_not_implemented": functions,
        "purpose": purpose, "offline_test_ids": tests, "current_edit_authorized": False,
        "future_D1B1_approval_required": True, "actual_edit": False})
put("D1B_SOURCE_AND_FILE_LOCK.json", {"schema": "r20-proposed-file-lock/1", "status": "PROPOSAL_ONLY",
    "existing_modifications_proposed": 3, "new_python_proposed": 5, "new_fixture_trees_proposed": 1,
    "targets": file_rows, "allow_other_existing_edits": False,
    "preserve": ["dsat_authority_runtime.py R19 offline semantics", "dsat_authority_host_activation.py R16", "dsat_authority_read_host.py", "protocol.py", "materials.py", "all old tests/runners/fixtures/locks", "all migration files", "business methods of AuthorityStore"],
    "source_snapshots_required_before_future_edit": True, "historical_locks_remain_immutable": True})

gaps = [
    ("G01", "运行接纳", "RuntimeContext只发行offline上下文，validate_service_entry恒拒绝", "LiveDeploymentIssuer和核验后的LiveAuthorityContext；部署权限不含P2", "runtime RuntimeConfig/规范化可复用；原offline context保持", ["live admission", "lifecycle", "launcher"]),
    ("G02", "真实OS provider", "OFFLINE_PATH_PROVIDER/合成process字段", "self/owned-child句柄上的SID、FILETIME、image、最终路径/文件ID/DACL", "windows_isolation.py仅借鉴惰性Win32/关闭句柄方法，不调用restricted launcher", ["Windows host provider"]),
    ("G03", "单活", "SingleActive仅Controller使用", "Authority的独占lock文件handle贯穿prepare/init/start；子进程显式传同一handle", "SingleActive为现有比较来源；SQLite WAL写锁不代表单活", ["Windows host provider", "lifecycle"]),
    ("G04", "源码运行绑定", "SOURCE_BASIS固定R18历史摘要；合成source digest可输入", "批准后完整artifact清单、固定执行入口、模块origin与加载前后文件摘要；可信OS条件", "canonical/digest/版本字符串", ["lifecycle", "live admission", "launcher"]),
    ("G05", "初始化", "公开AES向量和内存Schema2", "新测试state key、独立TLS key、全新文件SQLite两表/三行/合成receipt", "R19 seed结构、现有AAD、Schema2列定义", ["lifecycle", "storage.py"]),
    ("G06", "构造异常", "Store connect后可能在execute/metrics/marker/config失败，调用方尚无对象", "optional bootstrap_context即时捕获连接；构造异常关闭；严格2版防自动migration", "原ctor/schema/execute默认路径", ["storage.py", "lifecycle"]),
    ("G07", "监听前清理", "services的finally只覆盖serve_forever", "所有获取点先登记拥有者；Store到TLS/ready都在同一资源包络", "Handler认证和TLS常规工具", ["services.py", "lifecycle"]),
    ("G08", "关闭死锁与线程", "RuntimeContext.close_owned无条件shutdown；ThreadingHTTPServer无请求线程上限", "live同步轮询loop；无serve_forever/shutdown互等；有限连接和timeout", "标准库socketserver shutdown docstring与HTTPServer", ["services.py", "lifecycle"]),
    ("G09", "会话重启", "R16槽为process-local/connection对象namespace", "单Store/单连接、每启动新epoch、旧P2 envelope失效；本阶段P2总额0", "R16核心保持、未来P2独立接纳", ["live admission", "lifecycle"]),
    ("G10", "RPC与默认权限", "旧lab.initialize建三角色及controller业务权限", "Authority-only、identities/permissions均为空；拒绝请求止于Store之前；stop走OS控制Event", "常规Bearer检查和权限拒绝顺序", ["services.py", "lifecycle"]),
    ("G11", "停止/恢复入口", "现脚本只有offline计划，旧lab.stop直接kill", "固定owned handle+epoch的graceful stop；recover仅分类，无自动重启/修复/解密", "固定JSON/最小记录合同", ["launcher", "lifecycle", "Windows host provider"]),
    ("G12", "P1限制", "P1a合成文件provider；P1b静态", "本轮继续延期；部署只发布自身有限receipt；独立P1仍须另批", "现inspect脚本和P1B静态合同保持", [])]
put("D1A_TO_D1B_GAP_MATRIX.json", {"schema": "r20-gap-matrix/1", "rows": [
    {"id": gid, "topic": topic, "offline_completed": before, "live_required": after, "reuse": reuse,
     "proposed_file_ids": files, "side_effects": "new instance only; file/OS/SQL/TLS/process effects explicitly budgeted",
     "compatibility": "legacy defaults and old tests unchanged; new live branch gated",
     "offline_responsibility": "D1B_TEST_PLAN new52 plus reused68", "deployment_responsibility": "separate B2 acceptance; NOT_RUN",
     "authorization": "B1 code/testing then B2 real deployment, each independent", "blocker": "ENTRYPOINT_NOT_IMPLEMENTED" if files else "P1_INDEPENDENT_AUTHORIZATION_PENDING"}
    for gid, topic, before, after, reuse, files in gaps]})

identity = {"schema": "r20-instance-contract/1", "status": "SPEC_READY_RUNTIME_UNVERIFIED", "AUTHORIZED": False,
    "environment_id": "h2-authority-synth-001", "approved_root": str(DEPLOY), "confirmed_config": str(CONFIRMED),
    "operating_domain": "one local Windows NTFS host, trusted researcher SID/SYSTEM/admin and runtime; no hostile code under service SID",
    "actual_SID": None, "actual_PID": None, "actual_process_creation_FILETIME": None, "actual_process_epoch": None,
    "config_digest_policy": "hash full effective immutable live config excluding its own digest and transient observed PID/epoch/results; approval binds config/source digests, config never hashes the approval document back",
    "deployment_binding": ["environment_id", "canonical approved root", "root volume/file-ID", "instance_uuid256", "DB volume/file-ID", "initialization_id", "source_manifest_digest", "application_version=0.16.0 + deploy revision", "origin_file_digest_set", "Python image path/file-ID/hash", "dependency versions and origin lock", "effective full config digest", "h2 synthetic scope"],
    "os_binding": ["TokenUser SID", "process DACL", "PID + creation FILETIME via retained handle", "image from handle", "own listener getsockname and child handle; not global process/port enumeration"],
    "trusted_bootstrap": {"approval_source": "researcher-approved nonsecret artifact and ACL-protected execution record; ID/approved boolean alone grants nothing", "operations": ["prepare", "initialize", "start", "stop"], "P2": False, "issuer_location": "trusted child entry after handles/source/OS verification", "capability": "process-local opaque registry, not serialized/deserialized", "one_context_one_store": True},
    "persistent_instance_id": {"creation": "CSPRNG256 after exclusive fresh-root reservation; before keys/DB", "path": "config/instance.json", "bind_to": ["approved root", "root physical ID", "host scope", "owner SID", "initialization_id"], "clones": "same UUID with mismatched approved root/file IDs refused; same-SID/admin hostile clone beyond trust model", "restart": "identity may persist; runtime epoch always fresh and new execution approval required", "anti_rollback": False, "global_clone_detection": False},
    "single_active": {"resource": "runtime/instance.lock", "mechanism": "Win32 CreateFileW shareMode=0, stable physical file, kept open; no path-only lock or PID-only lock", "before": "any DB open/instance modification", "handoff": "parent-to-owned-child explicit inherited handle allowlist; retain at least one live handle until child ready; close only own duplicates", "abnormal_exit": "OS releases owned handles; if parent survives it releases after child-exit evidence", "limits": "cooperating approved writer; malicious same-SID/old CLI/DB ACL bypass outside domain"},
    "session_contract": {"max_session_total_reads": 1, "current_B1_B2_P2_reads": 0,
        "future_approval_tuple": ["authorization_id", "instance_uuid", "root physical ID", "DB file-ID", "source/config digests", "PID+creation", "process_epoch", "singleton approved_scope", "caller/issuer identity", "expiry"],
        "namespace": "R16 connection object + authorization_id + epoch + canonical scope; enforce one Store/connection for lifecycle",
        "restart": "old approvals invalid; no auto authorization recovery, no same-envelope rebind", "issuer_rebuild": "shared process-lifecycle registry and R16 namespace; no new connection or epoch inside one live lifecycle", "cross_process_replay_claim": "epoch-scoped invalidation under exclusive instance and trusted approval; no durable adversarial rollback resistance"},
    "recovery": {"mode": "CLASSIFY_ONLY", "SQL": 0, "state_key_load": 0, "world_decrypt": 0, "automatic_restart": False, "automatic_marker_repair": False, "key_DB_claim": "file identity and trusted initialization provenance only; cryptographic content/key pairing remains unverified on recovery without separate permission"},
    "no_claims": ["hardware/remote loaded-memory attestation", "malicious same-SID isolation", "durable global authorization replay ledger", "anti-rollback storage", "all historical writer fencing", "native currentness/typed O/COMPLETE"]}
put("D1B_INSTANCE_IDENTITY_CONTRACT.json", identity)

directories = [".", "config", "authority", "secure", "logs", "runtime", "evidence", "tmp", "control", "artifacts", "artifacts/src", "artifacts/src/auth_lifecycle", "artifacts/src/auth_lifecycle/online_state", "artifacts/scripts"]
files = ["config/deployment.json", "config/instance.json", "config/initialization_receipt.json", "evidence/deployment_approval.json", "evidence/ownership.jsonl", "evidence/lifecycle.jsonl", "artifacts/source_manifest.json", "artifacts/runtime_lock.json", "secure/authority.key", "secure/server.key", "secure/server.crt", "secure/authority.json", "authority/authority.db", "authority/initialized", "authority/storage_configuration.json", "authority/database_ops.jsonl", "authority/transport.jsonl", "runtime/instance.lock", "runtime/authority_metadata.json", "runtime/state.json", "runtime/stop_receipt.json", "control/authority_ready.json", "logs/service_stdout.log", "logs/service_stderr.log", "evidence/failure.json", "config/initialization.pending.json"]
sql = ["PRAGMA page_size=4096", "PRAGMA page_size", "PRAGMA max_page_count=2048", "PRAGMA journal_mode=DELETE", "PRAGMA synchronous=FULL", "PRAGMA synchronous", "PRAGMA busy_timeout=0", "BEGIN IMMEDIATE", "CREATE TABLE authority_state(id INTEGER PRIMARY KEY CHECK(id=1),version INTEGER NOT NULL,ciphertext BLOB NOT NULL)", "CREATE TABLE authority_events(version INTEGER PRIMARY KEY,operation TEXT NOT NULL,projection TEXT NOT NULL)", "PRAGMA user_version=2", "INSERT INTO authority_state VALUES(1,?,?)", "INSERT INTO authority_events VALUES(?,?,?) [synthetic version1]", "INSERT INTO authority_events VALUES(?,?,?) [synthetic version2]", "COMMIT"]
store_sql = ["PRAGMA user_version [strict context first; require2]", "PRAGMA journal_mode=WAL", "PRAGMA synchronous=FULL", "PRAGMA synchronous", "PRAGMA busy_timeout=5000", "PRAGMA wal_autocheckpoint=1000", "SELECT version FROM authority_state WHERE id=1"]
cost_names = ["C_preflight", "C_source_validation", "C_identity", "C_initialize", "C_initialization", "C_database", "C_store", "C_key", "C_tls", "C_host_registration", "C_host", "C_network", "C_listener", "C_logging", "C_shutdown", "C_recovery", "C_cleanup", "C_retry"]
budget = {"schema": "r20-budget-proposal/1", "status": "PROPOSED_CAPS_NOT_EXECUTED", "measurement": "NOT_MEASURED", "D1B1": "NOT_RUN", "D1B2": "NOT_RUN",
    "directory_paths_under_root": directories, "directories_max": 14, "parent_creation": {"path": str(DEPLOY.parent), "max": 1, "condition": "only if absent and explicitly covered by B2; trusted DACL, preserve on stop"},
    "fixed_persistent_files": files, "fixed_files_max": 26, "source_files_max": 64, "source_total_bytes_max": 2097152,
    "source_copy_scope": "package __init__, flat online_state .py/.sql, approved launcher script; no tests/venv/secret/runtime/history",
    "SQLite_companions_max": 3, "SQLite_companion_names": ["authority/authority.db-wal", "authority/authority.db-shm", "authority/authority.db-journal"],
    "concurrent_temp_files_max": 3, "maximum_path_count": 96, "path_count_formula": "26+64+3+3=96, root only; separate B2 evidence cap4 files",
    "external_B2_evidence": {"root": str(B2_EVIDENCE), "directories_max": 1, "files_max": 4, "bytes_max": 1048576, "separate_approval_required": True},
    "SQLite": {"initialization_connections": 1, "Store_connections": 1, "simultaneous_max": 1, "lifecycle_connection_total_max": 2,
        "initialization_explicit_transactions": 1, "initialization_normal_SQL": sql, "initialization_normal_SQL_count": 15,
        "strict_Store_normal_SQL": store_sql, "strict_Store_normal_SQL_count": 7, "normal_total_SQL": 22,
        "failure_rollback_attempts_max": 1, "all_path_wrapper_SQL_attempts_max": 23,
        "normal_State_rows": 1, "normal_Event_rows": 2, "ciphertext_bytes_max": 16384,
        "world_read_state": 0, "world_plaintext_decrypt": 0, "SELECT_version_only": 1,
        "migration": 0, "genesis_fallback": 0, "checkpoint_SQL": 0,
        "database_page_size": 4096, "max_page_count": 2048, "database_logical_bytes_max": 8388608,
        "VFS_flush_WAL_SHM_checkpoint_io": "NOT_MEASURED; close may checkpoint/write; never counted as zero", "recovery_connections": 0},
    "keys": {"state_key_generate": 1, "state_key_bytes": 32, "state_key_write": 1, "state_key_readback": 1,
        "AES_GCM_encrypt": 1, "nonce12_generate": 1, "state_decrypt": 0, "TLS_RSA2048_generate": 1,
        "TLS_private_key_write": 1, "TLS_sign_certificate": 1, "TLS_certificate_write": 1,
        "SSLContext_load_cert_chain": 1, "runtime_state_cipher_calls": 0, "secret_value_output": 0,
        "underlying_OpenSSL_file_reads_and_key_copies": "NOT_MEASURED", "Python_secure_zeroization": "not guaranteed; minimize lifetime, drop references"},
    "TLS": {"address": "127.0.0.1", "port": 27443, "minimum": "TLS1.2", "certificate": "fresh local self-signed test cert; IP SAN127.0.0.1, validity<=24h; isolated client trust", "system_trust_changes": 0, "server_contexts_max": 1, "handshake_attempts_max": 3, "handshake_timeout_seconds": 2, "client_validation_calls_max": 2},
    "network": {"listener_bind_attempts": 1, "listen_attempts": 1, "exclusive_bind": "allow_reuse_address=False and Windows SO_EXCLUSIVEADDRUSE required before bind; unsupported→refuse", "accept_attempts_with_connection_max": 3, "accepted_connections_concurrent_max": 1, "approved_client_connections_max": 2, "backlog": 1, "HTTP_requests_max": 2, "request_seconds_max": 2, "request_body_bytes_max": 1024, "response_bytes_max": 4096, "auto_port_fallback": 0, "plaintext_HTTP": 0, "application_business_dispatch": 0, "availability_under_local_DoS": "not guaranteed; connection cap exhaustion closes safely"},
    "processes": {"Authority_children_total_max": 1, "Authority_children_concurrent_max": 1, "supervisors_max": 1, "parallel_stop_CLI_max": 1, "controlled_processes_peak": 3, "Authority_application_threads_max": 1, "native_OS_thread_count": "NOT_MEASURED", "Authority_child_subprocesses": 0, "all_process_scan": 0, "forced_termination": 0, "start_automatic_retries": 0, "initialize_automatic_retries": 0},
    "Store": {"construct_max": 1, "same_connection_and_lock": True, "close_max_successful": 1, "constructor_failure_connection_ownership": "registered immediately after connect before first execute"},
    "host": {"dormant_bind_max": 1, "live_context_max": 1, "P2_activation": 0, "permits": 0, "protected_reads": 0, "new_epoch_per_start": True},
    "logging": {"lifecycle_events_max": 32, "ownership_entries_max": 128, "database_ops_events_max": 8, "transport_events_max": 2, "record_bytes_max": 2048, "structured_log_total_bytes_max": 524288, "stdout_stderr_each_bytes_max": 65536, "rotation": 0, "EventLog_init_max": 4, "logical_appends_max": 170, "logical_appends_formula": "32+128+8+2=170"},
    "time_limits_seconds": {"initialize": 15, "child_start_to_ready": 10, "service_ready_lease": 60, "graceful_stop": 5, "classify_recovery": 10, "B2_run_total": 120},
    "time_limit_semantics": "cooperative API timeout/observation deadlines; uninterruptible OS I/O may exceed them; timeout→RECOVERY_REQUIRED, no assertion of forced bounded process exit",
    "cleanup": {"automatic_persistent_deletion": 0, "automatic_temp_delete_max": 3, "whole_tree_delete": 0, "owned_handle_close": "each acquired object exactly once/idempotent", "ownership_unknown": "retain RECOVERY_REQUIRED; no delete/no terminate"},
    "logical_content_budget_bytes": 16777216, "physical_IO_time_disk_CPU": "NOT_MEASURED; OS and SQLite VFS amplification recorded separately; quota excess fails safely",
    "costs": {k: {"actual": "NOT_MEASURED", "B1": "NOT_RUN", "B2": "NOT_RUN", "method": "phase perf_counter_ns + resource attempt/success counters; OS/VFS unsupported observations remain UNKNOWN"} for k in cost_names},
    "cost_aliases": {"C_initialize": "C_initialization", "C_host": "C_host_registration", "C_listener": "part of C_network"},
    "retry_policy": "automatic retries0; failed start consumes its authorization; fresh explicit approval for another start; no hidden exponent/cost claims"}
budget["phase_accounting"] = [
    {"phase":"preflight/source/identity", "operations_max":"one approved config pass; <=64 source artifacts, <=2 source validation passes plus one copy-read pass; exact runtime-origin list fixed after B1", "worst_persistent":"bounded external refusal evidence only", "failure_loss":"source/hash/OS inspection CPU+I/O; no instance mutation", "costs":["C_preflight","C_source_validation","C_identity"]},
    {"phase":"reserve/prepare", "operations_max":"14 directories plus at most one explicitly approved parent; <=64 source copies, one UUID/initialization identity and one exclusive lock", "worst_persistent":"private partial new root/source/ownership record", "failure_loss":"new root reserved permanently for review; no overwrite/retry", "costs":["C_initialize","C_logging"]},
    {"phase":"key/TLS material", "operations_max":"one state key generation/write/readback; one TLS key/certificate generation/write/sign; one AES-GCM encryption", "worst_persistent":"private key/cert/config files plus at most3 temp files", "failure_loss":"partially stored test keys retained; no automatic regeneration", "costs":["C_key","C_tls"]},
    {"phase":"SQLite initialization", "operations_max":"one connection, one explicit transaction, 15 normal statements or prefix plus at most1 rollback", "worst_persistent":"new encrypted DB and rollback journal with seed receipt pending", "failure_loss":"commit uncertainty requires classification; source world reads0", "costs":["C_initialization","C_database"]},
    {"phase":"Store construction", "operations_max":"one ctor, one connection,7 wrapper SQL; one marker and storage config publication; no migration/genesis", "worst_persistent":"DB/WAL/SHM,7 metrics appends,marker/config", "failure_loss":"constructor-local cleanup required even before object return", "costs":["C_store","C_database","C_logging"]},
    {"phase":"Host/TLS/listener", "operations_max":"one dormant bind,one SSLContext cert_chain load,one bind/listen; at most3 accepts/handshakes and2 HTTP requests", "worst_persistent":"runtime/Ready candidate and bounded transport log", "failure_loss":"burned start claim and stale epoch candidate; no new port", "costs":["C_host_registration","C_tls","C_network"]},
    {"phase":"shutdown/cleanup", "operations_max":"one owning close pass over finite resource stack; stop replay<=2 only classifies already closed objects; temp deletion<=3; persistent deletion0", "worst_persistent":"all DB/key/evidence retained; possibly partial stop receipt", "failure_loss":"unproved exit remains RECOVERY_REQUIRED; forced termination0", "costs":["C_shutdown","C_cleanup"]},
    {"phase":"recover/retry", "operations_max":"one separately approved classifier pass; SQL/key/decrypt/repair/start0; automatic retries0", "worst_persistent":"classification receipt, previous state retained", "failure_loss":"no key/DB content validation; extra access requires new approval", "costs":["C_recovery","C_retry"]},
]
for row in budget["phase_accounting"]:
    row["measurement"] = "NOT_MEASURED; future per-phase timers and attempt/success/resource counters; unsupported OS/VFS values remain UNKNOWN"
put("D1B_RESOURCE_BUDGET.json", budget)

stages = [
    ("NEW", "confirmed parameters and separate B1/B2 permission evaluated", "trusted bootstrap", "read approved files/source metadata only", [], "none", "effective source/config/OS/root preconditions agree", "mismatch→FAILED", "close inspection handles", "preflight can be repeated with no stateful action", "NEW"),
    ("PREFLIGHTED", "all predicates hold; parent/root policy verified", "bootstrap+OS provider", "exclusive reserve fresh root/private directories and identity", ["root/dirs", "instance.lock", "instance UUID"], "reservation and ownership intent", "fresh root and exclusive physical handle", "create/ACL/ownership failure→RECOVERY_REQUIRED if any artifact exists", "close own handles; retain root/evidence", "no automatic retry after root creation", "reserved/incomplete only"),
    ("RESOURCES_RESERVED", "exclusive lock held; root UUID/file-ID recorded", "initializer", "new keys/TLS material/config/source manifest", ["state/TLS keys", "certificate", "source artifact", "config"], "initialization.pending stage", "all required artifacts privately and durably prepared", "key/TLS/source/log error→FAILED/RECOVERY_REQUIRED", "keep persistent material, remove only known-owned temp", "no automatic regeneration/overwrite", "DORMANT incomplete"),
    ("INITIALIZING", "prepared keys and exclusive DB-new creation", "initializer", "15 SQL / one explicit transaction / encrypted synthetic seed", ["DB", "journal", "seed receipt"], "SQLite commit then seed receipt; cross-file publication non-atomic", "DB commit and seed receipt flushed; no pending ambiguity", "commit/receipt uncertainty→RECOVERY_REQUIRED", "rollback if in_transaction then close; retain DB/key", "zero auto retry", "classification only"),
    ("SEED_READY", "initialization receipt binds new DB/key artifact provenance", "start supervisor", "claim one start durably, launch exactly one owned child", ["owned child", "new epoch", "stop Event"], "start claim irrevocably spent before process creation", "child acknowledges inherited lock and exact approval/source/OS tuple", "uncertain spawn/claim→RECOVERY_REQUIRED", "retain lock until child handed off; no blind spawn retry", "new independent execution approval for another start", "DORMANT/no child proof unknown"),
    ("STORE_READY", "child owns verified lock/context; schema must be2", "child resource owner", "strict ctor once, 7SQL, marker/storage-config publication", ["connection", "RLock", "metrics", "marker/config"], "Store config/log; version2 row unchanged", "same Store+connection+lock captured", "ctor/registration error→FAILED", "constructor-local connection guard and outer owner both idempotent", "no ctor retry/connection replacement", "seed retained, no listener"),
    ("HOST_DORMANT", "same Store verified; no P2 approval", "live deployment issuer", "bind inert host descriptor; prepare Handler/TLS", ["host descriptor", "TLS context"], "host status only", "P2=false, permits0, reads0", "Handler/TLS error→FAILED", "invalidate context→close TLS refs/connection", "no rearm", "DORMANT closed"),
    ("LISTENER_READY", "TLS cert_chain validated before bind; dormant remains", "bounded live server", "exclusive socket bind/listen once, prepare bounded accept loop", ["listener", "ready candidate"], "candidate metadata bound epoch", "loopback/TLS/listener owned; Ready publish succeeds", "bind/Ready error→FAILED", "server_close without shutdown before loop; revoke capability first", "port conflict stops", "no active listener after cleanup"),
    ("SERVICE_READY", "loop started and startup receipt linked to owned child", "bounded live server+supervisor", "two bounded TLS clients incl one fixed denied request; poll stop/lease", ["accepted sockets bounded"], "audit/lease record only; no world mutation", "child handle+lease valid and bounded TLS startup check", "I/O/log/budget/lease failure→STOPPING", "close accepted sockets, stop admissions", "no implicit reconnect/restart", "Dormant until stop"),
    ("STOPPING", "stop Event, lease expiry or error; identity exact", "owner child", "invalidate context, finish bounded handler, close listener/Store/logs, release lock last", [], "final shutdown receipt if possible", "owned child exits; parent waits exact handle; lock free", "cleanup/timeout→RECOVERY_REQUIRED", "continue independent cleanup; retain primary+cleanup errors", "stop replay classified idempotently, no new start", "no P2; ownership ambiguity retained"),
    ("STOPPED", "child exit proved by retained handle and durable receipt", "supervisor", "status record, preserve all persistent DB/key/evidence", [], "STOPPED record", "quiescent and resource counters closed", "receipt loss→UNKNOWN/RECOVERY_REQUIRED", "no persistent deletion", "new start needs new approval/epoch; outside first B2 cap", "STOPPED Dormant"),
    ("FAILED", "failure with provable closed ownership", "resource owner", "bounded safe cleanup/evidence", [], "fixed error-class record", "all owned live handles closed", "ownership uncertain→RECOVERY_REQUIRED", "best effort independent closes; no recursive delete", "no auto retry", "closed; persistent seed remains"),
    ("RECOVERY_REQUIRED", "crash, partial initialization, timeout or uncertain ownership", "separately approved recovery classifier", "inspect owned ledger/files/target only; no SQL/key load/decrypt/start", [], "classification receipt, no repair", "clear diagnosis of MISSING/PARTIAL/STOPPED/CURRENTLY_OWNED/UNKNOWN", "extra access or ambiguity→retain state", "delete0, terminate0, persistent overwrite0", "new approval for any corrective action/start", "DORMANT diagnosis only"),
]
put("D1B_LIFECYCLE_STATE_MACHINE.json", {"schema": "r20-lifecycle/1", "status": "SPEC_ONLY_NOT_RUN",
    "state_rows": [{"state": s, "precondition": precond, "trusted_actor": actor, "allowed": allowed, "created": created, "persistent_change": persistent, "success": success, "failure": failure, "cleanup_owner": cleanup, "retry": retry, "minimum_recovered_state": recovered} for s,precond,actor,allowed,created,persistent,success,failure,cleanup,retry,recovered in stages],
    "normal_edges": [[a,b] for a,b in zip([s[0] for s in stages[:11]], [s[0] for s in stages[1:11]])],
    "failure_edges": "any state with acquired resources→STOPPING/FAILED/RECOVERY_REQUIRED; external crash inferred as RECOVERY_REQUIRED; no transition activates P2",
    "cross_file_atomicity": "SQLite transaction is atomic; keys/manifests/markers are a separate checked publication protocol. Ambiguous crash requires manual classification.",
    "status_record_is_not_liveness_attestation": True})

faults = [
    ("路径预检失败", "NEW", "canonical/final path/reparse/alias check", "inspection handles", "none", "none", "NEW"),
    ("OS身份不符", "NEW", "TokenUser/image/process-DACL mismatch", "self/child query handle", "none", "none", "NEW"),
    ("源码摘要不符", "NEW", "artifact hash/origin differs", "source read handles", "none", "approved artifacts/evidence", "NEW"),
    ("依赖不匹配", "NEW", "version/origin/runtime lock differs", "metadata read handles", "none", "fixed error evidence", "NEW"),
    ("部署目录创建失败", "PREFLIGHTED", "exclusive CreateDirectory fails or existing target", "maybe only parent created", "reservation intent if available", "existing target untouched; owned parent retained", "RECOVERY_REQUIRED if partial"),
    ("目录创建后中断", "RESOURCES_RESERVED", "root exists, ownership/UUID incomplete", "root/private dirs/lock", "partial intent", "all uncertain persistent files", "RECOVERY_REQUIRED"),
    ("SQLite连接失败", "INITIALIZING", "connect/create-new open error", "DB handle if returned, keys", "keys/config already stored", "keys/DB artifact/evidence", "RECOVERY_REQUIRED"),
    ("初始化事务中断", "INITIALIZING", "before/during COMMIT", "connection/journal", "SQLite uncertain commit", "DB/journal/keys/seed intent", "RECOVERY_REQUIRED"),
    ("DB提交后marker或receipt缺失", "INITIALIZING", "COMMIT succeeds; publication fails", "committed DB", "version2 row + events may exist", "DB/key and pending record; do not fabricate marker", "RECOVERY_REQUIRED"),
    ("密钥生成后写盘失败", "RESOURCES_RESERVED", "exclusive write/fsync fails", "generated bytes/private temporary", "possibly partial key file", "private partial artifacts for owner review", "RECOVERY_REQUIRED"),
    ("密钥已写而DB失败", "INITIALIZING", "DDL/INSERT/COMMIT refusal", "key/DB/journal", "key committed; DB ambiguous", "key and DB; no key regeneration", "RECOVERY_REQUIRED"),
    ("TLS证书创建失败", "RESOURCES_RESERVED", "sign/serialize/cert publication fails", "TLS key/cert partial", "possibly new private key", "private material and safe error", "RECOVERY_REQUIRED"),
    ("TLS key写入后listener失败", "HOST_DORMANT", "load_cert_chain/bind/listen fails", "Store/TLS refs/listener if returned", "seed and TLS material", "persistent material, failed epoch", "FAILED or RECOVERY_REQUIRED"),
    ("EventLog初始化或写入失败", "ANY_ACQUIRED", "directory/append/flush budget/error", "current owned stack", "prior committed state unchanged", "primary+cleanup error classes; external bounded fallback", "RECOVERY_REQUIRED if final evidence incomplete"),
    ("Store构造后Host注册失败", "STORE_READY", "binding rejects source/lock/context", "Store/connection/lock", "7SQL may have happened, marker/config", "seed, logs, consumed start claim", "FAILED"),
    ("Host注册后Handler构造失败", "HOST_DORMANT", "Handler/TLS factory raises", "host/Store/TLS refs", "host record dormant", "same failed epoch; no read slot rearm", "FAILED"),
    ("Listener创建后Ready失败", "LISTENER_READY", "metadata/ready fsync fails", "listener/Store/host", "candidate record possibly written", "stale record marked ambiguous; preserve evidence", "FAILED or RECOVERY_REQUIRED"),
    ("端口冲突", "HOST_DORMANT", "single exclusive bind error", "socket (even unbound) / Store", "seed intact", "failed attempt; conflicting foreign listener untouched", "FAILED"),
    ("启动后立即异常退出", "SERVICE_READY", "owned child dies after Ready", "OS releases child handles; parent owns duplicates", "stale Ready/epoch", "start claim, DB/key/Ready evidence", "RECOVERY_REQUIRED"),
    ("正常停止期间异常", "STOPPING", "handler/server_close/connection.close/fsync failure", "remaining owned handles", "partial stop receipt", "all persistent state; aggregate close errors", "RECOVERY_REQUIRED"),
    ("停止成功但ACK丢失", "STOPPED", "stop caller loses reply", "possibly only parent process handle", "stop receipt may be durable", "receipt/epoch; never use lost ACK as restart permit", "STOPPED if proved else RECOVERY_REQUIRED"),
    ("清理途中再次崩溃", "STOPPING", "after some closes before final ledger", "subset of remaining owned handles", "partial cleanup record", "unknown resources retained; no unproven file deletion", "RECOVERY_REQUIRED"),
    ("重启发现旧运行marker", "SEED_READY", "old Ready/pending epoch present", "static records only", "old start claim", "old markers and phase history", "RECOVERY_REQUIRED"),
    ("同实例两个并发启动", "SEED_READY", "second exclusive lock open denied", "first owner lock/child; second inspection handles", "one start claim at most", "first process untouched", "second FAILED; first unchanged"),
    ("复制DB或实例目录", "NEW", "root/DB file-ID or approved-root mismatch", "foreign/copied static references", "cloned UUID insufficient", "copy left untouched; no adoption", "RECOVERY_REQUIRED"),
    ("旧authorization_id重放", "HOST_DORMANT", "same envelope in current/other process", "same context and original consumed slot", "current phase/start claim", "consumed slot or rejection; no fresh connection", "DORMANT/REJECTED"),
    ("不同issuer重建", "HOST_DORMANT", "second deployment issuer/mount for same session", "process-wide registry + same Store", "first registration/start claim", "no replacement context/connection", "DORMANT/REJECTED"),
    ("旧epoch继续请求", "SERVICE_READY", "old tuple presented after restart/new epoch", "current listener/context", "new epoch; old approval invalid", "fixed refusal only", "DORMANT/REJECTED"),
]
matrix=[]
for i,(name,phase,point,resources,committed,keep,post) in enumerate(faults,1):
    matrix.append({"id":"F%02d"%i,"name":name,"initial_phase":phase,"injection_point":point,
        "created_resources":resources,"committed_state":committed,
        "cleanup_owner":"creator/OwnedResources in reverse acquisition order; constructor owns connection before return; supervisor owns child handle",
        "preserve":keep,"deletable":"only positively owned, closed, whitelisted temporary files (max3); persistent deletion0",
        "idempotent_recovery":"check ownership+file-ID+epoch; close own remaining handles; missing object benign only after identity proof; ambiguous record retained; no auto repair/start",
        "safety_postcondition":post+"; P2=0; no auto retry/fallback/foreign kill", "future_test_id":"F%02d"%i,"status":"NOT_RUN"})
put("D1B_FAILURE_AND_CLEANUP_MATRIX.json",{"schema":"r20-failure-cleanup/1","count":28,"status":"SPEC_ONLY_NOT_RUN","rows":matrix})

extra_tests=[
    ("T29","six-operation parser rejects unknown/secret/scope expansion; R19 offline argv preserved"),
    ("T30","D1A/B1/B2/P1/P2 approval types cannot substitute; opaque object cannot come from JSON flags"),
    ("T31","exact source/config digest, module origins and parent/child source set"),
    ("T32","targeted self/owned-child SID+creation+image; no process enumeration"),
    ("T33","exclusive root, reparse/hardlink/file-ID mismatch and owner-only ACL facts"),
    ("T34","15-statement seed transaction, two synthetic events, AES public-vector file-DB codec plus bounded fresh temporary test-key roundtrip"),
    ("T35","strict Store7SQL, schema!=2 before mutation, no genesis/migration; constructor cleanup"),
    ("T36","bounded temporary test TLS key/cert/context load without sockets; TLS-before-bind, loopback/27443/exclusive bind/no retry and bounded accept"),
    ("T37","all-stage OwnedResources LIFO, primary error retained when cleanup also errors"),
    ("T38","Dormant source same Store/connection/lock; no permits or world read"),
    ("T39","explicit inherited lock handle transfer keeps continuous single-active ownership"),
    ("T40","stop before loop, during handshake and after loop avoids shutdown deadlock"),
    ("T41","exact owned PID+FILETIME stop event, no foreign termination; repeated stop classification"),
    ("T42","normal stop retains DB/key/logs; timeout ownership ambiguity stays RECOVERY_REQUIRED"),
    ("T43","recover metadata-only, SQL/key/decrypt/start zero, no marker repair"),
    ("T44","cross-file COMMIT/receipt ambiguity and clone rejection with all channels considered"),
    ("T45","new process epoch makes old approval invalid; startup failure consumes start permission"),
    ("T46","same lifecycle cannot construct second Store, replace connection or rearm via new issuer"),
    ("T47","unknown/Dormant/scope/native gaps remain; no typed O/o/COMPLETE upgrade"),
    ("T48","compatibility AST and original24+44 test classes under fresh declared source mapping"),
    ("T49","canary scan all stdout/log/errors/receipts; no raw argv/env/state/key output"),
    ("T50","deny real socket/RPC/deployment access; child allowlist/count/timeout and output path guard"),
    ("T51","attempt/success resource counters, SQL rollback/VFS unknowns and per-phase cost labels"),
    ("T52","all six operations have coded refusal/NOT_IMPLEMENTED contract until gates satisfied"),
]
b2_tests=[
    ("B201","new approved root/source snapshot/config digest match"),("B202","approved SID, process creation/image and physical root/DB references agree"),
    ("B203","one initialization15SQL+strictStore7SQL and resource caps"),("B204","fresh key/TLS/seed provenance; no old-world read or migration"),
    ("B205","only127.0.0.1:27443; pinned self-signed IP SAN TLS client success"),("B206","Dormant, permit0/read0 and one denied application request before Store"),
    ("B207","one Store/one active lock/one epoch; no restart or P2"),("B208","bound Ready lease and minimal owned-child startup receipt"),
    ("B209","graceful owned stop closes sockets/connection/lock; persistent files retained"),("B210","zero native/Provider/Controller/P1/P2/B2write/S5 and no foreign cleanup"),
    ("B211","log/IO/error evidence and resource accounting with UNKNOWN where unobserved"),("B212","actual argv/source/dependency/termination outcome locked; no automated extra run"),
]
put("D1B_TEST_PLAN.json", {"schema":"r20-future-test-plan/1","all_current_status":"NOT_RUN",
    "B1_new_count":52,"B1_new_cases":[{"id":x["future_test_id"],"expected":x["name"]+" safe cleanup","status":"NOT_RUN"} for x in matrix]+[{"id":i,"expected":e,"status":"NOT_RUN"} for i,e in extra_tests],
    "B1_reuse_new_R19":24,"B1_reuse_legacy_A1_H1":44,"B1_planned_total":120,
    "old_tests_and_locks_mutable":False,"old_runner_reuse":"load original classes through new runner with explicit old→proposed source delta; original runners/prechecks unchanged",
    "B1_output_root":str(B1_OUTPUT),"B1_execution_permissions_requested":{
        "direct_commands":3,"command_suites":["new52","r19_24","legacy44"],"base_python":PYTHON,
        "legacy_python":str(PROJECT/'.venv-dsat-r07-networkx-3.7/Scripts/python.exe'),
        "new52_scope":{"private_test_subdirs_max":64,"file_SQLite_connections_total_max":104,"memory_SQLite_connections_total_max":16,"connections_per_case_max":2,
            "test_file_paths_max":512,"test_output_bytes_max":67108864,"fake_child_launches_total_max":8,"fake_children_concurrent_max":2,
            "fake_child_seconds_max":10,"fake_child_total_seconds_max":60,"threads_test_max":4,"threads_test_total_created_max":16,
            "test_keys":"public AES vectors plus explicitly owned temporary test-only keys; never under deployment root or used by a real service",
            "temporary_test_state_key_generations_max":2,"temporary_test_TLS_key_cert_generations_max":2,"temporary_test_SSLContext_loads_max":2,
            "real_service_keys":0,"TLS_handshakes":0,"listeners":"simulated only", "existing_crypto_import":True,
            "Win32_calls":"own token/process handles, newly owned test paths/ACL/file-ID/lock/Event; no global scans/no production target",
            "network":0,"service_processes":0,"real_deployment_root_access":0,"new_dependencies":0},
        "R19_24_memory_connections_max":8,"legacy44_memory_connections_max":32,
        "suite_soft_seconds_max":300,"approved_failure_fix_reruns_max":1,"all_suites_invocations_max":6,
        "baseline_caps_apply_per_invocation":True,"all_run_logs_retained":True,
        "aggregate_max_if_all_authorized_reruns_used":{"stub_child_launches":16,"file_SQLite_connections":208,"new52_memory_connections":32,"R19_24_memory_connections":16,"legacy44_memory_connections":64,"temporary_test_state_key_generations":4,"temporary_test_TLS_key_cert_generations":4,"temporary_test_SSLContext_loads":4,"all_suite_output_bytes":402653184},
        "B1_requests_authorized_now":False},
    "B2_acceptance_count":12,"B2_cases":[{"id":i,"expected":e,"status":"NOT_RUN"} for i,e in b2_tests],
    "B2_requests_authorized_now":False,"B2_fresh_start_attempts_max":1,"B2_invasive_fault_injections":0,
    "B2_note":"fault injection is B1 domain; B2 one controlled initialize/start/TLS/denied-request/stop, no independent P1/P2"})

ops = {}
effects = {"prepare":"static config/source/OS preflight and fresh owned dirs/artifact reservation; no DB/key/listener", "initialize":"new synthetic keys/TLS/SQLite seed once; no Store/listener", "start":"consume one start claim; launch one verified child; Store/dormant/TLS bounded listener", "status":"read only own recorded lifecycle receipt; explicit OBSERVED_AT/UNKNOWN; no process or DB enumeration", "stop":"exact owned process/epoch event and wait; no force kill; preserve data", "recover":"classification only, no SQL/key/decrypt/repair/restart; new permission for corrective action"}
for op in effects:
    ops[op] = {"semantic_operation":op,"implemented_now":False,"command_executable":False,
        "actual_argv":None,"blocker":"ENTRYPOINT_NOT_IMPLEMENTED","AUTHORIZED":False,"EXECUTED":False,
        "future_python":PYTHON,"future_reviewed_script":str(PROJECT/'scripts/run_h2_authority_service.py'),
        "future_frozen_script_after_prepare":str(DEPLOY/'artifacts/scripts/run_h2_authority_service.py'),
        "proposed_argument_schema_only_not_argv":{"operation":op,"manifest":"absolute approved artifact/operation document", "approval_ref":"absolute ACL protected approval record, ID alone insufficient", "result":"fixed approved evidence path"},
        "implicit_not_user_overridable":{"environment_id":"h2-authority-synth-001","root":str(DEPLOY),"address":"127.0.0.1","port":27443,"TLS_REQUIRED":True,"P2":False},
        "effects":effects[op],"timeout_seconds":{"prepare":15,"initialize":15,"start":10,"status":5,"stop":5,"recover":10}[op],
        "max_successful_attempts_first_B2":0 if op == "recover" else (1 if op in {"prepare","initialize","start"} else 2),
        "recover_separate_permission_required":op == "recover",
        "automatic_retries":0,"success_predicate":"approved identity/source/epoch plus operation-specific receipt and owned-handle evidence; record alone does not attest liveness"}
put("D1B_COMMAND_LOCK.json", {"schema":"r20-command-spec/1","status":"SEMANTIC_SPEC_ONLY_ENTRYPOINT_NOT_IMPLEMENTED",
    "command_executable":False,"actual_argv":None,"AUTHORIZED":False,"EXECUTED":False,
    "actual_supported_R19_interface":{"script":str(PROJECT/'scripts/run_h2_authority_service.py'),"args":["--manifest PATH","--mode offline (default)"],"capability":"offline plan only"},
    "operations":ops,"future_exit_codes_proposed":{"0":"operation succeeded or proved already-stopped","2":"refused/config/source/identity/gate mismatch","3":"NOT_IMPLEMENTED","4":"FAILED safely closed","5":"RECOVERY_REQUIRED/UNKNOWN ownership/timeout"},
    "P1a":{"authorized":False,"implemented_live":False},"P1b":{"authorized":False,"implemented":False},"P2":{"authorized":False},
    "promotion_rule":"after B1 implementation/checks freeze actual parser support, source SHA, SID and exact argv; only then request B2 execution approval"})

auth = {"schema":"r20-staged-authorization-request/1","AUTHORIZED":False,"EXECUTED":False,
    "current_phase":"D1-B0_ANALYSIS_ONLY","B1":{"status":"READY_FOR_IMPLEMENTATION_REVIEW_AUTHORIZATION_PENDING","approved":False,
        "purpose":"nine-target live startup code offline implementation plus52 new and68 compatibility cases",
        "file_lock":"D1B_SOURCE_AND_FILE_LOCK.json","test_plan":"D1B_TEST_PLAN.json","output_root":str(B1_OUTPUT),
        "allowed_if_approved":["modify exact3 existing files after snapshots", "add exact5 Python files and1 fixture subtree", "existing dependency imports, synthetic file/memorySQLite and public AES vectors", "per new52 invocation at most2 temporary test-only state keys,2 test TLS key/certs and2 SSLContext loads; no socket/handshake", "bounded8 owned stub child launches and Win32 tests under new test root", "three separate suite domains and at most one authorized repair rerun each", "document actual budgets/hashes/argv and retain all failures"],
        "forbidden_even_if_B1_approved":["approved deployment root or its DB/key reads/writes", "real Authority/Controller/Provider/Casdoor process", "socket/TLS handshake/RPC", "real service state/TLS key generation or reuse", "P1/P2/typedO/S3B2/S5", "new dependency installation", "unlisted source/tests/history changes"],
        "trusted_runtime_SID_needed_for_offline_tests":"only own temporary test process SID query; no nomination of real deployment SID by inference", "all_caps":"D1B_TEST_PLAN B1_execution_permissions_requested"},
    "B2":{"status":"NOT_AUTHORIZED_NOT_YET_EXECUTABLE","approved":False,"new_root":str(DEPLOY),
        "budget":"D1B_RESOURCE_BUDGET.json","outside_evidence_root":str(B2_EVIDENCE),
        "requires_after_B1":["actual B1 code/tests and unchanged-history evidence", "reviewed final loaded-artifact manifest and supported exact argv", "specific OS SID and inherited-handle/ACL validation", "initialize/start/TLS/stop budget accepted", "independent execution approval; root/database/key/TLS scope"],
        "future_bounded_scope":"one fresh prepare/initialize/start/<=2 TLS clients/one denied request/graceful stop; no active P2 or restart",
        "restart_recovery":"classify only after separate permission; corrective action/new epoch/new start need new approval"},
    "P1a_P1b_P2_S3B2_S5":"SEPARATE_NOT_AUTHORIZED","unique_next_action":"approve exact D1-B1 nine-target code+offline fault-test request only",
    "request_basis":"user R20 sections1,14,20 explicitly reserve B1 code/testing and B2 real execution for independent approval"}
put("D1B_AUTHORIZATION_REQUEST.json", auth)
print(json.dumps({"structured_specs_written":10,"targets":9,"faults":28,"new_B1_cases":52,"planned_B1_total":120,"tests_executed":0,"project_edits":0}))
