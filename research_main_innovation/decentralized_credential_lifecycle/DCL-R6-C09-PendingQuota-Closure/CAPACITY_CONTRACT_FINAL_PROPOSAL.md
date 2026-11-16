# 配额与容量合同最终待批材料

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

当前有两类独立决定：**C09逻辑配额v2为PROPOSED_NOT_EFFECTIVE；完整容量合同为CAPACITY_CONTRACT_NOT_READY。** 容量新上限尚未选定，现行256行政原件/257 native成员守卫原字节保持。

可审阅的固定对象为[C09-PENDING-QUOTA-CONTRACT/2-DRAFT](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json)，版本PendingQuota-Closure/review-1，SHA-256 `7effe4e39e1eae665153bae4e16f7d2a20513a574fc26a4873ded5a81ef680ae`。该文件给出256次全部准入尝试、263主行、345148主预留、schema、类别去重、终态锁存、预付顺序、耗尽与崩溃烧额/关闭规则。

精化的独立元数据参数为cursor1198、更新522次；主日志/配额/首错/STOP/CLOSED及声明的失败staging子集≤350166，写量≤971216、durability尝试≤1316。它们由具体schema和持久顺序推导，作用域限于列明子集。完整关闭回收/MR/seal/admin字节仍UNRESOLVED；批准逻辑条款不构成完整关闭保留量、容量、实现或动态验收批准。

配额最终待批条款：

1. 只对一次全新、唯一batch/boot/handoff/执行锁/授权绑定生效；当前实际身份null。样例batch14仅作宽度占位，历史batch14保持CLOSED。
2. 256次独立预付在C09 controller/ready/counter冻结前完成；沿用原scalar持久预算核心，无MR额度转移，无观察阶段全局R变更。预付中断或重复初始化关闭原实例。
3. 七个生命周期/ACK类别位和分类ordinal在同一个Root保护cursor持久预扣，全部写者用同一稳定H锁；相同token永不重授额度。
4. 准入后检查/事实/分类失败也烧额。完整raw append/fsync后再写completion；终态锁存先于释放锁回收。第256条PENDING完整保留，第257次拒绝且不追加错误行。
5. 仅允许现行封闭scalar schema、明确宽度和固定编码；先验证输入再分配/编码。原始错误输入、部分行和失败staging保留，缺证据则UNKNOWN。
6. cursor预扣或完成模糊、短写、EIO、重启、外来cursor、过期/终态均关闭；不退款、不重建T0/预算/新免费窗口，不把摘要写入成功当作实际回收成功。
7. 单份首错与停止标记独立于主额度；原始ACK/commit/witness/预算/角色退出和原native/admin证据仍全部必需。完整关闭分区待未决字段闭合，容量准入保持关闭。
8. 现行停止/封存/行政/守卫/MR跨实例规则保持；后续静态维护和原生验收需新明确授权与完整增量重算。

可直接采用的独立决定文字：

> 批准逻辑草案：我批准上述版本及SHA-256的C09配额逻辑条款用于下一阶段静态维护申请，接受有限配额可能提前关闭合法延迟见证轨迹。完整关闭保留量和完整容量仍待闭合；本决定不授权实现、WSL、真实故障、T0/预算建立或F1/F4，MR规则仍单独待批。

> 拒绝或退修：我拒绝当前C09配额逻辑草案，或要求先闭合完整关闭保留量；现行源码、守卫和资源门继续保持。

完整容量最终审批应等待：所有raw单项/总量、部分/异常/staging集合、新增文件/访问Δ、ZIP格式和压缩膨胀、native/admin嵌套、manifest最大尺寸、读写/哈希/解压/内存/FD与期限、逐件原始oracle及原生异常关闭证据均具备完整参数。现阶段不建议填写一个更大的任意cap。[CONTRACT_APPROVAL_CHECKLIST.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/CONTRACT_APPROVAL_CHECKLIST.md)逐项列出阻断。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
