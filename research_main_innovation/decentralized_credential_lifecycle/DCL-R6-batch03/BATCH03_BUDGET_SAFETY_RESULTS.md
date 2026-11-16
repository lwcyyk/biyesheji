# batch03预算安全结果
Material Passport：静态能力复核完成；动态S1–S9=NOT_EXERCISED；RESOURCE_EVIDENCE_INCOMPLETE。

## 每项实际状态
|性质|冻结路径覆盖差异|动态证据|
|---|---|---|
|S1 精确预留前崩溃|C07在case单信用入口后退出，缺专项精确范围夹具|NOT_EXERCISED|
|S2 PREPARED后崩溃|C11为单信用局部镜像；全局fault被代码拒绝|NOT_EXERCISED|
|S3 持久完成至派发前崩溃|缺range registry/final-intent/dispatch缝隙夹具|NOT_EXERCISED|
|S4 派发/claim后崩溃及恢复|缺CLAIMED缝隙与部分消费恢复夹具|NOT_EXERCISED|
|S5 同task重试/冲突|三个child各reserve一次，缺重试和冲突测试|NOT_EXERCISED|
|S6 并发range/claim|C05测试普通visit/mirror，缺双range/双claim|NOT_EXERCISED|
|S7 短写/fsync失败|C11局部单信用故障覆盖有限；缺range registry/claim和实际fsync失败夹具|NOT_EXERCISED|
|S8 批关闭/过期后局部信用与恢复|C06/C12涉及时间/状态谓词，缺LocalCredits失效使用夹具|NOT_EXERCISED|
|S9 N+1访问前置拒绝|C02最多N、C03恰N、C04一次；缺一次额外访问|NOT_EXERCISED|

固定源码仍有上限、身份、事务与恢复拒绝分支，其静态条件证明继续有效；本表仅表示本次要求的机器证据缺口。当前用户§5要求缺失故障能力时保持资源门关闭，源码中的PASS分支和静态证明没有转成动态验收。

全局账尚未初始化：实际counter读数=N/A；本轮发放预留0、payload访问0、退款0。R=A+U等式及R≤B没有新的运行样本；旧batch02 R=32191原件继续保持。未创建测试镜像、发放lease、注入失败或丢弃事务残片。

正式准入当前只能核验13个case receipt；用户要求的关键UNKNOWN排除条件尚无独立range证据门。evidence/ADMISSION_COUNTEREXAMPLE.json给出静态控制流见证：假定所有旧case为PASS而S9动态证据缺失，当前分支仍可进入FORMAL。该见证未执行，也未归类为F1/F4协议反例。
