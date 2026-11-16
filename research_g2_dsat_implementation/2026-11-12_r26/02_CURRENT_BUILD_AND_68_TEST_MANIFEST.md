# 当前构建与原68项身份

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助静态源码/计划/历史证据审查；本轮项目模块导入、工程修改、suite和测试子进程均为0。

**R26_CURRENT_BUILD_LOCKED / R26_68_TEST_MANIFEST_VERIFIED。** 静态身份核对通过，运行结果仍为NOT_RUN。

## 原始来源

| 组 | 数量 | 当前原测试 | 原计划 |
|---|---:|---|---|
| D1-A | 24 | tests/test_dsat_authority_runtime.py::D1ACases | R19/D1A_TEST_PLAN.json::new_cases |
| A1 | 20 | tests/test_dsat_authority_host_activation.py::ActivationCases | R15/H2_HOST_ACTIVATION_PLAN.json::A1.new_tests；R16实际验收 |
| H1 | 24 | tests/test_dsat_authority_read_host.py::H1Cases | R13/REAL_READONLY_TEST_PLAN.json::H1.cases；R14实际验收 |

68个ID完整、互异，未改变发现规则。3份测试源与其原R19/R16/R14实际执行记录的hash一致，10份fixture逐一与相应原始记录对应，3份计划原字节保持。每项原expected/spec、完整调用名、行号、文件hash、方法AST hash、显式断言/拒绝调用和fixture集均在`R26_68_TEST_MANIFEST.json`。方法之外的公共helper由完整测试文件SHA共同固定。

## 完整清单

| ID | 原callable | 原expected | 当前状态 |
|---|---|---|---|
| D01 | D1ACases.test_D01_confirmed_config | confirmed-config | NOT_RUN |
| D02 | D1ACases.test_D02_closed_types | missing/unknown-field | NOT_RUN |
| D03 | D1ACases.test_D03_path_boundary | root-path-isolation | NOT_RUN |
| D04 | D1ACases.test_D04_source_and_derived | derived-path-and-source | NOT_RUN |
| D05 | D1ACases.test_D05_reparse_and_existing | reparse-existing-root-facts | NOT_RUN |
| D06 | D1ACases.test_D06_dependency_import | dependency-import-and-gap | NOT_RUN |
| D07 | D1ACases.test_D07_seed_contract | canonical-synthetic-seed | NOT_RUN |
| D08 | D1ACases.test_D08_AES_memory | public-AES-memory-SQLite | NOT_RUN |
| D09 | D1ACases.test_D09_crypto_refusal | crypto-invalid-vector | NOT_RUN |
| D10 | D1ACases.test_D10_default_offline | strict-offline-launcher | NOT_RUN |
| D11 | D1ACases.test_D11_bootstrap_order | bootstrap-order-single-store | NOT_RUN |
| D12 | D1ACases.test_D12_dormant_zero_read | dormant-zero-read | NOT_RUN |
| D13 | D1ACases.test_D13_source_binding | opaque-source-binding | NOT_RUN |
| D14 | D1ACases.test_D14_epoch_config | epoch-config-source-binding | NOT_RUN |
| D15 | D1ACases.test_D15_closed_context | closed-stale-context | NOT_RUN |
| D16 | D1ACases.test_D16_metadata_closed | closed-detached-metadata | NOT_RUN |
| D17 | D1ACases.test_D17_one_target | one-target-metadata-provider | NOT_RUN |
| D18 | D1ACases.test_D18_P1_boundaries | P1-privilege-boundary | NOT_RUN |
| D19 | D1ACases.test_D19_network_policy | loopback-TLS-port-policy | NOT_RUN |
| D20 | D1ACases.test_D20_conflict_stop | port-conflict-no-fallback | NOT_RUN |
| D21 | D1ACases.test_D21_cleanup_fault | owned-cleanup-failure | NOT_RUN |
| D22 | D1ACases.test_D22_phase_gates | phase-authorization-gates | NOT_RUN |
| D23 | D1ACases.test_D23_services_AST | services-AST-compatibility | NOT_RUN |
| D24 | D1ACases.test_D24_CLI_sinks | CLI-and-secret-sinks | NOT_RUN |
| A01 | ActivationCases.test_A01_default_off | disabled registration no source I/O | NOT_RUN |
| A02 | ActivationCases.test_A02_binding | same Store/connection/lock and runtime binding | NOT_RUN |
| A03 | ActivationCases.test_A03_forgery | body flags/strings cannot issue Registration | NOT_RUN |
| A04 | ActivationCases.test_A04_synthetic_compatibility | H1 default compatibility and bare LOCAL refusal | NOT_RUN |
| A05 | ActivationCases.test_A05_authenticated_context | authenticated identity passed to the pure dispatch core; services hook AST checked | NOT_RUN |
| A06 | ActivationCases.test_A06_old_roles | legacy controller/Agent not granted metadata operation | NOT_RUN |
| A07 | ActivationCases.test_A07_scope_grant_rid | singleton tuple and predetermined grant/rid | NOT_RUN |
| A08 | ActivationCases.test_A08_current_permissions | current authorization-ticket version/expiry/withdrawal | NOT_RUN |
| A09 | ActivationCases.test_A09_multiple_permits | new permits and concurrent requests share one total slot | NOT_RUN |
| A10 | ActivationCases.test_A10_epoch | restart/epoch invalidates old P2 and prevents automatic rearm | NOT_RUN |
| A11 | ActivationCases.test_A11_SQL_codec_equivalence | bounded one-SELECT result and old codec equivalence | NOT_RUN |
| A12 | ActivationCases.test_A12_resource_schema_missing | oversize/missing row/unknown schema refuses before key | NOT_RUN |
| A13 | ActivationCases.test_A13_transaction_reentry | active transaction/reentrant callback refusal | NOT_RUN |
| A14 | ActivationCases.test_A14_fault_costs | telemetry/key/decode/return failure preserves incurred cost | NOT_RUN |
| A15 | ActivationCases.test_A15_no_DML | no DML or old call; legacy dispatch behavior preserved | NOT_RUN |
| A16 | ActivationCases.test_A16_secret_sinks | all public sinks secret-free | NOT_RUN |
| A17 | ActivationCases.test_A17_mount_position_AST | source mounting definitions do not launch services | NOT_RUN |
| A18 | ActivationCases.test_A18_client | minimal client strict argv and one call without Laboratory | NOT_RUN |
| A19 | ActivationCases.test_A19_budget_no_rearm | metadata/quota/log cost accounting and no rearm | NOT_RUN |
| A20 | ActivationCases.test_A20_egress_permissions | unknown/native gaps and final permission check preserved | NOT_RUN |
| H01 | H1Cases.test_H01_registration | exact object/producer/locator/epoch binding | NOT_RUN |
| H02 | H1Cases.test_H02_identity | deny before any source read; offline identity provider only | NOT_RUN |
| H03 | H1Cases.test_H03_body_flags | plain request flags cannot issue trusted permission | NOT_RUN |
| H04 | H1Cases.test_H04_expiry_withdrawal | current-policy denial before source read | NOT_RUN |
| H05 | H1Cases.test_H05_exact_tuple | account/audience/task/caller/generation all match | NOT_RUN |
| H06 | H1Cases.test_H06_account_audience | zero reads and no foreign output | NOT_RUN |
| H07 | H1Cases.test_H07_task_caller_generation | deny each mismatched component | NOT_RUN |
| H08 | H1Cases.test_H08_cartesian_scope | mixed tuple from two authorized tuples denied | NOT_RUN |
| H09 | H1Cases.test_H09_selectors | reject unsupported grant/rid/path/field extensions | NOT_RUN |
| H10 | H1Cases.test_H10_lock_parallel | policy then reentrant reader lock; one R12 read | NOT_RUN |
| H11 | H1Cases.test_H11_isolation_traps | constructor/old dispatcher/SQL/services/provider zero | NOT_RUN |
| H12 | H1Cases.test_H12_quota | one read plus6 headroom; no retry | NOT_RUN |
| H13 | H1Cases.test_H13_failure_ordering | fixed error without raw exception/locals/cause | NOT_RUN |
| H14 | H1Cases.test_H14_active_transaction | deny before source read; no commit/rollback | NOT_RUN |
| H15 | H1Cases.test_H15_schema | supported synthetic registration; unknown source refused; no migration | NOT_RUN |
| H16 | H1Cases.test_H16_private_decode | foreign synthetic values stay internal; no row/material exports | NOT_RUN |
| H17 | H1Cases.test_H17_sinks | canaries absent from response/error/repr/JSON/log/cache/serialization | NOT_RUN |
| H18 | H1Cases.test_H18_world_effects | world/a/events/budget unchanged; permit and read telemetry explicit | NOT_RUN |
| H19 | H1Cases.test_H19_revoke_order | policy lock orders denial versus historical authorized read | NOT_RUN |
| H20 | H1Cases.test_H20_replay | second use denied without source read | NOT_RUN |
| H21 | H1Cases.test_H21_source_substitution | same data/a under different reader or host epoch denied | NOT_RUN |
| H22 | H1Cases.test_H22_limits | whole failure without partial success; errors also bounded | NOT_RUN |
| H23 | H1Cases.test_H23_separate_rights | inactive business grant readable only under separate audit permission | NOT_RUN |
| H24 | H1Cases.test_H24_qualification_and_binding | math/native/global false; no S1/S2/S3 invocation; all stages costed | NOT_RUN |

