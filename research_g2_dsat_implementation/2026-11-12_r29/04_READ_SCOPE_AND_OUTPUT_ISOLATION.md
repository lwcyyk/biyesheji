# 读写边界与新命名空间

日期：2026-11-12（Asia/Shanghai）。过程：本对话内知情模型辅助单文件修复、AST/源码/元数据/哈希审查。本轮Runner与测试模块未导入，--help和所有测试未执行，SQL/key/测试进程资源0；外部独立核验待取得。

## 允许集合

- 原42+5工程/测试辅助源与当前Runner：固定SHA，只读。
- 原3测试、10fixture、3原计划及历史保护清单：具体路径/摘要，只读。
- 原24runtime及新394运行时代码文件：具体已锁对象，原整个Python目录放行已移除。
- R29实际运行需要的控制JSON：仅command.control_pins和命令锁等明确文件。
- 新输出：只允许13个固定名字；receipt只读，其余x/xb创建。

运行时清单逐项用途见R29_RUNTIME_READ_MANIFEST；完整静态边在sources/RUNTIME_IMPORT_GRAPH.json。未解析的记录含被导入属性、builtin/frozen及平台/惰性替代项，不产生新读取许可；没有在静态审查中识别到目标导入链新增必须放行的数据或真实配置文件。未来任何实际未知读取仍应记录并失败，禁止现场自扩。

## A17与D24互不借权

阶段继续A1→H1→D1-A，新增policy使用errno/importlib纯路径辅助，metadata预检不加载crypto或测试。import/exec屏障和原A17保持，D1A继续延迟装配。

D24三类ProjectionFile/ProjectionRead/D24Projection及OrderedSuite的AST与a9版本相同；两个JSON原路径/hash、有限逻辑名、只在D24激活与finally恢复完全保留，仅目标随新run迁移。缓存分支只处理.pyc且反推.py，无法授权额外JSON。生产读取白名单hash保持。

## 新输出

根：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r29\verification_runs`。

run：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r29\verification_runs\r29_regression68_001`。

R26已消费run和R28报告全部只读，控制schema/aliases/结果schema迁移为R29。原hardlink T33四个路径只读例外保持，既不属于cache源，也不属于新output。

目录上限2、文件13、总逻辑2MiB、每日志64KiB保持。所有stdout/stderr、receipt、计费、错误、A17/D24/来源记录和索引仍在原13名字结构中；新增cache审计塞入原ledger/results，不增加文件。

本轮只创建交付根，verification_runs、receipt和RESULTS不存在。以后需独立批准，再准备唯一receipt及新根；Runner拒绝既有槽位/run和旧目录fallback。

## 预算

仍为未来一次68、自动重跑0、main入口120秒；内存SQLite A1≤32/H1=0/D1A≤8，总≤40、同时≤32；execute≤376、rollback≤1。子进程、文件DB、真实服务/RPC、新secret key/TLS和原生文件锁上限0。Python线程总12/峰值6保持。

新394代码文件hash验证和源码回退成本计入原120秒，不提前断言已运行成本；原RAM数值硬额未设，保持实测/未知规则。原2MiB输出guard继续约束新增审计，满额即失败。当前运行资源实际0。

这份Python审计维持原可信本机/库/完整文件系统模型；它不新增对恶意管理员、不可中断OS I/O或C库全部内部I/O的证明。存储失败时保留部分文件、原/次异常和非零退出，不借旧目录写回。
