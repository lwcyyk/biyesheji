# 容量修复方案与选择边界

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


|方案|所需条件|当前判断|
|---|---|---|
|A：原格式版本化容量|完整生产者最大清单、精确N与元数据开销、固定字节/内存/时间证明；旧版本规则保留|优先采用；合同提案已形成，生产N尚未选定|
|B：无损表示优化|合同承认逐件恢复/身份/hash等价，并有独立逐件oracle与重放证明|通用ZIP/tar/内容寻址清单已覆盖；COVERED_BY_G|

选A的可审查变更面为容量合同、相关reader/exporter/host边界及版本绑定。当前完整数量最大值尚未闭合；新admin_files/native_members字段均null、runtime_enabled=false。旧64份源及上限保持冻结。

方案B属于现成通用归档方法G的覆盖范围。当前没有可构造的严格分离实例，未引入新编码、归并机制或候选协议实现。新增代码承担通用验证基础设施维护与专项测试职责。

必要修订程序：闭合261个站点的可达输出基数，包括失败/临时文件/动态退出记录；把校准与模型完整最大清单和字节上界绑定scope；明确host14侧件与各manifest/native ZIP嵌套开销；选择精确版本化N；保留旧配置可复核；最后集成和重新冻结。当前只读组件验证的cap313明确标为最低见证测试边界，未成为生产提案N。

[版本化合同提案](proposals/CAPACITY_CONTRACT_REVISION.json) · [完整约束证明](EVIDENCE_COUNT_CONTRADICTION.md)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