原计划内部NOT_RUN是计划形成时事实；本轮外层current_execution_status统一NOT_RUN_IN_R26，historical_result的PASS带原文件/选择器/摘要独立保存。

## 静态接口判断

三个configure签名保持：D1A(plan,fixture_root,connect_memory,output)、A1(plan,fixture_root,connect_memory)、H1(plan,fixture_root)。核心调用、RuntimeContext、read host/activation、当前services AST钩子及CLI参数定义均可定位到当前版本。

D1A使用的runtime代码、A1会话门和H1纯宿主接口保持既有定义；services/launcher经历R19/R21/R22演进，这些已知历史差异采用当前R25目标版本，禁止加载旧源码来迁就旧锁。原测试源本身保持。

静态接口兼容带两项明确执行条件：A17之前不能导入D1A的cryptography；D24原路径合同需要受控文件投影。当前没有实现这两项条件的新入口，故不登记无条件可运行或回归PASS。

## 导入与运行时

A1/H1直接依赖标准库及纯protocol/read/read_host/activation模块，没有NetworkX调用路径。旧venv含NetworkX与历史runner的解释器约束，不等于这些68项实际需要流求解器。未来提议统一使用R25基准Python，保持依赖指纹，无需安装包。

A1必须保留原A17对services/storage/materials/cryptography未导入的断言。H1阶段采用FakeConnection，不开SQLite。之后才加载D1A，执行D06的真实已安装crypto导入及D08/D09公开向量内存运算。该进程装配顺序尚待新入口实现和独立静态审定；不能删sys.modules或用stub规避断言。
