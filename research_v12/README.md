# v1.2：结构性算法深化与动态核心传递

研究开发交付，不是正式 H-A/H-B/H-AB 统计验收。入口为同目录 Word 报告、FORMAL.md、AUDIT.md、LITERATURE.md 和 runs/。旧 auth-lifecycle、v1.0、v1.1 不修改；本目录只以只读方式导入旧有限模型、解释器和强基线。

## 算法入口

- `independent.py`：独立 R-J12、完整 Post、策略/反驳重放及下界检查器。无候选求解导入。
- `kernel.py`：有限候选图与完整统一控制策略求解。
- `oracle.py`：实际完整原生 B 调用、配置后残余停止 BFS、同一精确缓存与动态证书复用。
- `joint.py`：统一联合策略类及可持续增量 session，八组合只切换 A4/B4/AB3。
- `a4.py`：任务相对价值单元、并集检查和反例单例精化。
- `b4.py`：安全路径类压缩、全局字典序展开与独立压缩检查。B4-1 非零接口分解只诊断/回退，尚未实现。
- `smt_joint.py`：独立有限图 Z3 编码及 push/pop；旧 `smt_comparator.py` 为直接 B Optimize 对照。

## 可复现命令（PowerShell）

在 `D:\毕业设计` 运行。每次输出目录必须是新目录，脚本拒绝覆盖。

```powershell
$py = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B research_v12\test_ab3.py --out runs\ab3_replay
& $py -B research_v12\test_structures.py --out runs\structure_replay
& $py -B research_v12\verify_corpus.py --out runs\transfer_replay
& $py -B research_v12\run_study.py --out runs\reproduce_all
& $py -B research_v12\analyze.py runs\reproduce_all
& $py -B research_v12\dynamic_schedule.py --out runs\dynamic_replay
& $py -B research_v12\run_fuzz.py --out runs\fuzz_replay
& $py -B research_v12\analyze.py runs\fuzz_replay
& $py -B research_v12\preserve.py --verify
```

Python 3.12 随工作区运行时提供；Z3 4.15.4.0 在旧研究 `.deps`，bootstrap.py 明确路径。原项目自身只需标准库。报告生成额外使用 python-docx、pypdf、PDFium 和本地 Word 渲染；不属于算法依赖。未取得 Git 提交，不伪造；版本由 registry、SOURCE_MANIFEST.json 和旧材料 SHA256 标识。

## 测量口径

每个主运行由独立 worker 执行，4 个逻辑 CPU 亲和性、8GiB 进程内存限制，30s 共享周期，32s 父进程含启动超时。记录编译、源到表审计、完整子问题、缓存、证书、最终策略/交付检查及评分；额外记录包含 Python 启动的 process_inclusive_seconds。不是专用机器，也不是原生产品准入/网络请求时延验收。

J 为最坏全分支总请求 Q；B 为原生(G,配置字典序)。完整 B 的单世界建议不作为跨世界执行许可。失败、界内拒绝和 UNKNOWN 保留在分母；模型评分器对未完成使用 budget+1 的既定开发惩罚，不把此值称为现实开销。未执行原生请求。

当前接入仍有一个实质限制：单世界完整B结果只影响控制动作遍历顺序，统一控制层继续完整求解，因此存在重复计算。八组合真实测到了B的计算成本，但不证明B结果已带来更强的联合剪枝或配置决策增量，也不保证联合策略优先最小化G。

dev01 保留原测量和源码快照；其 Z3 行附加即时后继查询，因此不与单根墙钟作优势比较。dev02 使用同单根口径；dynamic01 使用各方法完全相同的根/即时 probe 后继序列，单独评价增量。随机结构增补是开发诊断，不是留出确认集。

证书成本细分另见 `runs/certificate_cost01/result.json` 和 `measure_certificates.py`：记录控制搜索加证书构建、独立核验、完整Post和传递总时长。构建时间包含搜索，不冒称纯序列化时间；这一诊断不参与配对优势计算。

## 证据与限制

读取历史 5393 个可读文件建立哈希基线；运行中的 Keycloak H2 数据库被占用，明确列在 historical_unreadable.json，未声称已核验。完整源/数据哈希与结果核对见交付清单。失败尝试保留，不删除或回填成功。

交付核对发现旧 `.runtime/l1/processes.json` 与起始哈希不同；本轮未写入此路径，来源未归因，也没有恢复或覆盖。其余5392个可读文件相符。全体可读文件检查明确为false，非运行时源码/报告/历史结果检查为true；不掩盖这一差异。

AB3 proof replay、A4 value abstraction、B4 类压缩都提供给通用等价对照。不能把同一机制不同名字当独立创新。H-S 仍是依赖完整模型与真实服务符合性的条件命题；其他三项正式假设未运行。密码学 v1.1 第13—19节保留；来源/成功域/泄漏与端到端收益门槛尚未满足，不扩 MPC。
