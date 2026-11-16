# B1关闭调用与记录数证明

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

**CONDITIONAL_PROVED。** 定义E域为一次新鲜的第256条PENDING耗尽事件，初始C09阶段Sender已经退出，HANDOFF_VERIFIED尚未建立，恢复尚未发生，观察/关闭没有新global debit，拟异常吸收语义生效。原全scope界H52/core212、A16/S23/Q7/W2另行保留。[SCOPED_CLOSE_COUNT_PROOF.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/SCOPED_CLOSE_COUNT_PROOF.json)

|类型|E域最多调用/生产|唯一目标/稳定路径|重复与池归属|
|---|---:|---:|---|
|Receiver第一层abort|1|多原件节点|最多9项核心生产尝试，健康串行前缀8写/7路径|
|Receiver第二层abort|1|复用固定目标及新stop路径|最多9尝试，健康串行追加6写，前后合计14写/9路径|
|同阶段coordinator abort|4|同固定目标及其stop路径|继承一阶段有限异常包装器，已退出Sender的Python finally不执行|
|STOP_REQUEST|≤6次Root发布|1|存在检查可并发覆盖，按写量和稳定路径分别计|
|first_failure|≤6次put尝试|1|exclusive首次文件，无独立随机staging|
|external_closing|≤6次put|1|同一受信delegate原件，替换写产生临时对象|
|ABORTING/final|各≤6次put|同1文件|两个版本写成本，最终路径一次计量|
|CLOSED|primary/fallback尝试共同受S/A约束|1|H锁保护首次终态，部分发布失败仍可后续尝试|
|stop_event|≤8次primary marker候选|≤8|CLOSED已存在时创建，来自实际有限stop调用|
|stop_result|≤8|≤8|每次到达结果发布的stop调用一个路径|
|close_attempt行|≤6|1文件|每个非announce abort至多一行|
|waitpid|≤1|≤1|只在当前initial phase实际父进程reap时发布|
|sealer调用|≤3|后层对象另计|coordinator finally、boot异常、Receiver external tail各一次|

E域active coordinator至多一个阶段，其abort≤4；Receiver两层≤2，故A_E≤6。每abort至多一次primary stop_tree，coordinator另外两个直接stop位置各至多一次，故S_E≤8。W_E≤1、Q_E≤3、H_E=0。由原七项非stop-tree生产规则得到。

\[N_{E,production}\le7\times6+2\times8+1=59.\]

核心稳定目标粗界为5个固定异常目标＋2×8个stop路径＋close_attempt文件1＋waitpid1=23。BC随机staging创建尝试≤3A=18，RootIPC≤2A＋2S＋W=29，合计47；稳定与失败staging路径类的粗合并界为70。它们是不同计量，极值也可能互斥。空mr_close.lock、必要目录与后层sealer lock等metadata另需inode/资源。[src/manager_recovery.py:33](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:33) [src/root_ipc.py:105](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/root_ipc.py:105) [src/boot_continuity.py:99](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/boot_continuity.py:99)

健康串行示例的第一层写STOP、first、delegate、ABORTING、CLOSED、result、attempt、final共8次。第二层复用STOP/first，写delegate、ABORTING、stop_event、result、attempt、final共6次。ABORTING/final同路径，最终共9个稳定核心路径。该示例需要Receiver首错胜出、普通持久化成功且两次primary cleanup均完成。

正常VERIFIED路径执行一次close=False，并发生HANDOFF_VERIFIED状态、result_C09、AWAIT状态、RESUMED状态及恢复batch_state五次其他数据发布，共6次真实发布、4个稳定载体。其stage主行已经属于263/345148。预付/bind/ACK/resume失败等E域外的B1故障使用原更宽冻结角色包络，212次尝试持续保留其作用域。

现有first文件有幂等首错性质，其他attempt/event仍会追加。当前没有close请求ID或单独关闭grant账，因此“恢复不重发关闭额度”和“CLOSED后冻结新预留”是拟合同义务。已经预留的有限关闭操作需要在CLOSED之后完成final/退出证据，普通新观察和新的关闭预留发行同时吸收。域外任意E_n不属于原次数界。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
