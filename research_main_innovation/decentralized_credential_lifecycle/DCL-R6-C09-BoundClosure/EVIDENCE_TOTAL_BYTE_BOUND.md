# 完整证据字节闭包审查

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


当前B_total不能闭合；**CAPACITY_CONTRACT_NOT_READY**。给C09一份未生效的有限草案，不会给现行生产者或其他文件自动带来总量限制。

|类别|已经具备的界|界的性质/剩余责任|
|---|---|---|
|C09 native|条件行1298/1322；当前次数无上界|生成总量缺口已构造可达反例；草案预留345148仍未生效|
|授权/身份输入|operator_bytes对单份原文/回执读取设4MiB；source/input locks为冻结已知字节|不把可重算报告或元数据排除出完整保留集合；动态输入实际hash/长度还需当批绑定|
|C00–C12固定二进制|counter24、C03共享16MiB|源码固定布局/ftruncate，可证明；C05/C11局部journal需独立计量|
|全局预算journal|健康完成全域最多2,000,000行；条件line-none/请求界见机器表|生成器没有对应总字节检查；range oracle只接受≤200000行/16KiB行，terminal另要求总32MiB/32KiB行|
|预算journal条件精算|旧完整校准≤15,441,008字节；全1m窗口≤471,876,988字节|固定请求/ABI条件，三次批预付节省36990事务；该有限粗界仍可超过32MiB接受界，不证明实际模型会耗尽预算|
|Boot/RootIPC/MR/PT/PF/TR/RA|Root JSON读取4MiB、BC读取128KiB；MR事件写32KiB|读取接受cap与生成界分开；事件/元数据/异常链及聚合仍需逐schema证明|
|readiness原生诊断|602×131072=78905344字节|写前单条cap与sample300＋confirm1；组合cap高于32MiB，未证明该极端同时可达|
|C09H34|204事件＋34oracle；事件reader上限64KiB|writer/reader义务不同，按接受cap估计事件部分13369344；独立oracle输出另计|
|S1–S9|48个实际actor×256事件×4096=50331648；原子metadata16KiB|可证明写cap乘积，尚非紧上界；registry/journal/snapshot/临时件/派生结果另计|
|门18及ledger聚合|固定18门、ledger18子例及两轮重查|有限数量，内容/派生证明/日志的完整字节界仍需绑定|
|stdout/stderr/系统查询/退出错误|部分MR查询结果接受8192/2048（capture后检查）；first_error部分字段截2048|G._run PIPE未设统一输出字节界；traceback/SEAL_ERROR repr/外部journal导出未被这些局部界覆盖|
|F1/F4输入/状态/策略/反例|196个固定输入/输出/摘要槽位|未得出各状态/树/trace/report编码上界，文件数量和访问上限不足以代替字节证明|
|native/admin/manifest|各接受32MiB、manifest4MiB|接受集合有限；native构建前G.digest整文件读、admin嵌套ZIP/host原始流仍要生成/聚合证明|

分层公式：U_native=R_raw＋M_native；Z_native=ΣD(s_i)＋H_native；行政导出=R_raw＋M_native＋Z_native；行政归档未压缩量再加host流、4份source lock和M_admin。ZIP本身的文件字节及包内原件都需计入行政总量，不能因包内包而忽略复制成本。

现有32MiB是拒绝/失败边界。源码没有因此在生成时为每个必要对象分配总量；超限可能使封存无法完成，真实裁决应保留FAIL/UNKNOWN和首次失败，不能删除原始记录或缩短反例以制造成功。

[全对象分类表](evidence/TOTAL_BYTE_FAMILY_AUDIT.json) · [journal条件推导](evidence/GLOBAL_JOURNAL_BYTE_MODEL.json) · [ZIP代数](evidence/ZIP_BOUND_ALGEBRA.json)。

在额外off_t64/封闭只追加假设下，可列极粗的单文件表示界2^63−1与raw4450文件乘积41044005564003752341150；它未覆盖外部host控制文件的另外ABI，也未证明原件能装入一个合法包。本文的UNRESOLVED指资源兼容的可用字节/工作量界，不将物理表示空间描述为无限。

[表示边界与量词范围](evidence/REPRESENTATION_LIMIT_CAVEAT.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
