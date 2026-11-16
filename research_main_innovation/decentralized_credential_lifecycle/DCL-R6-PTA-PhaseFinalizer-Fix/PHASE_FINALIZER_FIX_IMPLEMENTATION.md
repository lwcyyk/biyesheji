# 有限修复实现与差异说明

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

**最终冻结r3：55份文件、38份程序；新增3份Linux程序及1份输入。** 新程序为admin_postexit、phase_finalizer_regression及其独立oracle。所有新实现均在独立pf01，原pt01和batch11保持原样。

|变更位置|理由与行为|
|---|---|
|startup_lifecycle|同一Root锁覆盖phase写入/公开点发布和Root读取；加入seq/record digest与具体异常操作数；WORK身份检查；终态只读seal分支|
|admin_postexit（新增）|stdlib bootstrap；先设置单次行政AS/时间界，再验证固定源/摘要并载入模块，保持-I -S -B|
|Native post|当前回执/activation/boot绑定；已登记角色核验与有界收敛；native结果先单独保存；native完成也独立行政归档|
|host/startup_finalize|原始双流结束后审计/打包；失败独立记录；保持已审查native状态；重复包/manifest和路径/字节界核验|
|host/windows_entry、boot_continuity、guard授权接口|绑定新增测试合同及显式PF批准位；入口/预检在发放前拒绝缺授权|
|guard C00分支|原PT64之后同步执行PF48，然后按最小A关闭；不进入MR/C09或模型|
|phase_finalizer_regression/oracle/contract|48项（40safe＋8mutant），同一原预算计费；oracle独立分类实际差异，再检查声明的预期违规和伴随集合|
|部署/输入/执行锁|新pf01/batch12-r3身份、53项Linux部署、精确新入口、摘要DAG与访问硬界；执行计划元数据对齐实际顺序|

13份关键程序逐字节相同，包括五业务、预算range_core、probe、S驱动、runner、C00Ready、C09、MR驱动/oracle。57项原预算/Boot/门18/MR/RootIPC/C09成员AST在必要namespace归一后保持；整个RootIPC AST另核一致。原slice文件字节相同，UID/GID/ACL语义、sealed、一次认领、MR管理审查和C09持久ACK语义保持。

r1候选与r2候选的完整源码/锁/检查结果均保留。r2补齐当前回执和已登记角色绑定；最终r3将1GiB/单次30秒行政界移至bootstrap之前，并继承剩余期限。最终r3是唯一下一申请目标，候选版本均无动态执行。

[全部源码路径/前后SHA](evidence/FILE_DIFF_INDEX.json) · [完整diff](evidence/FULL_DIFF.patch) · [版本记录](evidence/REVISION_LOG.json) · [最终55项锁](evidence/STATIC_WORKSPACE_LOCK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
