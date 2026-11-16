# 关闭记录数和字节保留量证明

## Material Passport

DCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。

总体裁决：**CLOSE_RESERVE_UNRESOLVED**。与上轮CLOSE_RESERVE_BOUND_UNRESOLVED含义一致。部分源码结构次数与单条schema已得到CONDITIONAL_PROVED；完整N_close,max和B_close,max仍未具备统一数值。

在冻结完整scope、单次activation、最多一次C09恢复、Restart=no、首个异常展开退出、无外加Root调用的前提下，继承并复核：A_abort≤2×3＋2×4＋2=16；S_stop_tree≤16＋4＋1＋1＋1=23；Q_seal≤7。两个phase的正常/异常waitpid写入互斥，合计W≤2。源码依据为[src/guard.py:1140](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:1140)、[src/guard.py:1222](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:1222)、[src/boot_continuity.py:415](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/boot_continuity.py:415)和[src/manager_recovery.py:317](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:317)；完整展开见[CLOSE_COUNT_DERIVATION.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/CLOSE_COUNT_DERIVATION.json)。

每次abort在stop_tree之外至多7项数据生产尝试：STOP、first_failure、external_closing、ABORTING、fallback CLOSED、close_attempt一行、final close_state。stop_tree至多一份CLOSED/stop_event及一份stop_result。于是：

\[N_{core,attempt}\le7A+2S+W+H=160+H.\]

H单独表示budget-halt的额外STOP写入。在C09 idle/no-new-budget的关闭前缀中H=0；完整scope的每角色halt工作量还需单独核算。该160界排除主日志/配额元数据、MR正常审查、payload退出遥测、native/admin证据。核心唯一稳定路径的保守界为5个固定异常目标＋2S＋close_attempts文件1＋W=54，失败staging另列；**160是生产尝试数，54是局部路径数，两者都未作为完整关闭配额获批。**

单个健康Receiver异常关闭分支，STOP和首错均未存在时，可发生8次核心数据发布，落在7个核心路径：STOP、first、external_closing、ABORTING、CLOSED、stop_result、attempt、final state；ABORTING/final共用路径。父waitpid、退出证明、封存/行政材料继续另计。因此“仅两个停止标记”不足以枚举必需关闭证据。

定义R为reason的JSON编码token长度（含引号），T为适用异常类名token上界且T≥4，B为三份预算hash/size/error映射长度，E为关闭异常repr的编码token长度，V_j为12个cgroup值token长度。[CLOSE_SCHEMA_BYTE_ALGEBRA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/CLOSE_SCHEMA_BYTE_ALGEBRA.json)给出固定键、JSON标点/缩进、数值及逐字段代数：

|记录|编码|条件上界bytes|
|---|---|---:|
|STOP/CLOSED/stop_event|RootIPC indent2 UTF-8，无LF|144＋R；reason为43字节ASCII时189|
|ABORTING|BC compact ensure_ascii=True，无LF|237|
|external_closing|BC compact，无LF|260|
|first_failure|BC compact；error≤2048 code points|25054＋R＋T＋B|
|cleanup state（分支并集包络）|BC compact|997＋11T＋B|
|close_attempt行|相同compact＋LF|998＋11T＋B|
|stop_result|RootIPC indent2|1151＋E＋ΣV_j|
|正常waitpid含完整当前source state|RootIPC indent2|1223|
|异常reap waitpid|RootIPC indent2|565|

B≤69＋3max(106,29＋T)。error的2048字符经ensure_ascii=True最坏占24576内容字节，加引号24578；notes持久化前保守计10项，角色分支取字段并集、至多2个目标。实际成功/失败分支通常更小。

数值前提明确保留：PID正int32≤10、ticks/dev/inode/预算长度u64≤20、clock_ns signed64≤20、binary64 JSON≤25、waitstatus≤11；stat_ctime_ns采用signed64秒换算纳秒的29字符界，单独处理其与clock_ns的表示差异。冻结namespace、source state键集合及无额外Root字段为条件，当前没有新宽度验证实现。

核心字节公式为：

\[W_{core}\le A(L_{STOP}+L_{first}+260+237+L_{fallback}+L_{cleanup}+1+L_{cleanup})+S(L_{marker}+L_{result})+W\max(1223,565)+W_{budgetSTOP}.\]

单次生产的数据要么保留于目标，要么留下部分staging；累计生成字节可以保守上界这些目标/staging的保留总量。文件别名按集合计一次，覆盖写的多次成本只进入W。全关闭还需加pre-seal、SEAL_ERROR、payload退出原件、外部见证和独立native/admin集合，见[CLOSE_TOTAL_FORMULA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/CLOSE_TOTAL_FORMULA.json)。

派生兼容义务：若另行证明适用异常类名T≤502，则16×[998＋11T＋69＋3max(106,29＋T)]≤131072，与MR oracle现有整个close_attempts文件读取界相容；T=502给130912，T=503的保守式给131136。[MR_CLOSE_ORACLE_COMPATIBILITY.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/MR_CLOSE_ORACLE_COMPATIBILITY.json)记录这项推导。502仅为代数阈值，当前未选择新政策或证明完整TCB的T界。

最终未决项是R_budget、T的完整TCB来源、E、V_j、terminal review、payload/host流及全部派生集合。存在这些未决项时，B_close保持null，停止猜测更大的容量数值。通用重复调用反例与冻结调用界分别审查，不能用域外任意调用否定上述有条件16/23界。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。
