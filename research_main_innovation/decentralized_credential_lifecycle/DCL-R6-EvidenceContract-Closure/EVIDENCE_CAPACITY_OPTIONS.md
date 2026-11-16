# C1与C2工程方案比较

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


|项目|C1：版本化数量上限|C2：标准归档分段|
|---|---|---|
|证据字节|逐原件保留现行路径与hash|逐原件保留，根manifest绑定有序完整分段及各自清单|
|完整集合|整包成员集合＝完整manifest集合|分段ID集合必须与根manifest完全相等，任一缺段/重复/额外段拒绝|
|独立oracle|读取全部原件及每个包成员|读取所有分段和全部成员，跨段路径唯一、分段hash/全局原件hash都匹配|
|资源|固定总字节和总工作量，修改count须批准|逐段界与所有段总量/工作量同时限制，避免分段放大总许可|
|当前工程变动|原格式容量字段、相应读验/导出界及版本绑定|需要新的分段组织合同/清单与读验接线，当前合同尚未承认|
|当前建议|优先；数量包络已有，字节/工作量仍待闭合|备选标准工程方案；当前只做规则比较|

C2可采用现成标准ZIP/tar＋版本化根manifest，属于COVERED_BY_G。当前严格分离实例仍为0；没有新封装代码、研究候选机制或未经批准的分段承认实现。

C2的完整性证明以集合等式为核心：根清单确定必需原件集合E和完整分段集合S；每段的hash/成员清单与根绑定，oracle验证分段索引双射及所有原件hash；缺任一s∈S或任一e∈E均拒绝。只提交部分段无法形成该等式。包内包的嵌套不解除最内层逐件验证责任。

分段只改变组织方式，不能约束当前未计量的C09日志生成，也不能把每段32MiB误读为总量扩容；当前raw字节与封存期限缺口对C1/C2共同适用。新count/分段规则均需另行明确批准后才可能实施。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
