# 局部静态准入与28项冻结

R41_STATIC_PREFLIGHT_PASSED=true，范围限本轮维护补丁的源码、状态转换、前缀及存储不变量。完整68执行准入继续受G2/G3/G4及旧禁用命令阻断，EXECUTION_AUTHORIZED=false。

静态证据包括：五函数/一helper的精确AST和原字节差异，23条受控调用路径证明，P1—P6前缀论证，原常量/调用点保持，21字段audit的910B条件原始界，以及原异常/测试身份完整保留。仅检查源码标记是否出现的做法未被用作正确性证据。

R41_28_TEST_MANIFEST逐行保留R40全部原字段，另加当前源SHA、静态路径定位和原行规范化摘要。原计划SHA为 `b257f15e92acf7fba59ad289cab79e70f77635155f63f33acfddabd739157d69`。ID仍为R40-PC-T01…T28，执行状态28个NOT_RUN。

| 测试 | 当前代码责任 |
|---|---|
| T01—T04 | 容量拒绝、独立收尾、旧前缀、无虚假提交 |
| T05—T09 | write未知、零短写、部分write、flush、fsync |
| T10—T12 | 逻辑头更新与ACK间隙、多个拒绝及记录重入 |
| T13—T17 | reserve/io前置截止、terminal时限、receipt不足、二次失败 |
| T18—T21 | 旧Poison、正常链、L0失败安全、原存储预算 |
| T22—T24 | 身份冲突、未知/过期token、账本更新中断 |
| T25—T28 | ACK后日志失败、授权单调、预检拒绝、读取/清理 |

本轮新建测试驱动0，原测试/fixture修改0，动态执行0，静态审查没有被统计为PASS用例。

## 后续独立申请

R41_NEXT_AUTHORIZATION_REQUEST提出下一轮两个有顺序的部分：先获准建立一个专用28项离线驱动并冻结实际源码/命令/资源；其静态门满足且有独立运行批准后，至多启动一次专项，自动重跑0。

拟新增驱动为 `D:\毕业设计\auth-lifecycle\tests\test_dsat_runner_poison_classification.py`，目前文件尚未创建。拟解释器为当前固定Python，文件SHA已写入申请；这只绑定拟用单元验证域，未改变原G4结论。新驱动的普通文件入口及argv仅是接口提案，可执行命令锁仍待实际驱动源形成。

提议输出根 `D:\毕业设计\research_g2_dsat_implementation\2026-11-14_r42_poison28\verification_runs\poison28_001`，目标已存在即停。拟9对象cap合计999424B，覆盖结果、日志、manifest、来源、状态、资源、失败证据及至多一份65536B native小Journal；总逻辑存储仍以2MiB为上限。数据域内存请求32MiB仅指测试自有活跃数据，整解释器RSS及监测合同仍须源级冻结。

拟预算：一次28项、重跑0、120秒、额外线程0、测试子进程0、SQLite/SQL0、网络0、密钥/TLS0；可选单个自有小Journal成功检查须精确纳入读写/句柄账本。故障适配器验证属于离线单元语义，真实崩溃与native故障持久性没有自动获得验证资格。

现阶段仍缺新驱动实际字节/SHA、完整运行证据正常/异常需求证书、实际argv/输出/whole-runtime内存和逐文件读写锁。申请保留这些门，当前dynamic_packet_ready=false。该状态不妨碍局部补丁静态验收，也不提前开放下一轮运行。
