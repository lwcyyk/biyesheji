# 256次观察与263条主日志的记录数证明

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

**PQ-2=CONDITIONAL_PROVED；现行256上界为COUNTEREXAMPLE；RECORD_BOUND_CONDITIONAL。** 以下归纳针对待批合同。当前冻结程序继续保留PENDING自环。

设A为已持久预扣的分类尝试，P为完整PENDING行，T为终态CHECK，E为生命周期行，K为ACK行，U为未完成的部分行/已烧掉空槽。取“记录”时同时约束完整行和占用槽，避免把短写尾部遗漏：

\[P+T+U\le A\le256,\quad E\le6,\quad K\le1,\quad N_{main}\le A+E+K\le263.\]

T≤1要求认证单Receiver及终态锁存；成功路径T=1⇒P≤255。失败路径允许P=256；它停在EXIT_OBSERVED前缀，通常仅4个stage＋1ACK，故261行已是该耗尽轨迹的更紧界。263为所有路径的共同包络。对完成恢复的正常轨迹，旧源码公式N=P＋8；代入成功P≤255得到263。

|额外类别|实际调用位置|固定上界的来源|崩溃/并发条件|
|---|---|---|---|
|HANDOFF_PREPARING|[c09_handoff.py:187](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:187)|sender_prepare已有state即拒绝|持久类别位先扣；发布中断后关闭|
|HANDOFF_READY|[c09_handoff.py:226](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:226)|只从PREPARING进入|同锁/类别位；重复PREPARE不给新stage|
|HANDOFF_COMMITTED|[c09_handoff.py:232](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:232)|同一PREPARE分支提交一次|同锁/类别位；commit原件保留|
|LAUNCHER_EXIT_OBSERVED|[c09_handoff.py:262](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:262)|只从COMMITTED进入；PENDING维持revision4|同锁/类别位；重放时烧掉的位保持|
|HANDOFF_VERIFIED|[c09_handoff.py:286](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:286)|classification_count从0变1|终态锁存先于解锁cleanup，随后类别位一次|
|RESUMED|[c09_handoff.py:343](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:343)|VERIFIED、resume_count0与AWAIT等门|类别位先扣；状态发布模糊即关闭|
|SENDER_ACK_OBSERVED|[c09_handoff.py:196](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:196)|原生sender_prepare业务调用一次|独立第7位；相同token不得再次append|

公式可写为f(O_max,E_max,R_max)=O_max+E_max+ACK_max+R_max=256+6+1+0。R_max=0只指额外主日志恢复/补充行：当前Root恢复仅RESUMED，HANDOFF_FAILED无原生发布；MR/STOP/回收文件属于独立集合。未来增加生产点或恢复重试必须重审R_max和字节表。

归纳不变量：每次授权写入先在同一个durable cursor递增ordinal和reserved/debited计数；七个类别位只从0变1，A只增不减。所有角色用同一稳定H锁，锁内重新读取cursor，检查终态并持久预扣，完成后最多一次os.write。每个被消耗token只对应一次写入尝试；部分写入保留，整行重试关闭。由注入映射“写入尝试→不同持久槽”得到N≤263。

并发临界点为**预扣cursor的原子发布及其必需fsync成功，且H锁尚未释放**。最终分类另有completion写入，在释放锁去stop_tree前锁存TERMINAL_LATCHED。最后一额只会发给第一个完成预扣者；第二个看到A=256或终态，获得0额。稳定锁inode、受信Root、无回滚和存储持久性都是显式条件。

最小反例CE-LAST：A/B都先读255，分别append，再写256，得到257次记录；CE-TERMINAL：A写VERIFIED解锁cleanup，B在VERIFIED stage落盘前再写VERIFIED；CE-REPLAY：stage日志fsync成功、state落盘前崩溃，恢复者重做publish。三者说明仅有计数变量/状态名/顺序执行论证不足以证明并发及恢复。见[CRASH_AND_CONCURRENCY_MATRIX.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/CRASH_AND_CONCURRENCY_MATRIX.json)。这些是静态交错，未运行测试。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
