# 实际修复与原缺陷对应

补丁保存在 `sources/RUNNER.patch`；修改前后完整原字节分别在 `sources/RUNNER_BEFORE.py.txt` 与 `sources/RUNNER_AFTER.py.txt`。当前构建SHA：`245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f`。

| 原缺陷 | 本轮处理 |
|---|---|
| commit_case_record原668无条件Poison | 独立空token传入checkpoint；只采用匹配本次异常的封存分类，安全事前拒绝保留健康；未知继续Poison |
| safe_checkpoint原899无条件Poison | 相同按次分类；false返回和原failure记录保留 |
| io_write原1008前置截止进入1023Poison | 截止在write可能开始标记之前；同步拒绝绑定同一异常，完整扣费保持；原生write之后全部未知路径继续Poison |

## 精确分类

checkpoint在原RLock内要求精确内置空dict，为这次调用绑定owner、active状态、旧句柄/ledger、seq/head/bytes/identity、费用和计数。健康入口要求已有独占非关闭句柄、原确认前缀、无旧Poison、无用户缓冲、returned=confirmed=journal_bytes、charge>=confirmed。外部不可变性与原确认可信性继续作为原合同前提。

helper只在明确的同步拒绝位置记录异常对象的运行时身份及拒绝点。比较采用当前仍存活异常的id和当前token，未解析异常文字或errno。异常对象引用没有存进token。序列化块的Refusal还需满足纯预检控制位置、全部入口及边界条件；类型本身不足以取得健康资格。

中心分类再次确认同一row/stream、active owner、无write可能开始、完整或零扣费阶段、同一seq/head/bytes/identity及原尝试/返回/确认计数。其safe初值false，finally对不安全状态保持Poison。封存分类匹配原异常后，两个包装器才采用它。token结束后active=false；复用的非空token在入口即拒绝。

运行时audit中的attempt数值是候选checkpoint准入序号，未准入的多次拒绝可有同一候选数。可靠的当次匹配由新鲜私有token及异常身份承担，公开数值没有被当作跨运行全局唯一ID。

## 写入与提交边界

io_write在调用前先设置write可能开始。标记先于实际调用，边界附近中断可以保守记为可能已write。完整返回、flush、fsync以及checkpoint的seq/head/bytes推进和确认引用交付依次保留。原子发布在本源码中是fsync后的逻辑头推进；rename后端仍受原audit禁止。

第一份Journal创建、未知路径/身份、计费修改中断及所有未认证异常继续保守。短写、返回0、部分写、flush/fsync错误、write之后截止、头部或ACK间隙均保持Poison。成功路径的原ACK字段、结果身份和Hash链格式保持。

## 停止与费用

reserve继续执行原90/115截止，在同一事前分支拒绝已停止的非terminal工作，错误码沿用WORK_DEADLINE_OR_STOP。它防止失败后继续普通写入；begin_terminal只使用原收尾资格。已消费的字节、构造/terminal尝试、一次性输出路径及授权均保持，新增退款0。

安全事前拒绝仍然使整体验收失败：persistence_ok=false、incomplete/stop保持。Journal健康只保留满足原约束的独立既有收尾提交资格，原失败记录保持FAILED或UNKNOWN。

## 分类证据与失败记录

新增21字段有界原语audit，包括旧前缀、阶段、拒绝点、费用前后、尝试与确认计数、缓冲及未知上界。stage来自原evidence_text已验证、脱敏结果；不可得时使用明确的未验证标签，原异常责任继续保留。

失败的case记录及其原failure行附checkpoint_attempt；Journal账本保存last_checkpoint_failure。直接调用checkpoint失败时另增加一条分类failure行，原向外异常和上层原failure继续存在。这会增加失败证据压力，完整容量继续待证。新增诊断构造再失败时保留保守Poison及固定incomplete事实，原异常重新传播。

本轮没有创建测试代码。该维护结果只登记静态修复，未来真实运行结果继续NOT_RUN。
