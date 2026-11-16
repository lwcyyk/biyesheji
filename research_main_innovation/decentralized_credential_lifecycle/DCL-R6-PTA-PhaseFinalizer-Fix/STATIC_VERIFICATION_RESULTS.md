# 静态验证结果与动态缺口

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

|核验|结果|
|---|---|
|55项冻结源码/输入|最终摘要DAG完整；36 Linux程序＋2 host程序＋17输入；未来Linux53项|
|38程序文法/compile|PASS_STATIC；主机CPython3.14执行AST/内存compile，3.12文法解析；目标角色执行0|
|控制流/生命周期|28项AST断言，Root发布/读锁、顺序/身份/WORK、终态/异常传播和入口均通过|
|实际导入关系|完整AST边清单；本地模块均部署，其他为stdlib；受控入口5项通过，原生3.12导入UNRUN|
|保护语义|13文件字节保持、57成员归一AST保持、整个RootIPC归一AST相同；slice字节保持|
|原PT64与新增PF48|64jobs保持；48唯一ID/8mutant/固定帧界/独立参考及允许违规集合静态核验；实际套件/oracle执行0|
|资源|PF完成817/硬1152，正常A完成1907/硬2689，完整硬66770≤100000；全链时间UNRESOLVED|
|历史|预先锁6825份；原PTA/PreT0/MRA/Manager包逐流核验；旧native成功与旧post失败均保留|
|本轮Native动作|WSL0、服务/Launcher0、T0/R=null、正式授权回执0|

PF-G1=PARTIAL：源码交错缺陷有具体反例，历史精确读取值和OR分支继续UNKNOWN。PF-G2/3/4=CONDITIONAL_PASS：静态义务与主机探针满足相应范围，真实并发/模块/IO/退出/封存待动态。PF-G5=PASS_STATIC：最小申请、回归、访问界和锁齐备；不赋予动态执行资格。

静态验证器曾因历史审查标签boot/gate18/MR与文件名别名不同而读取boot.py失败，修正别名映射后完成检查；该过程没有导入或运行目标。受控导入使用单独保留的stub和cwd诱饵，入口main始终未调用。source-only目录无pyc。

[最终机器结果](evidence/STATIC_RESULT.json) · [静态断言](evidence/SYNTAX_AND_CONTROL_FLOW_CHECK.json) · [导入探针](evidence/CONTROLLED_IMPORT_RESULTS.json) · [资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
