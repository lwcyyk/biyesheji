# R28最终裁决与唯一最小任务

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助实际离线调用与只读证据审查；独立外部核验待取得。本轮源码、Runner、测试及fixture修改均为0。

**本轮唯一入口调用失败，native退出1，68项全部NOT_RUN。D1B1离线合同继续部分实现。** 本轮额度已用完，代码修改0、自动重跑0，未执行第二次或额外54项。

| 状态 | 值/范围 |
|---|---|
| R28_STATIC_ADMISSION_PASSED / R28_SINGLE_SUITE_EXECUTED | TRUE，指18项事前核验及一次直接入口调用 |
| R28_68_REGRESSION_PASSED | FALSE |
| R28_A17_IMPORT_ORDER_VERIFIED / R28_D24_PROJECTION_VERIFIED | FALSE，未到达 |
| R28_OUTPUT_ISOLATION_VERIFIED | TRUE，本次实际失败输出范围 |
| R28_RESOURCE_BUDGET_SATISFIED / R28_HISTORY_INTEGRITY_VERIFIED | TRUE |
| R28_122_JOINT_EVIDENCE_ACCEPTED / D1B1_OFFLINE_CONTRACT_COMPLETE | FALSE |
| D1B1_PARTIAL_IMPLEMENTATION / SOURCE_OR_REFINEMENT_GAP | TRUE，gap为新Runner读取策略 |
| D1B2_AUTHORIZATION_PENDING / REAL_DEPLOYMENT_NOT_RUN | TRUE |
| P1A/P1B/P2/S3-B2/S5 | 继续未授权 |

| 问题 | 回答 |
|---|---|
| Q1 静态准入全部满足？ | 执行前18项冻结核验通过；动态暴露R27对cache读取路径的漏查，静态充分性存在缺口。 |
| Q2 严格只一次？ | 是，固定Runner调用1次并消耗唯一额度；用例实际执行0，剩余0。 |
| Q3 argv一致？ | 是，原RESULTS/包装argv逐项等于R27锁，native退出码1。 |
| Q4 68项统计？ | PASS0/FAIL0/ERROR0/SKIP0/BLOCKED0/NOT_RUN68；框架装配错误1单列。 |
| Q5 分组？ | A1 20、H1 24、D1-A24全部NOT_RUN，各组实际0。 |
| Q6 A17实际满足？ | A17未到达；入口初始模块检查通过且crypto未加载，不登记A17动态通过。 |
| Q7 D24与原文件？ | 投影未激活，目标副本0；两个原JSON及生产白名单源保持，D24动态结果NOT_RUN。 |
| Q8 输出隔离？ | 本次11个实际文件均在13白名单与新根内，失败路径隔离成立；成功D24路径未覆盖。 |
| Q9 T33链接？ | 4个名称的hash/底层身份/链接数/mode/属性均保持，只读核验，新结果无共享对象。 |
| Q10 资源预算？ | 已声明数值额度内：SQL/连接/子进程0，watchdog1，输出50090B，耗时约6.639s，RAM约37.39MiB；流程仍失败。 |
| Q11 与R25构建一致？ | 42工程源/24runtime及原测试fixture前后相同；R28实际模块载入止于装配，不能声称完整运行模块集合相等。 |
| Q12 联合条件满足？ | 未完成：54有效PASS＋68NOT_RUN，另有harness缺陷，原68历史证据未补入。 |
| Q13 可登记合同完成？ | 当前D1B1_PARTIAL_IMPLEMENTATION；缺读取策略修复后的当前68实测，以及A17/D24和联合条件核查。 |
| Q14 唯一下一项？ | 独立审批仅该Runner的精确cache探测/源码回退修复及新运行命名空间，完成静态冻结；再另行批准新68运行。 |

## 最小原因与责任

R27静态审查漏掉CPython get_code在-B模式仍会尝试get_data(bytecode_path)。新Runner用RuntimeError型READ_SCOPE_REFUSED拒绝该读取，标准导入器只对OSError型缓存不可用执行源码回退，因此在A1模块导入就终止。原始audit未记录具体被拒绝路径，这个证据字段缺项也需补齐。

这项遗漏属于测试入口装配层，当前没有任何原用例失败结论。R27原静态记录和源码锁保持，R28以实测指出覆盖不足。

## 唯一审批任务

详见sources/MINIMAL_RUNNER_FIX_REQUEST.json，当前approved=false。申请仅修订既有测试Runner，保持42工程源、3原测试、10fixture、生产reader/白名单和所有历史结果不动。

建议精确政策：仅当.pyc探测可反向绑定到某个已锁当前project .py文件时，记录“预期cache拒绝”，在读取cache字节前给出PermissionError/OSError，让固定CPython转读该源；其余未知读仍为致命READ_SCOPE_REFUSED。源文件继续执行SHA与exec/origin校验，不放行未锁bytecode，不清理或伪造sys.modules。该规则应覆盖原CLI helper的直接SourceFileLoader，不能只处理auth包的一种import形式。

建议后继静态材料使用2026-11-12_r29，后继验证根为该目录下verification_runs，run ID为r29_regression68_001；这些均为待独立批准的具体提案，本轮没有创建。

本轮R26root/run与槽位已经消费且必须原字节保留。下一实施申请同时只为新一次独立命名空间冻结OUTPUT/RUN_ID/LOGICAL与命令，不能重置、删除或覆盖当前失败run。原13路径与资源界沿用；任何扩大都另列审批。

该任务限代码修复和静态检查，动态测试0。完成后再请求新的唯一68项运行授权。若源码回退/输入绑定/日志范围仍有缺口，保留精确阻塞，停止执行。未来68真实通过并完成联合条件，才可能改变D1B1裁决；当前不进入D1-B2或真实P1/P2。
