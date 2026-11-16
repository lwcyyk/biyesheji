# 完整资源资格重试计划（未执行）

2026-11-10。batch01到期且关闭，本轮新增校准0。下面是新批次候选矩阵，不是运行结果。前置条件为已认证的严格启动资源包络、可用的v3平台适配器、明确新授权和代码/输入/命令锁。任何前置未满足，保持RESOURCE_GATE_FAILED，不启动压力探针或F1/F4。

## 1. 冻结指标和输入

新批次额度独立列出，不继承旧剩余999973访问；不得扩过原允许的1000000访问、1800秒、4294967296字节树驻留集。建议先申请更小的诊断范围100000访问/300秒，正式F1/F4不在该诊断申请内。所有控制、WD、probe、子孙/辅助角色、失败/重放统一占新账。

保持原memory案例：96MiB测试Job、32MiB WS、最多16个16MiB Python块。另设原生诊断最多128MiB reserve、1MiB commit步，完整记录成功/失败；独立WS案例最多96MiB并逐页付费。初始/持续资源组约束必须先有效，不能因这些输入“看起来小”省去硬界。

## 2. 必需校准矩阵

|ID|原始输入与方法|必须取的证据|判定/停止条件|
|---|---|---|---|
|C00 前置环境|固定runtime/OS/Job或替代内核group、角色清单|从首个入口生效的资源策略、代码/镜像hash、全部角色最大并发|启动窗/metric映射未证则阻止所有后续|
|C01 ABI/setter|同版本、同结构类/长度；v1参数与20页min分别审查|sizeof/offsetof、页大小、flags、Set每次返回/LastError、明确JobID|单因素足以识别才升级根因，不能以v2成功替代|
|C02 正常结束|有限probe返回0|limits before/after、PID/creationtime、last-live/post-exit、完整日志/Job结束|所有所需记录齐且整树退出PASS|
|C03 额度边界|局部cap17及并发小quota|每grant前后全局/局部、拒第18、拒绝后未处理状态|超额展开发生即FAIL；不把global归零作测试|
|C04 提交诊断|原bytearray＋reserve/commit分离|持有时current/private/Peak各窗；Native失败码；同Job成员/峰值|MemoryError单独不足；内部机制未鉴别记INCONCLUSIVE|
|C05 WS窗口|created-suspended→before-limit→after-limit→before-Resume→逐页touch|每段current/Peak、配置flags、OS单位、起始历史峰值|不减历史peak造“新峰值”；额外驻留未证即不授整体资格|
|C06 整树|全部允许角色并发/替换，测试内核数量上限|完整成员、每角色硬界、外部启动策略、额外辅助进程处理|硬合成界≤4GiB且无未覆盖角色；采样仅辅助|
|C07 墙钟|短局部deadline的等待/繁忙/子孙|绝对clock、独立终止源、整个组全退出、退出后无继续处理|CPU时间限额不算墙钟；仍活FAIL|
|C08 异常/中断|probe非零、controller故障、WD故障分别注入|原错误、双向联停、计数与日志可读、全部句柄/子孙结束|缺WD不默许继续；部分证据丢失明确INCONCLUSIVE|
|C09 父/Job关闭|最后句柄关闭、临时查询handle持有|句柄所有者、Job终止链、稳定进程handle的退出信号|PID查不到或权限拒绝不能单独当死亡证明|
|C10 逃逸/额外角色|受控breakaway、未经注册创建、数量触顶|内核拒绝/全部归属、flags/creation API与停止事件|进程已逃逸运行则FAIL；仅纸面限制不通过|
|C11 重复启动|重复session/关闭/到期/错授权root|历史hash、拒绝前后state/counter相同|任何新免费窗口或覆盖失败即FAIL|
|C12 事务中断|PREPARED、写counter、fsync、COMMITTED/返回前故障|journal、计数/模糊预留、锁释放与后续拒绝|不确定额度不回收；需要人工复核不自动重放|

所有项记录输入、命令、预期、实际、OS计数、退出、完整资源、源码/输入/授权hash和PASS/FAIL/INCONCLUSIVE。任何关键FAIL/INCONCLUSIVE均阻止RESOURCE_GATE_PASS。原失败继续保持FAIL，不因新分类改为历史通过。

## 3. 执行顺序与账

先C00/ABI，再最小正常/额度，再内存/WS/整树；前面的证明/记录不齐不进入压力矩阵。随后完整故障/墙钟/逃逸/事务矩阵。新批主deadline从明确的平台启动点开始，覆盖所有校准及必要重放；不得按子case重置。新程序未获执行许可时所有actual字段null。

现有v3只提供静态观测、预留和拒绝路径，平台接线及完整dispatcher仍待实现。计划命令仅在这些条件成立后为：固定Python的`-I -S -B <newroot>/src/guard.py --plan <newroot>/inputs/calibration.json --qualify-first`。当前无合法可启动的新root/适配器，不能把该模板直接当作准入。

## 4. F1/F4恢复

诊断批次不包含正式模型。只有严格界证明、全部必要校准、版本/输入/权限及剩余额度全部成立，另按对应新授权顺序恢复F1→F4。F1/F4业务源码和冻结输入继续原版本；本轮不缩域、改不变量或同步改参考来制造通过。
