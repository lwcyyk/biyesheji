# 逐字段单行字节上界

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

**单行结论为CONDITIONAL_PROVED。** [c09_handoff.py:15](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:15)使用sort_keys、逗号/冒号紧凑分隔、默认ensure_ascii=True；[c09_handoff.py:83](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:83)追加LF后UTF-8编码。以下长度均含1字节LF。完整模板、骨架和调整量见[RECORD_BYTE_ALGEBRA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/RECORD_BYTE_ALGEBRA.json)；新实例尚未签发，batch14只作宽度样例。

|字段族|最大编码长度|条件与编码责任|
|---|---:|---|
|event/verdict/阶段|固定枚举；最长stage22|取现行六种stage、ACK和EXIT_CLASSIFICATION_CHECK；额外键需重审|
|batch_id / execution_mode|7 / 27|冻结ASCII白名单；未来身份超长时重算|
|handoff_id、commit摘要、window四摘要|各64|SHA-256小写hex；引号/字段键已计骨架|
|boot_id（identity/window/stamp）|各36|规范UUID，源kernel及绑定；白名单ASCII|
|PID / start_ticks|10 / 20|正pid_t32、u64十进制；布尔冒充整数需拒绝|
|utc_ns|20|受审signed64十进制；符号已计|
|T0/deadline/stop_at/boottime/now/expires|各25|有限binary64 JSON宽度；未来须在编码前验证数值/类型和宽度|
|revision|1|范围1至6；重复PENDING保持4|
|facts布尔|每项≤5|13个固定布尔键，true4/false5；无递归容器|
|witness|null4或退出整数≤11|直接parent waitstatus来源；类型和范围需固定|
|task_id、错误码/errno、systemd原文、traceback引用、校验头|主行中均无此字段|这些对象位于commit/resources、socket错误流、MR或停止/封存族；独立计量|

公共数值调整：PID从1变10增加9；start_ticks增加19；utc_ns增加19；window三浮点＋boottime共4项各增加24，合计143。分类再含now/expires两浮点，增加48。模板骨架已包括所有字段名、引号、括号、嵌套、逗号/冒号和LF。

|类别|骨架与调整|上界bytes|
|---|---|---:|
|缺witness、durable ACK真实的PENDING|1107＋143＋48|1298|
|通用分类schema|对全部13布尔取false、witness取11字符退出整数后重算|1318|
|合同分类预留槽|沿用既有1322，较通用schema代数多4|1322|
|stage最大|805＋143|948|
|ACK|885＋143|1028|

六种stage逐项上界为943、939、943、948、942、933，总5648；合同仍按6×948=5688预留，保留40字节余量。1298仅用于正常缺见证自环，其他标量事实组合一律按1322；本轮把这一证明范围写明，容量安全无需依赖1298覆盖全部异常分支。

字符串白名单中没有引号、反斜线、控制字符、换行和非ASCII，因此字符长度等于UTF-8长度。若未来接纳任意Unicode，JSON ensure_ascii=True每code point最多12个ASCII字节，当前表须重新计算。通用event(kind,**data)本身可接任意键值，未施加schema/字宽检查；封闭调用者与ABI前提为当前证明边界。

主机研究脚本仅按JSON语法统计固定模板与最大十进制宽度，未导入运行源码；主机Python版本不构成原生3.12兼容验收。未来实现须把全部profile检查置于不受限序列化分配之前，完成原生宽度和异常回归，才能取得源码约束证明。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
