# BF-static-2 静态变更记录

Material Passport：最终冻结修订 r4；2026-11-11；动态执行0。

## 实际文件

相对唯一可信 BF-static-1 的 lc03/src：

- 修改 guard.py：增加RANGE调度、受锁测试模式、共享核心接线、主账校准子预算、root原始证据重算、17个资格门负向检查、FORMAL强制再准入与calibrate-only路径。

- 新增 range_core.py：生产/合成共用范围事务、事实查重、一次派发/claim、局部前置扣减；变异仅在隔离校准模式启用。

- 新增 range_fixtures.py：34个固定job、真实worker崩溃、单worker并发、I/O适配器故障、原始语义记录及受限变异。

- 新增 range_evidence.py：独立原始账/屏障/身份/操作检查及真实全局journal流式核对。

- 五业务、run_batch.py与guard_probe.py保持逐字节相同。正式业务参数、D1-PBFT-SEAL/1.1和费用语义保持。

完整旧新摘要及full diff见evidence/SOURCE_DIFF_INDEX.json。新增文件以空参考生成完整add diff；旧BF原件完整保留。

## 静态审查修订链

candidate1：首个完整实现。
r1：旧C11钩子增加case、故障枚举和精确路径限制，FORMAL不能调用。
r2：隔离路径锚定OUT、拒绝目录符号链接；意外拒绝/恢复与非故障模糊终态阻断。
r3：safe/mutant使用统一安全断言；只有预注册违例集合可以作为变异命中。
r4：S6在真实RESERVE_REQUEST事件之后设置第二个request屏障，确保两个申请均已进入才允许PREP。独立检查两请求时序及屏障身份，避免退化为顺序测试。

候选源码/manifest/执行锁及摘要保存在freeze_candidate_*目录。全部修订间动态运行数0；最终执行许可只能绑定r4的实际hash。预算协议EXACT-RANGE/1保持，生产事实目录在新批次使用visits.bin.facts；历史账迁移0、退款0。

## 时序与资源

生产范围保持9个预留同步机会、claim另2个；编码、write/pwrite、fsync及最终持久完成继续计时。合成事件与操作、调用、短写副本均有计数/字节上限，真实全局主账先计费。RANGE硬限20000，共同校准300秒/100000保持；新增完成路径静态上界19229。性能与可运行性仍待动态验证。
