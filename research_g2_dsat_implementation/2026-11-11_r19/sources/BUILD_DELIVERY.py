"""R19 document/evidence assembly only. Does not import application modules."""
import ast
import hashlib
import json
from pathlib import Path

PROJECT = Path(r"D:\毕业设计\auth-lifecycle")
BASE = PROJECT.parent / "research_g2_dsat_implementation"
RECORD = BASE / "2026-11-11_r19"
OFFLINE = BASE / "2026-11-11_r19_offline"
PYTHON = r"C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
DEPLOY = r"D:\毕业设计\h2_test_runtime\h2-authority-synth-001"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    path = RECORD / name
    if isinstance(value, str):
        path.write_text(value.strip() + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


new = load(OFFLINE / "d1a_002/RESULTS.json")
old = load(OFFLINE / "regressions_002/RESULTS.json")
plan = load(RECORD / "D1A_TEST_PLAN.json")
baseline = load(RECORD / "sources/PRECHECK_LOCK.json")
code = new["code"]
assert code == old["code"]
assert all(sha(Path(row["path"])) == row["sha256"] for row in code)
assert all(c["satisfied"] for result in (new, old) for case in result["details"] for c in case["checks"])

# Preserve the intermediate R19 assembly records before enriching them.
for name in ("D1A_FILE_LOCK.json", "D1A_SECURITY_AUDIT.json", "D1A_TEST_RUNS.json", "SOURCE_LOCK.json"):
    dest = RECORD / "sources" / (Path(name).stem + "_PRE_DELIVERY.json")
    if not dest.exists():
        dest.write_bytes((RECORD / name).read_bytes())

symbols = []
for row in code:
    p = Path(row["path"])
    tree = ast.parse(p.read_text(encoding="utf-8"))
    entries = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            entries.append({"symbol": node.name, "line": node.lineno, "kind": type(node).__name__})
            if isinstance(node, ast.ClassDef):
                entries.extend({"symbol": node.name + "." + c.name, "line": c.lineno,
                                "kind": type(c).__name__} for c in node.body if isinstance(c, ast.FunctionDef))
    symbols.append({**row, "entries": entries})
write("sources/CODE_SYMBOLS.json", {"schema": "r19-code-symbols/1", "method": "AST only; no production import", "files": symbols})

entry_info = [
    (["serve"], "role/root/fault + optional mount ticket and runtime context", "legacy server or fixed refusal before I/O", ["D23", "A01-A20", "H01-H24"], "legacy service has real side effects; this round AST-only; offline contexts rejected before config I/O"),
    (["RuntimeConfig.from_confirmed", "read_offline_json", "build_synthetic_seed", "prepare_public_memory_database", "RuntimeContext.from_offline_host", "RuntimeContext.bind_store", "simulate_bootstrap", "inspect_offline_metadata", "p1b_static_contract"], "confirmed document / synthetic adapters / explicitly owned memory connection", "offline plan / synthetic seed / public memory codec / closed metadata", ["D01-D24"], "only caller-owned memory SQLite/public vectors and simulated lifecycle are exercised"),
    (["parse_args", "offline_plan", "main"], "--manifest PATH [--mode offline]", "JSON offline plan exit0; sanitized refusal exit2", ["D10", "D22", "D24"], "approved offline JSON reads and stdout; no live issuer/init/serve"),
    (["OfflineRecordProvider.read_one", "parse_args", "main"], "--metadata PATH --request PATH [--mode offline]", "closed synthetic metadata exit0; sanitized refusal exit2", ["D17", "D18", "D24"], "two approved offline JSON inputs; no OS provider/process enumeration/DB/RPC"),
    (["configure", "D1ACases.test_D01_confirmed_config", "D1ACases.test_D24_CLI_sinks"], "frozen R19 plan + three new fixture files + memory factory", "24 unittest results and 137 satisfied checks", ["D01-D24"], "new suite imports existing cryptography; old suites stay in separate process domain"),
    (["preflight", "audit", "connect_memory", "run_class", "main"], "--suite {d1a,regressions}", "new append-only run directory, logs, JSON and code snapshots", ["D01-D24", "A01-A20", "H01-H24"], "no spawned children; writes restricted to R19 offline output; in-memory DB limits8/32 by suite"),
    (["CONFIRMED_CONFIG.json", "PUBLIC_VECTORS.json", "CANARIES.json"], "immutable confirmed input and fresh public/synthetic values", "fixture inputs, hashes only in public reports", ["D01-D24"], "canary source is an authorized input; values excluded from public evidence"),
]
lock = load(RECORD / "D1A_FILE_LOCK.json")
for row, info in zip(lock, entry_info):
    entry, inputs, outputs, tests, boundary = info
    row.update(entry=entry, inputs=inputs, outputs=outputs, allowed_tests=tests,
               safety_boundary=boundary, status="IMPLEMENTED_WITHIN_D1A_OFFLINE_SCOPE",
               source_symbol_index="sources/CODE_SYMBOLS.json")
    p = Path(row["path"])
    row["after_sha256"] = sha(p) if p.is_file() else None
    if p.is_dir():
        row["subtree_files"] = [{"path": str(c), "sha256": sha(c)} for c in sorted(p.rglob("*")) if c.is_file()]
write("D1A_FILE_LOCK.json", lock)

common = {"schema": "r19-future-command-lock/1", "date_china": "2026-11-11",
          "AUTHORIZED": False, "EXECUTED": False, "authorized": False, "executed": False,
          "execution_count": 0, "command_executable": False, "actual_argv": None,
          "environment_id": "h2-authority-synth-001", "PARAMETERS_CONFIRMED": True,
          "python": PYTHON, "working_directory": str(PROJECT), "deployment_root": DEPLOY,
          "actual_PID": None, "actual_epoch": None, "actual_OS_identity": None,
          "source_code": code, "approval_required": "independent bounded execution approval after missing code/contracts are resolved"}
launcher = PROJECT / "scripts/run_h2_authority_service.py"
inspector = PROJECT / "scripts/inspect_h2_authority_metadata.py"
write("D1B_COMMAND_LOCK.json", {**common, "phase": "D1-B", "status": "BLOCKED_EXECUTION_ADMISSION_AND_AUTHORIZATION",
    "entrypoint_exists": True, "entrypoint": str(launcher), "entrypoint_sha256": sha(launcher),
    "supported_current_arguments": ["--manifest PATH", "--mode offline (default)"],
    "current_entrypoint_capability": "offline plan only; no real initialization/start interface",
    "offline_argv_example_only": [PYTHON, "-B", str(launcher), "--manifest", str(PROJECT / "tests/fixtures/dsat_authority_runtime/CONFIRMED_CONFIG.json"), "--mode", "offline"],
    "offline_example_is_deployment_command": False, "real_arguments_supported": False,
    "bind_policy": {"address": "127.0.0.1", "port": 27443, "TLS_REQUIRED": True, "conflict": "STOP_NO_FALLBACK"},
    "service_identity": "researcher role confirmed; actual Windows principal/SID and ACL pending",
    "blockers": ["live RuntimeContext issuer/admission absent; validate_service_entry always refuses offline contexts",
                 "strict live launcher, source verification, OS/path/ACL provider and single-active epoch proof absent",
                 "real fresh-key/TLS provisioning, bounded Schema2 persistence and complete initialization SQL/I/O budget absent",
                 "real source/epoch/session-id/scope linkage to R16 mount requires review; offline regression alone gives no end-to-end deployment proof",
                 "cleanup must cover every pre-listen/TLS/ready failure and owned-process stop; real shutdown behavior untested",
                 "final deployment snapshot and config digest binding, exact start/stop argv and independent approval pending"],
    "initialization_side_effects_to_freeze": ["exclusive fresh directories/ACL", "fresh state and TLS keys/certificate", "encrypted synthetic seed DB and two synthetic history rows", "Store constructor SQL/marker/storage configuration/log writes", "single TLS listener and ready/runtime metadata", "owned-process start/stop evidence"],
    "total_setup_SQL_budget": None, "real_initializations": 0,
    "stop_policy": "stop on existing root, source/owner/epoch mismatch, dependency failure or port conflict; no auto fallback/migration/retry",
    "rollback_policy": "future exact owned process/connection/listener only; preserve generated failure evidence; no global kill or recursive cleanup",
    "rollback_command": None, "P2_enabled": False})
write("P1A_COMMAND_LOCK.json", {**common, "phase": "P1a", "status": "BLOCKED_NO_LIVE_PROVIDER_OR_TARGET",
    "entrypoint_exists": True, "entrypoint": str(inspector), "entrypoint_sha256": sha(inspector),
    "supported_current_arguments": ["--metadata PATH", "--request PATH", "--mode offline (default)"],
    "R18_proposed_manifest_flag_supported": False,
    "current_entrypoint_capability": "single synthetic target/file provider only; not OS runtime attestation",
    "offline_argv_example_only": [PYTHON, "-B", str(inspector), "--metadata", str(OFFLINE / "d1a_002/test_metadata.json"), "--request", str(OFFLINE / "d1a_002/test_request.json"), "--mode", "offline"],
    "real_arguments_supported": False,
    "blockers": ["no actual running instance/PID/creation instant/epoch", "no approved bounded OS/runtime provider or verified endpoint owner", "fresh build/config digests and real DB/key reference association pending", "independent P1a approval pending"],
    "future_read_budget": {"nominated_targets": 1, "SQL": 0, "key": 0, "decrypt": 0, "RPC": 0, "output_bytes_max": 16384},
    "forbidden": ["all-process enumeration", "environment or raw argv", "key contents or key hash", "world state/ciphertext", "RPC", "configuration/ACL modifications"],
    "stop_policy": "reject missing/stale/mismatched target; no discovery fallback", "rollback_policy": "close owned metadata handle only; preserve fixed-code failure"})
write("P1B_COMMAND_LOCK.json", {**common, "phase": "P1b", "status": "DEFERRED_STATIC_CONTRACT_ONLY",
    "entrypoint_exists": False, "actual_entrypoint": None, "proposed_entrypoint": str(PROJECT / "scripts/inspect_h2_db_metadata.py"),
    "part_of_seven_target_lock": False, "actual_database_path": None,
    "database_candidate": DEPLOY + r"\authority\authority.db", "supported_current_arguments": [],
    "statements": ["PRAGMA user_version", "PRAGMA journal_mode"], "statement_budget": 2, "each_max": 1,
    "connection": {"maximum": 1, "mode": "ro", "uri": True, "immutable": False, "missing_file_creation": False, "rw_fallback": False},
    "world_SELECT": 0, "key": 0, "decrypt": 0, "ATTACH": False, "extensions": False, "migration": False,
    "checkpoint": False, "PRAGMA_assignment": False, "retries": 0,
    "blockers": ["P1a-based necessity undecided", "optional script deliberately outside current seven targets", "no actual DB identity or WAL/SHM/VFS side-effect budget", "independent P1b target/permission and exact argv pending"],
    "stop_policy": "stop if extra query, repair or write fallback is required", "rollback_policy": "close only owned ro connection; preserve failure evidence"})

cases = {c["id"]: c for c in new["details"] + old["details"]}
cost_map = {
    "C_config": ["D01", "D02", "D03", "D04", "D05"], "C_dependency_check": ["D06"],
    "C_bootstrap_preflight": ["D10", "D11"], "C_dormant_registration": ["D12", "D13"],
    "C_epoch_binding": ["D14", "D15"], "C_session_gate": ["A09", "A10", "A13", "A14", "A19"],
    "C_metadata_check": ["D16", "D17", "D18"], "C_cli_validation": ["D24"]}
costs = {k: {"case_ids": ids, "case_duration_sum_ns": sum(cases[x]["elapsed_ns"] for x in ids),
             "meaning": "inclusive case-duration proxy, not isolated component timing"} for k, ids in cost_map.items()}
costs["C_secret_scan"] = {"status": "CLEAN", "isolated_elapsed_ns": None, "measurement": "NOT_MEASURED; assertions/scans included in cases and driver"}
costs["C_offline_total"] = {"new_ns": new["elapsed_ns"], "regression_ns": old["elapsed_ns"], "sum_ns": new["elapsed_ns"] + old["elapsed_ns"], "meaning": "two final processes through result construction; trailing result/index I/O not isolated"}
write("D1A_COSTS.json", {"schema": "r19-costs/1", "categories": costs,
    "real_start_TLS_WAL_key_access_P1": "NOT_MEASURED", "public_vector_AES": "executed offline in D08; no isolated cryptographic benchmark"})
audit = load(RECORD / "D1A_SECURITY_AUDIT.json")
audit["direct_suite_commands"] = 5
audit.update(direct_suite_command_templates=2, completed_suite_invocations=4, early_preflight_failed_invocations=1,
    direct_suite_commands_meaning="all five test-process invocations including one preflight failure; command templates two",
    cost_details="D1A_COSTS.json", metadata_provider="OFFLINE_FILE_PROVIDER_ONLY", real_service_runtime_compatible=False)
write("D1A_SECURITY_AUDIT.json", audit)
runs = load(RECORD / "D1A_TEST_RUNS.json")
runs["early_failures"] = [{"path": str(OFFLINE / "preflight_001/EARLY_FAILURE.json"),
                           "sha256": sha(OFFLINE / "preflight_001/EARLY_FAILURE.json"), "tests_executed": 0}]
runs.update(total_process_invocations=5, completed_suite_invocations=4, final_acceptance_cases=68,
            repeated_suite_runs_are_not_additional_cases=True,
            invocation_record_caveat="regression requested venv executable; Python sys.orig_argv records base executable via Windows venv launcher; preflight independently checks sys.executable against approved venv")
write("D1A_TEST_RUNS.json", runs)

header = "日期：2026-11-11。范围：研究者本轮明确批准的成熟工程接线与离线验收。证据为本对话内模型辅助实现、实际执行与知情源码复核；外部独立验证待取得。\n\n"

write("01_IMPLEMENTATION_SUMMARY.md", "# G2-R19 实施摘要\n\n" + header + r"""
D1-A 七个逻辑文件目标已经落地，最终离线验收为 **68 PASS / 0 FAIL / 0 ERROR / 0 SKIP**，共 2056 条满足的检查。范围包含新增 D01–D24 和原 A01–A20、H01–H24。真实部署保持关闭，`INSTANCE_RUNNING=false`。

## 授权和参数

本轮授权来自用户提供的 G2-R19 原文，摘要固定在 `APPROVAL_RECEIPT.json`。R18 的候选文件继续保留原字节，参数确认作为独立来源读取。R18 尚未冻结新增测试 ID；D01–D24 由本轮按第八节先行登记，来源明确标为 R19。原 44 项测试分母和断言保持。

| 已确认参数 | 实际进入代码的边界 |
|---|---|
| 研究者兼研究/批准/数据保管 | 验证确认文档；真实姓名和 Windows SID 保持待确定 |
| 新根 `D:\毕业设计\h2_test_runtime\h2-authority-synth-001` | 固定精确路径及派生 DB/key/log/evidence 引用，离线执行仅保存引用 |
| base CPython 3.12.14 AMD64 | 固定解释器路径，新测试实际导入现有依赖 |
| `h2_*_001`、1 grant、1 QUEUED issue | 计数、来源、规范 digest、limit/reserved/spent 校验；无 attempt/release/result |
| `127.0.0.1:27443`、TLS、冲突停止 | 固定配置与替身决策，冲突仅尝试一次 |

参数确认文件内部仍保留历史 `D1_A=false`。本轮独立授权由 receipt 表达；读取配置时保持原确认文件的历史语义。文件内布尔量与实际执行授权分层使用。

## 七目标实物

| 目标 | 交付 | 验收范围 |
|---|---|---|
| `services.py` | 可选 `authority_runtime_context`、Store 后绑定、listener 回调及清理钩子 | AST 顺序检查，旧默认路径保留；服务模块未导入运行 |
| `dsat_authority_runtime.py` | 配置/路径、合成 seed、公开向量 codec、内存 Schema2、离线上下文、启动替身、元数据合同 | D01–D24 |
| `run_h2_authority_service.py` | 严格 `--manifest` 和 `--mode offline` | 输出离线预检计划；真实模式安全拒绝 |
| `inspect_h2_authority_metadata.py` | `--metadata`、`--request`、离线单目标 provider | 合成元数据验证；真实 OS provider 待补 |
| `test_dsat_authority_runtime.py` | 24 项新测试 | 137 条检查满足 |
| `run_dsat_authority_runtime_tests.py` | 两种 suite、拒绝钩子、日志、快照与哈希 | 直接分开调用；测试内子进程 0 |
| `tests/fixtures/dsat_authority_runtime/` | 确认配置副本、公开 AES 向量、合成哨兵 | 三文件摘要固定，公开输出仅记录摘要 |

精确路径、I/O、副作用、依赖和入口见 `D1A_FILE_LOCK.json`；函数行号见 `sources/CODE_SYMBOLS.json`。实际 diff 见 `sources/CODE.diff`。

## 已达到与后续责任

`PARAMETERS_CONFIRMED=true`；`DEPLOYMENT_PREPARED` 只指代码及离线预检准备。当前脚本尚无真实初始化、真实启动接纳或实际进程检查能力。`RuntimeContext.validate_service_entry` 对本轮可发行的离线上下文始终返回 `D1B_NOT_AUTHORIZED`。

因此，本轮具备可复核的离线启动桥和工程接口，D1-B 可执行性仍有代码与合同缺项。七目标文件落地与真实部署就绪分别登记。A/B/AB、T3、统一计数界、数学优先权和严格分离门保持原裁决；此次接线验收贡献属于成熟工程工作。
""")

write("02_BOOTSTRAP_AND_DORMANT_ACTIVATION.md", "# 启动桥、Dormant 与接纳边界\n\n" + header + r"""
## 实际离线顺序

`RuntimeConfig.from_confirmed` → 替身路径事实 → 依赖事实 → Schema2 事实 → `construct_store` 一次 → `bind_store` → 替身 listener 一次 → 封闭元数据 → `finally` 关闭拥有资源。D11 检查确切事件序列、构造次数、world 摘要保持及零 SQL/key/read。

规范 seed 单独构造。它保持一个 grant 和一个 QUEUED 请求，预算 limit=1、reserved=1、spent=0；请求 digest 使用既有 `normalized_request` 与 caller 规则。version=2、两条历史明确标为合成准备来源。D07 校验字段关系，D08 使用公开固定向量加密、在拥有的 `:memory:` SQLite 中建 Schema2 并往返核验。此过程没有连接实际 AuthorityStore。

未来真实顺序仍须保持：新根/ACL → 批准 manifest/源/依赖 → 新 state/TLS 材料 → 规范 seed 加密和新 Schema2 → 唯一 Store → Dormant 绑定 → Handler/TLS → runtime 元数据。真实总 SQL 与文件预算待冻结；R18 中预置库后构造约 7 次 SQL 只覆盖构造阶段，准备器费用另计。

## 两种绑定证据

1. 新 `RuntimeContext` 的离线 registry 捕获同一 Store/connection/lock，计注册次数并返回 `DORMANT_SOURCE_BOUND` 元数据；直接构造、重复绑定、替换 lock、关闭后复用均有拒绝检查。该 registry 保存配置、source digest、epoch 的离线关联，当前没有真实会话激活发行者。
2. 既有 R16 的 `mount_authority_host`、可信 ticket/peer 与进程内 `_SESSION_NAMESPACES` 继续保留。原 20 项 A1 和 24 项 H1 在原断言下通过，覆盖会话总量、并发、重放、issuer 重建和来源别名。新 `services.serve` 保留既有默认 ticket 路径。

二者在离线证据中分别验证。当前完整真实链尚需证明：可信 OS/启动发行者 → 实际 epoch/config/source → 授权会话 ID/读 scope → R16 mount ticket → 同一 Store → 总量槽。D14/D15 只验证离线字段与关闭状态，跨真实进程重启的旧授权失效需要未来实际 issuer/epoch 合同。该责任记录为 `SOURCE_OR_REFINEMENT_GAP`。

## 实际 services 钩子

`serve` 新增可选 keyword；给定 runtime context 时，接纳检查位于配置读取之前。当前离线上下文在此安全拒绝。现有 Store 构造之后绑定 context，再执行原 R16 mount 与 Handler 定义；listener/TLS 准备后上报引用，`serve_forever` 使用 finally 清理。

D23 通过 AST 校验上述位置与默认兼容性。该检查保证所核对的源码顺序，实际服务行为仍待 D1-B 验证。未来打开 live 路径前，还须扩展异常清理包络，使 Store 构造后至 TLS/ready/serve 前的所有失败均关闭拥有资源，并验证真实 `shutdown` 调用上下文；当前 `serve_forever` 外围 finally 的覆盖面有限。

## Dormant 和资源清理

离线上下文的 `issue_permit` 与 `read_state` 固定拒绝 P2；绑定操作自身零 SQL、零 key、零 world 修改、零 Provider、零 permit。D12/D13 及 D11 验证这些属性。默认挂载状态与未来 P2 接纳分别管理。

listener 替身返回后先登记为拥有资源，再校验 loopback/port/TLS，策略拒绝时仍进入清理。D20 覆盖端口冲突和非法地址，D21 覆盖 shutdown 抛异常后继续 server_close/connection.close。所有成功/失败为离线拥有对象；无真实进程停止操作。

## 元数据

P1a 当前接受一个精确请求（environment、PID、创建时点、epoch、source/config digests），通过 provider 读取单目标并验证封闭字段、大小和脱离内部引用。实际测试的 PID、epoch、source digest 均为合成替身值，`source_kind=OFFLINE_SIMULATION`，`INSTANCE_RUNNING=false`。

元数据中的相对 DB/key 路径只表示约定引用。它们没有证明实际文件存在、ACL 正确、进程拥有 endpoint 或真实源码匹配。P1a 真实 provider 与独立授权待补。

P1b 保持 R18 延期范围，仅提供两条固定 PRAGMA 的静态合同。D08 的公开内存 Schema2 验证和 P1b 实际运行核验分别登记。P1b 专用脚本未创建。
""")

write("03_ENVIRONMENT_ISOLATION_AND_SECURITY.md", "# 环境隔离与安全审计\n\n" + header + r"""
## 路径、导入与执行隔离

配置固定确认根、解释器、scope、源依据及所有派生路径，拒绝相对路径、UNC、ADS、越界路径与错误来源。离线 JSON 读取限于确认文件、新夹具子树和 R19 离线输出树；读取前检查现存祖先符号链接/重解析属性，限制 `.json` 和 1 MiB。D03–D05 验证拒绝路径和替身 reparse/root-existing 条件。

部署根路径在本轮仅作配置引用和最终存在性元数据检查。实际 OS 主体、ACL、单活、对抗并发路径替换及真实文件安全打开尚待 live 准入合同；离线替身事实的 `producer` 字符串只用于测试接口，不能承担生产证明。

runner 从获批解释器直接启动独立测试进程。新 crypto 测试与原 A17 无 crypto/services 断言隔离：新域导入现有 cryptography，回归域保持未导入。原测试模块、runner、锁和断言均保留原字节。此次未执行整仓 pytest、R07/R10/R12 全量回归或 native 实验。

Python audit hook 拒绝 socket、进程创建、真实 DB/key/private 文件、部署根访问及输出树外写入；SQLite 连接只接受受控 `:memory:`，新域上限 8，A1 域上限 32，H1 域拒绝新增连接。受控连接 authorizer 拒绝 ATTACH/DETACH 和扩展加载。新 suite 实际连接 1，回归实际连接 18。

隔离证据由 AST/import 检查、运行 audit hook、受控连接、调用计数和历史哈希共同组成。该审计覆盖本轮受控 Python 测试执行，外部原生绕过路径与真实系统安全证明另有责任。

## 真实副作用

| 项目 | 新域 | 回归域 |
|---|---:|---:|
| 内存 SQLite 连接 | 1 | 18 |
| 文件 SQLite、真实 key、private-file 访问 | 0 | 0 |
| socket/bind/TLS/RPC | 0 | 0 |
| 测试发起 subprocess | 0 | 0 |
| 部署根访问、输出树外写、禁止 SQL | 0 | 0 |
| services/storage/materials 模块实际导入 | 0 | 0 |

命令执行工具直接运行过 5 次测试进程：1 次预检失败与 4 次完整 suite。两种命令模板相互隔离；“子进程 0”专指测试代码自行生成的子进程。

## 合成秘密与日志

新 seed、handle、material 与哨兵均为专用合成输入；AES key/nonce 是公开测试向量，仅用于离线回归。公开结果只保留摘要、大小、固定拒绝码与受审元数据；输入夹具本身属于允许持有哨兵的来源。真实 state key/TLS key 生成、持久化和读取均为 0。

测试 stdout/details 完成哨兵检查；最终交付扫描覆盖报告、JSON、diff、日志和代码快照，结果见 `sources/DELIVERY_QA.json`。扫描结论仅针对已登记哨兵；生产数据访问继续保持 0。R18 确认配置副本 SHA 与原文件一致。

## 十项验收性质定位

| 性质 | 实际证据 | 范围 |
|---|---|---|
| P1 配置准确 | D01–D05、D22 | 确认参数与生效控制项 |
| P2 默认 Dormant | D10–D12、D22、A01 | 离线绑定，P2 固定拒绝 |
| P3 可信宿主绑定 | D11、D13、D23、A02–A04 | 新离线对象关联 + 原 R16 回归；live 链待补 |
| P4 会话总量 | A09/A10/A13/A14/A19、全部44项 | 原受控会话合同回归；生产接纳待核 |
| P5 实例隔离 | D03–D05、audit | 离线访问范围；OS/ACL 待核 |
| P6 权限分层 | D18、D22、D24、三份命令锁 | 本轮无 live 发行者 |
| P7 最小元数据 | D16–D18、D24 | 单合成目标，closed schema |
| P8 网络策略 | D19–D20、audit | 替身决策；真实 TLS 未测 |
| P9 秘密隔离 | D09、D16、D18、D24、sink scan | 合成哨兵与固定错误 |
| P10 真实访问0 | 两组 scope_audit、导入记录 | 本轮运行审计 |

安全状态限定为离线验证。真实服务启动、ACL、TLS、WAL、OS 元数据及真实 P1/P2 保持独立执行门。
""")

rows = []
for c in new["cases"]:
    detail = cases[c["id"]]
    spec = next(x for x in plan["new_cases"] if x["id"] == c["id"])
    rows.append(f"| {c['id']} | {spec['expected']} | {c['status']} | {len(detail['checks'])} | {detail['elapsed_ns']} |")
cost_rows = [f"| {k} | {', '.join(v['case_ids'])} | {v['case_duration_sum_ns']} |" for k, v in costs.items() if "case_ids" in v]
write("04_TEST_RESULTS.md", "# 实际测试与费用\n\n" + header + r"""
## 最终冻结结果

| suite | 项数 | PASS | FAIL | ERROR | SKIP | 满足的检查 |
|---|---:|---:|---:|---:|---:|---:|
| d1a_002 | 24 | 24 | 0 | 0 | 0 | 137 |
| regressions_002（A1 20 + H1 24） | 44 | 44 | 0 | 0 | 0 | 1919 |
| 最终总计 | 68 | 68 | 0 | 0 | 0 | 2056 |

检查数为测试内部布尔检查数量，存在重复断言。最终验收分母为 68；历史重复运行保存在记录中。

新增 ID 来自本轮 R19 清单，原计划的 NOT_RUN 是执行前冻结快照。实际结果在 `D1A_ACTUAL_RESULTS.json` 及两个最终 `RESULTS.json`。预期拒绝属于 PASS 条件；UNKNOWN、STAGING_READY_WITH_GAPS 等业务状态保持实际含义，未升级为完整数学/原生可用性。

## 准确复现命令

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_runtime_tests.py' --suite d1a
```

```powershell
& 'D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7\Scripts\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_runtime_tests.py' --suite regressions
```

这是原实际两种调用模板，单次执行对应一个独立进程。Windows venv launcher 使回归结果的 `sys.orig_argv` 首项显示 base Python；runner 的 preflight 同时以 `sys.executable` 校验获批 venv 路径。原始 argv 记录保留；这里区分工具请求的入口和解释器看到的启动向量。两次最终结果的六个源码 SHA 列表完全一致，并与当前源码一致。

## 所有轮次与修复

1. `preflight_001`：AST 源读取使用 Windows GBK 默认编码，产生 UnicodeDecodeError（byte 0xae，position 519），测试执行数 0。记录保存实际异常、归一化栈位置和六文件快照，原始完整控制台输出未另存。
2. 新 runner/test 的源码读取显式设为 UTF-8；`d1a_001` 24 PASS，`regressions_001` 44 PASS。
3. 知情代码复核后补强真实内存 Schema2/history 准备、策略拒绝 listener 的拥有资源关闭、严格 bool 类型及直接配置构造校验。此阶段属于审查补强，未发生测试 FAIL。
4. `d1a_002` 与 `regressions_002` 按最终源码重跑，取得上述 68 项结果。

完整 suite 调用 4 次，共重复执行 136 次测试用例；另有 1 次预检失败。两种模板共 5 次测试进程调用，测试自行派生进程 0。失败记录和前序结果均保留。

## 新增24项

| ID | 目标 | 结果 | 检查数 | case inclusive ns |
|---|---|---|---:|---:|
""" + "\n".join(rows) + r"""

## 依赖层级

实际新域：CPython 3.12.14 AMD64、cryptography 50.0.2、SQLite 3.53.1。D06 真实最小导入，D08/D09 执行公开向量 AES-GCM 加密/解密及错误向量拒绝。`METADATA_PRESENT` 和 `PACKAGE_IMPORTABLE` 已验证；完整真实 Authority 的 `RUNTIME_COMPATIBLE` 仍待验证。本轮依赖安装次数 0。

## 费用

最终新域总时段 1,170,382,800 ns；回归域 1,278,059,000 ns；合计 2,448,441,800 ns。计时包含 preflight、哈希和测试至结果构造；结果文件/运行索引尾部写入未单独计时。这些数值是本次离线运行成本。

以下分类用对应测试 detail 的时长求和，包含配置、断言及序列化等辅助工作；它们是覆盖用例的 inclusive 代理值，组件级独立计时保留 NOT_MEASURED。分类可能重叠，总计使用独立 suite 时段。

| 类别 | 用例 | case-duration sum ns |
|---|---|---:|
""" + "\n".join(cost_rows) + r"""

`C_secret_scan` 已完成 CLEAN 检查，独立计时 NOT_MEASURED。真实启动、TLS 握手、WAL、真实 AES-GCM key 文件访问和实际 P1 全部 NOT_MEASURED。D08 是公开向量密码学功能检查。更细费用和数据来源见 `D1A_COSTS.json`；注册数、槽位、模拟读取与预期业务拒绝保存在结果 details。
""")

write("05_CODE_DIFF_AND_INTEGRITY.md", "# 代码差异与历史完整性\n\n" + header + r"""
## 修改边界

本轮仅修改一个既有源文件 `src/auth_lifecycle/online_state/services.py`，新增五个 Python 文件和一个三文件 fixture 子树。完整路径以 `D1A_FILE_LOCK.json` 为准。研究目录中的报告与证据汇编工具仅用于文档取证。

| services.py | SHA-256 |
|---|---|
| 原始源码/原字节快照 | `7cc2321e2623c06848e13d106680887a01bd5635bf417127942a5bac1647be41` |
| 当前源码/最终两域测试版本 | `3bd6f5dd29b5327308c9aa08459e20a704724756ef4801acb4b31716d5a05d03` |

原字节存于 `sources/original/services.py.txt`。修改理由为可选 runtime context、Store 后绑定、listener 元数据和拥有资源清理钩子。原默认路径与 R16 ticket/mount/dispatch 逻辑保留。`sources/CODE.diff` 包含实际完整 diff 和五个新增文件；由于原行尾形式不同，services diff 可能显示较大替换范围，语义顺序另由 D23 AST 检查。

## 核验结果

执行前历史比较 **1441 行匹配**；执行后仅允许 `services.py` 对应的 **9 个来源比较行**映射到新 SHA，其余 **1432 行保持**。9 行来源于多份历史锁中重复引用，实际既有修改文件数为 1。每轮测试前后均核对历史来源和当前 code/input；原 services 快照保持原 SHA。

保护范围覆盖 R16 激活/读宿主模块、原 A1/H1 测试/runner/fixture、R12 B1、R10 S3-A、R07 S1/S2、Controller/Provider、旧 CLOSED/1、migration，以及 R18/参数确认资料。既有 SOURCE_LOCK 和失败日志保留原字节。最终历史复查见 `sources/DELIVERY_QA.json`。

## 新证据固定

- `SOURCE_LOCK.json`：本轮请求授权、代码/输入、最终结果、所有运行及早期失败摘要。
- `CODE_DIFF.json`：逐路径 SHA、行数、原快照、新 fixture 与保护结论。
- `sources/CODE_SYMBOLS.json`：通过 AST 提取的实际入口与行号。
- `D1A_TEST_RUNS.json`：四个完整 suite，加一条预检失败引用；runtime 原索引保持。
- `sources/*_PRE_DELIVERY.json`：本轮中间汇编记录原字节，用于核对最终补充字段。
- `sources/DELIVERY_QA.json`：最终报告/证据清单及摘要，排除自身哈希循环。

生成报告后再次核对六份最终源码，文档汇编未改变已验收工程版本。所有轮次的快照、日志和异常记录保留。哈希仅固定版本；外部独立验证范围仍待取得。
""")

write("06_FINAL_VERDICT_AND_NEXT_STEP.md", "# 最终裁决与唯一下一步\n\n" + header + r"""
**裁决：D1-A 七目标在获批离线范围内已实现并通过验收。实际部署仍有接纳与恢复合同缺项。** 当前交付提供离线预检、Dormant 对象绑定、原会话总量门兼容性证据与受限元数据入口。

## 状态

| 状态 | 裁决/证据范围 |
|---|---|
| PARAMETERS_CONFIRMED | TRUE，五项参数继承确认记录 |
| DEPLOYMENT_PREPARED | OFFLINE_ONLY，代码与离线计划 |
| INSTANCE_RUNNING | FALSE |
| D1A_IMPLEMENTED | 七目标文件实际落地，范围为 D1-A 离线合同 |
| D1A_BOOTSTRAP_VERIFIED_OFFLINE | D10/D11/D20/D21，替身生命周期 |
| D1A_DORMANT_ACTIVATION_VERIFIED | D11–D15，默认关闭且零读；真实激活待批 |
| D1A_ENVIRONMENT_ISOLATION_VERIFIED | D01–D05、D19/D20、运行 audit，离线范围 |
| D1A_SESSION_GATE_REGRESSION_PASSED | 原20 A1 +24 H1通过 |
| D1A_METADATA_INTERFACE_VERIFIED_OFFLINE | D16–D18/D24，合成单目标与P1b静态合同 |
| D1A_SYNTHETIC_TESTS_PASSED | 新24 PASS、137检查；全68 PASS |
| D1B_AUTHORIZATION_PENDING | execution gate 与 live 实现缺项同时保留 |
| P1A_NOT_AUTHORIZED / P1B_NOT_AUTHORIZED / P2_NOT_AUTHORIZED | TRUE |
| S3B2_NOT_AUTHORIZED / S5_NOT_AUTHORIZED | TRUE |
| SOURCE_OR_REFINEMENT_GAP | TRUE，真实源/OS/epoch/session接纳与typed O/o仍待核 |

## Q1–Q15

| 问题 | 明确回答 |
|---|---|
| Q1 七目标全部实际实现？ | 七个文件/子树目标全部落地，离线验收通过。真实发行者、真实初始化与OS检查仍为后续责任；当前 launcher 限 offline。 |
| Q2 五项参数正确进入？ | 是，D01–D05/D19/D22 对固定根、Python、合成scope、端口及确认边界校验。负责人以角色确认，真实SID待定。 |
| Q3 启动桥离线预检？ | 是，D11 检查顺序、唯一Store、替身listener和清理；无真实init/serve。 |
| Q4 Dormant默认关闭？ | 是，新context不发permit，P2读固定拒绝；原默认ticket路径保留。 |
| Q5 Store初始化/注册顺序？ | 离线construct一次后绑定；services AST核对构造→bind→Handler。真实Store未构造，pre-listen异常清理还须补齐。 |
| Q6 会话总量门保留？ | R16代码未改，44项回归通过，包含多permit、并发、重建和别名。新live接纳到同一会话的完整连接待审。 |
| Q7 P1a/P1b最小实现？ | P1a为合成文件provider、单目标和白名单入口；P1b按R18只交付两PRAGMA静态合同，专用脚本延期。 |
| Q8 真实访问副作用？ | 真实DB/key/service/socket/TLS/RPC/native为0；公开向量AES和内存SQLite实际执行。 |
| Q9 合成与生产隔离？ | 本轮审计和路径限制通过；部署根保持未创建。真实OS/ACL安全保证须另验。 |
| Q10 依赖可用层级？ | Python3.12.14 AMD64、crypto50.0.2实际导入和公开AES往返通过；PACKAGE_IMPORTABLE。Authority完整RUNTIME_COMPATIBLE待验证。 |
| Q11 实际总数？ | 最终68项：PASS68、FAIL0、ERROR0、SKIP0，2056检查。保留早期预检失败1次（测试0）和先前两轮通过结果。 |
| Q12 修改与来源范围？ | 1既有修改、5新Python、1fixture树；1441来源行中9个services映射获准，其余1432保持。 |
| Q13 D1-B还缺？ | live接纳/启动代码、OS身份ACL、单活epoch、完整源/配置绑定、新key/TLS/Schema2和I/O预算、全阶段清理及精确start/stop命令，独立授权。 |
| Q14 P1a/P1b还缺？ | P1a需实际PID/创建时点/epoch/endpoint/source与有界OS provider；P1b需先确认必要性、指定库身份/ro/WAL/SHM预算、独立脚本与许可。 |
| Q15 唯一最小下一步？ | 进行D1-B执行接纳与失败清理合同审定，先形成具体补丁范围和精确启动/停止预算。此次结束时保持部署关闭。 |

## 三份命令锁

`D1B_COMMAND_LOCK.json`、`P1A_COMMAND_LOCK.json`、`P1B_COMMAND_LOCK.json` 均为 `AUTHORIZED=false`、`EXECUTED=false`、`command_executable=false`，实际运行argv为空。

前两个文件列出现存脚本和真实支持的 offline 参数。R18 的 P1a `--manifest` 提案已由当前实际 `--metadata`/`--request` 接口取代；旧提案文件保留。P1b脚本延期。离线示例argv仅用于说明已测接口，后续应依据补齐后的live代码重新冻结真实命令。

## 唯一下一项工作及退出判断

**D1-B执行接纳与全阶段失败清理合同审定。** 使用本轮最终source lock明确最小live issuer/host provider、source/OS/epoch/session绑定、Store至listener的异常所有权、fresh key/TLS/seed/SQL/I/O预算和实际start/stop参数，产出受限补丁与执行申请。审定成功意味着可申请随后独立部署授权；出现身份、恢复或预算未闭合时，保留具体缺项并继续离线边界。

本轮没有提出候选算法或新的分离优势。A/B/AB贡献裁决沿用；实现资格继续由用户规定的严格分离门管理。生产typed O、S3-B2、S5、真实C_native分别保留独立门。COL2026主动检索暂停，FS23沿用延期。
""")

statuses = ["D1A_IMPLEMENTED", "D1A_BOOTSTRAP_VERIFIED_OFFLINE", "D1A_DORMANT_ACTIVATION_VERIFIED",
    "D1A_ENVIRONMENT_ISOLATION_VERIFIED", "D1A_SESSION_GATE_REGRESSION_PASSED",
    "D1A_METADATA_INTERFACE_VERIFIED_OFFLINE", "D1A_SYNTHETIC_TESTS_PASSED", "D1B_AUTHORIZATION_PENDING",
    "P1A_NOT_AUTHORIZED", "P1B_NOT_AUTHORIZED", "P2_NOT_AUTHORIZED", "S3B2_NOT_AUTHORIZED", "S5_NOT_AUTHORIZED", "SOURCE_OR_REFINEMENT_GAP"]
write("FINAL_STATUS.json", {"schema": "r19-final-status/1", "scope": "D1A_OFFLINE_ONLY",
    "PARAMETERS_CONFIRMED": True, "DEPLOYMENT_PREPARED": "OFFLINE_ONLY", "INSTANCE_RUNNING": False,
    "statuses": statuses, "counts": {"PASS": 68, "FAIL": 0, "ERROR": 0, "SKIP": 0}, "satisfied_checks": 2056,
    "live_deployment_executable": False, "live_metadata_provider_implemented": False,
    "next_action": "D1B_EXECUTION_ADMISSION_AND_ALL_PHASE_CLEANUP_CONTRACT_REVIEW"})

source_lock = load(RECORD / "SOURCE_LOCK.json")
source_lock.update(file_lock_sha256=sha(RECORD / "D1A_FILE_LOCK.json"),
    final_status="FINAL_STATUS.json", final_status_sha256=sha(RECORD / "FINAL_STATUS.json"),
    all_runs=runs["runs"], early_failures=runs["early_failures"],
    finalization_note="report/metadata finalization only; six tested source hashes unchanged",
    evidence_levels={"application_services": "AST_ONLY", "crypto": "PUBLIC_VECTOR_OFFLINE", "DB": "OWNED_MEMORY_ONLY", "P1a": "SYNTHETIC_PROVIDER_ONLY", "P1b": "STATIC_CONTRACT_ONLY", "deployment": "NOT_EXECUTED"})
write("SOURCE_LOCK.json", source_lock)
print(json.dumps({"reports_written": 6, "command_locks_written": 3, "code_unchanged": True, "final_cases": 68}))
