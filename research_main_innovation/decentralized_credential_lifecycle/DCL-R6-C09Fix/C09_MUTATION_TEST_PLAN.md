# C09正常、异常与竞态回归

Material Passport：34个冻结job，实际执行0；输入见evidence/c09_contract.json。

22个正常/异常基础见证，加6类变异各safe/mutant一对，共34。涵盖已提交后exit23、旧读后提交、见证/退出不同观察次序、receiver继续监督；缺收据、其他退出码、错误batch/boot/锁、未ready、写入中断、fsync失败、确认后receiver死、停止源丢失、预算异常、闭合后晚收据、超时、sender错误、版本错误、重复分类和window变化。

|变异|实际被测错误行为|独立应命中|
|---|---|---|
|use_old_snapshot|按先前快照错误关闭|H2|
|ignore_version|跳过收据版本条件|H1/H8|
|exit23_only|只用退出23判成功|H1|
|reopen_closed|闭合后重新构造成功条件|H4|
|duplicate_classification|同事件重复形成终态|H6|
|unknown_success|未知交接直接成功|H1|

冻结字段包括case_id、完整事件交错、期望终态、mutant类型与预期违规。原始每步记录输入摘要、binding、actor、时钟、全局预付和subject状态；oracle从冻结事件独立重建facts并核对，不能仅以PASS字段通过。

这些C09H job是合成状态/故障交错回归；真实socket确认、waitpid退出和pidfd顺序由下一批真实C09正常路径另取证。接收进程真实崩溃、物理fsync失败及对抗调度的更强认证不能由合成布尔事件单独取得；相应边界保持条件状态。无故障注入在本轮运行。

每job≤64事件，一步一次原预算visit，driver核验1次，root核验1次。完成路径≤34×65+1+34=2245，C09H硬界5000；同校准300秒。任何UNRUN/FAIL/缺件/未命中拒绝C09H资格；真正C09无法完成时禁止C10–C12与FORMAL。
