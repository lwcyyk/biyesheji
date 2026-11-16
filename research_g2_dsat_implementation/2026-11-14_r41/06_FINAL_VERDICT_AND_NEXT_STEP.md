# R41最终裁决

**R41_MINIMAL_PATCH_IMPLEMENTED；R41_PREWRITE_POISON_STATICALLY_REPAIRED；R41_STATIC_PREFLIGHT_PASSED（局部维护静态范围）。**

实际只修改一个Runner的五个获准函数，并新增一个局部helper。当前SHA为 `245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f`。源码/fixture边界外保持，动态测试0，28项NOT_RUN，EXECUTION_AUTHORIZED=false。

## Q1—Q16

| 问题 | 回答 |
|---|---|
| Q1 五函数锁严格遵守？ | 是。五个原函数及一个获准有界helper，作用域外原字节和模块AST一致。前后摘要、原快照及diff齐备。 |
| Q2 三处无条件Poison修复？ | 是，原668/899包装器采用匹配的当次分类，原1008→1023路径在write前截止得到准确处理。 |
| Q3 能证明尚未发起受保护I/O？ | 对明确同步认证拒绝可以；fresh/active token、异常身份、旧健康前缀、计费和write可能开始边界共同证明。其他路径默认保守。metadata读取与payload-write分别记录。 |
| Q4 纯事前拒绝后健康保持？ | 在R40完整前提下静态成立；无法确认身份或边界时继续Poison。 |
| Q5 原前缀及Hash链保持？ | P1—P6静态论证成立；原ACK/独占可信是前提，动态摘要比较待执行。 |
| Q6 收尾预算仍可用？ | 错误的新Poison被避免；65536B保护差额保持，既有独立收尾仍逐项受115秒、32/8320次、scope/身份和实际包适配约束。 |
| Q7 错误退款、虚假提交、重复费用？ | 新增退款/重开/重试0；已扣费前置截止保留全费，拒绝结果为FAILED/UNKNOWN；原同记录早退和费用单调保持。 |
| Q8 短写/flush/fsync/未知保守？ | 是。may-write在调用前设置；这些错误及头部/ACK间隙保持Poison，原全费保留。动态回归待执行。 |
| Q9 前置截止保持时间？ | 是。90/115/120常量与原时间条件保持，并拒绝已停止的普通工作。没有延长期限。 |
| Q10 H2或持久授权受影响？ | 原字节保持；相关源与控制路径没有修改。原授权消费、epoch、重放门保持独立责任。 |
| Q11 2MiB可达路径/证据规模变化？ | cap/物理调用点保持；新增21字段audit，直接失败新增分类行，一些原收尾路径恢复可达，故完整失败联合负载需更新，仍UNPROVEN。 |
| Q12 28项保持？ | 原ID、输入、预期、预算及全部原字段逐行保留，新增实现定位。28个NOT_RUN，测试代码未创建。 |
| Q13 历史与源码边界？ | 继承2433项加R40的24文件，共2457项结尾核对，唯一允许变化为Runner；历史锁保留原字节。最终明细见HISTORY_AFTER。 |
| Q14 动态测试0？ | 是。Runner/抽取项目函数执行、动态导入、SQLite、测试子进程、网络及真实服务操作均0。 |
| Q15 能申请28项验证？ | 可以提出独立申请，包含专用驱动建立与条件满足后的一次运行。拟120秒/2MiB、9文件999424B、重跑0、子进程/线程/SQLite/网络/密钥0；驱动SHA、完整负载、argv及整运行时内存锁形成前保持执行关闭。 |
| Q16 G2/G3/G4缺口？ | 完整正常/异常L0需求UNKNOWN；G3九组原义务未闭合；G4七变化/五缺失保持。旧命令禁用，新构建完整回归及D1-B1验收各有独立责任。 |

## 状态边界

R41_FIVE_FUNCTION_SCOPE_VERIFIED、R41_PREWRITE_REJECTION_CLASSIFIED、R41_COMMITTED_PREFIX_STATICALLY_PRESERVED、R41_TERMINAL_RESERVATION_STATICALLY_PRESERVED、R41_UNCERTAIN_IO_FAIL_CLOSED_PRESERVED及R41_BUDGET_INVARIANTS_STATICALLY_VERIFIED成立，范围限冻结模型和源码证明。

G2_COMPLETE_L0_CAPACITY_UNPROVEN、G3_BOUNDED_CONTRACT_PARTIALLY_APPROVED、G4_RUNTIME_ORIGIN_ADMISSION_PENDING及D1B1_PARTIAL_IMPLEMENTATION继续保持。D1-B2、P1a、P1b、P2、S3-B2、S5继续未授权。原54/68/122历史证据没有被改成当前构建同版通过。

本次维护没有提出新算法机制或原创贡献主张。原场景研究与严格分离实现门继续沿用。

## 唯一下一步

独立审定 `R41_NEXT_AUTHORIZATION_REQUEST.json`：建立专用28项离线验证驱动，锁定实际源码/argv/完整资源与证据负载，再按明确独立授权至多执行一次。

这项需要新的授权，依据是用户R41第一、九节明确禁止动态测试及本轮创建动态测试代码。R41已经完成获准补丁、静态证明、测试oracle和资源申请；当前实际执行权限仍为false。

成功将提供当前补丁28项局部故障行为和清理的动态证据；失败将定位具体分类/前缀/费用责任并保留证据，原一次运行额度消费规则保持。两种结果都分别管理G2/G3/G4及完整回归准入。

当前对话内知情模型辅助工程实现与静态审查；外部独立核验待取得。
