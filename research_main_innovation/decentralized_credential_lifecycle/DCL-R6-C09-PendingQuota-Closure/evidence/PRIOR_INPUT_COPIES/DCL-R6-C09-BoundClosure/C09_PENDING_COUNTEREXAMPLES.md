# 最小反例族与阻止条件

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


反例只需一个合法handoff和一个缺waitpid见证的窗口；任务数、批次数、模型访问额均无需增长。输入族X_n变化的是调度次序：同一sender已退出、相同durable ACK、相同Receiver和Root owner，让父协调者的见证发布推迟到n次Receiver观察之后。

轨迹骨架：COMMITTED/revision3 → EXIT_OBSERVED/revision4 → [witness=None；R=R0；PENDING；append+fsync]^n → 父waitpid/见证 → VERIFIED一次。每次自环仅新增原生记录，不推进classification_count/恢复次数，不消费Budget.visit或c09h_charge。日志增长至少n行及其正字节长度。

|具体阻止条件|实际后果|与族X_n的关系|
|---|---|---|
|pidfd尚未取得而sender已消失|G.identity(target)可能先拒绝|族要求sender活着时已装好fd|
|ACK/binding/ticket/counter不匹配|check_base/分类拒绝|族固定这些原件有效且不变|
|wrong witness退出码|FAILED，首次异常关闭|族在重复区间witness缺失，之后只允许真实23|
|CLOSED已存在|入口返回CLOSED，追加前终止|族在截止前无终态标记|
|handoff截止先到|check_base先拒绝；分类中跨界最多一条FAILED|族只取有正余量的有限前缀|
|HANDOFF_VERIFIED已持久化|observe_exit早返回，不再追加CHECK|族自环发生于成功分类之前|

原合同不能阻止X_n的原因：新handoff/成功分类/恢复唯一性没有给PENDING观察计数；持久fsync没有带入可靠最短耗时合同；就绪pidfd不会因一次PENDING返回而变为未就绪。

历史原件显示同源码17次PENDING自环，全部revision4、一个handoff id、该区间全局journal增量0。其日志SHA为db70519e1b47cdb42d1a852d5ad7db19096a616886450b3714a57ff231ac6675。完整原始字节和相关commit/witness/预算均仅复制到本轮研究目录用于复核，历史不改写。

本轮没有运行反例重放程序、替换Root调度、创建state/账/服务或修改日志。可重放描述由源码行、初始前提、分支序列、保持式和参数n组成；未来真实实验需独立动态授权，有限实例的实测也不能证明无限统一上界。

[完整反例规范](evidence/COUNTEREXAMPLE_FAMILY.json) · [原日志副本](evidence/HISTORICAL_RAW/CALDIAG_c09_events.jsonl) · [保持式统计](evidence/HISTORICAL_NATIVE_LOG_ACCOUNTING.json)。

族X_n须服从真实存储可用空间/表示边界；状态机自身不设n配额。固定schema低界1099字节给出具体参数n=30532的32MiB合同反例候选，整个调度/存储环境约束均在附件列出；实际可达规模与时延没有由17条历史观测推断。

[表示边界与量词范围](evidence/REPRESENTATION_LIMIT_CAVEAT.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
