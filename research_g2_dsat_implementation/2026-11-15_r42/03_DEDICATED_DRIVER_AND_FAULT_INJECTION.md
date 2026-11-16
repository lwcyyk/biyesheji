# 专用驱动规格与独立故障观察

本轮形成规格，驱动代码尚未创建。拟文件沿用R41：`D:\毕业设计\auth-lifecycle\tests\test_dsat_runner_poison_classification.py`。R42_DRIVER_IMPLEMENTATION_LOCK给出唯一文件、拟函数/类范围和28项方法映射，R42_FAULT_INJECTION_MATRIX给出每项触发及变体。

## 调用真实实现

未来独立批准后，先核对Runner字节，再以非main别名加载。使用object.__new__建立合成State，完整列出使用的属性，保持真实State.checkpoint、commit_case_record、safe_checkpoint、reserve_bytes、io_write和helper的函数对象。

禁止将Poison分类或预算状态机抄入驱动作为oracle。入口entry/main/controls/State.__init__/preflight/connect_memory/load_group及原68/54模块不在测试装配调用范围。真实Authority、Controller、Provider、RPC、凭据生命周期和许可生成保持关闭。

## 外部边界适配

- ObservedFileIO先记录实际方法进入，再按单次计划接受k字节、返回或抛错；write、flush、fsync、close分别记事件。返回0、接受后抛错和可靠返回k分别管理。
- clock、os/fsync、path/metadata采用目标模块专属facade，driver真实wall clock和输出写入器保持独立。修改共享stdlib模块会污染自身取证，规格要求避免这种装配。
- PublicationProbeState只在实际journal_sequence/head/bytes赋值前后抛错，不实现另一份checkpoint。T11在bytes已实际赋值后抛错，使头一致但确认引用未交付。
- ObservedLedger只观察真实字段存储并在指定点中断，保留实际已发生的部分更新；不会替目标设置预期费用或Poison。
- SyntheticPath依托标准路径词法及独立内存元数据；原checked、metadata及descriptor_metadata规则由真实实现执行。源外资源访问直接成为装配失败。

每个故障需要证据证明“已armed、在指定边界触发、次数符合计划”。未触发、错位或被宽泛异常处理吞掉，都属于装配失败。全部facade改动在finally恢复；恢复或所有权不明时保持不完整。

## 独立oracle

实际write次数取自适配器进入日志，已接受字节取自观察缓冲；它们独立于目标的WRITE_ATTEMPTED计数和prewrite_safe标记。may-write标记先于实际调用，因此“目标不确定而观察到0次调用”是合法边界场景，不能直接推断目标应当保持健康。

前缀检查同时比较全部旧字节、记录数量/顺序/内容、seq/previous/hash链及已收到确认。独立JSON、SHA-256和无损codec核对用于证据读取；Hash相等不替代可信旧ACK前提。当前静态种子已做规范化摘要和解码摘要检查，见STATIC_PREFIX_SEED_CERTIFICATE，这项数据核验没有运行状态转换。

费用采用直接等式：事前拒绝c'=c；扣费后write前拒绝c'=c+B且确认不变；部分写保留c+B，实际接受k和可靠返回k分别观察；成功两个包费用c+B1+B2、序号+2，收到两个真实引用。全过程各阶段成本另外求和，任何已花费用不重置。

## 内存模型与物理持久性

必须区分虚拟流进入、真实native调用和驱动取证文件写入。所有强制故障均可以在受控模型观察，证明范围限实际受测代码在该边界模型中的行为。

R41只提出至多一个65536B自有native成功Journal。是否采用此可选伴随模式及完整调用/文件预算尚待批准。native成功样本也无法证明断电稳定性、磁盘失败或Windows任意中断。物理性质保持外部证据责任。

## 源码静态审查门

驱动存在后才能逐项检查调用图、AST和副作用路径。当前只有未来函数合同，STATIC_VERIFIED=false；实际文件Hash=null，未声称不存在的代码已能拦截真实服务。下一阶段需要对所有import/open/write/exec/线程/子进程/网络/SQLite路径作源码级核对，并逐项绑定28个调用点及取证位置。
