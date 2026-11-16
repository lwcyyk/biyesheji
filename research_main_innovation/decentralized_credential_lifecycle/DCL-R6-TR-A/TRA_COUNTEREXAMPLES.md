# 首次失败、具体环境差异与后续边界

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

**首次关键失败是BC_ARTIFACT_DRIFT，发生在artifact_check的运行时字节核验，早于实例准备和一次认领。**

|原路径|冻结SHA-256|实际SHA-256|
|---|---|---|
|/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2|c20a2dc8917c755f02b94049356320fe1f62ac7d9f8994731f807d9df39302da|5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f|
|/usr/lib/x86_64-linux-gnu/libc.so.6|3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf|755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a|
|/usr/lib/x86_64-linux-gnu/libm.so.6|fce00b6f25f459cf4ae0b7fae4257909a1a8a86f9149e7c029a5d617baf1ccd0|5dcc4d25466e29ca390ed6fabb371c69b65dff6fa4e91c34561057a020d6994a|

当前加载器/libc/libm均为Root所有的普通系统文件；Python、源码和冻结输入保持。包日志记录glibc8.9→8.12，与当前3项运行库变化同时形成环境资格缺口。没有将来源猜成代码缺陷、攻击或某个更新执行者；本轮安装操作0。

冻结预检在首个loader差异即拒绝；后续1241对象/3差异统计属于独立只读故障诊断。未通过改hash、放宽规则、使用旧RESOURCE_GATE_PASS或重跑避开失败。原TerminalRead语义仍未动态验收。

最小后续工作是运行时适配与资格审查：保存8.12实际字节/包来源，评估CPY312/AS4及原TCB假设影响，更新新独立版本的runtime闭包和依赖摘要，再新身份/执行锁申请有限验收。当前r1保持冻结；不直接把3个hash换成现值后继续本批。

[首错](evidence/FIRST_FAILURE.json) · [完整环境差异](evidence/RUNTIME_DRIFT_AUDIT.json) · [后续具体范围](NEXT_PLATFORM_ADMISSION_REQUEST.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
