# 崩溃与重复执行安全的条件证明
Material Passport：BF-static-1；CONDITIONAL_PASS；源码推导，动态故障注入0次，机器证明0次。

## 前提与线性化点
前提 P1：审查哈希对应的固定程序、可信root启动器/授权记录和内核；输出账仅由这些合作进程写入。P2：同一 counter inode、fcntl 锁与进程内锁有效，可信方保持文件/父目录，禁止换账、回滚、外部编辑。P3：Linux文件系统按所用 fsync、原子rename、目录fsync提供合同保证；WSL宿主掉电、设备缓存及损坏的端到端保证仍需部署证据。P4：boot与身份检查可用，未知异常终止信用发放。P5：计费操作只出现在受审扣减后的固定调用点；进程复制受身份检验。P6：管理器与调度可最终停止组；精确实时终止延迟仍未认证。

counter 更新是累计占用的串行点；最终 COMMITTED intent 的目录fsync返回是新范围可供派发的持久完成点。claim registry 的目录fsync返回是执行者唯一认领完成点。局部 used+=1 是本执行者扣减点。各项前后检查及失败分支均参与证明。

持久顺序（持有全局锁）：
PREP intent file+dir sync → PREP journal sync → counter pwrite+sync → 使用新stamp的COMMIT journal sync → UNCLAIMED事实file+dir sync → 最终COMMITTED intent file+dir sync → deadline复核 → 返回新对象。派发后，child claim另有file+dir sync。新建reservations目录的父目录由其后最终intent的OUT目录fsync覆盖；最终屏障完成之前不会派发。

## 归纳不变量
初始 R=0。单次申请量n已在锁内检查R+n≤cap且phase cap；成功后区间[R,R+n)与先前区间相离，R单调增加。单信用路径n=1，精确路径n=N。拒绝与异常均不会发放本次新执行信用。对于一次持久范围，只有首次created对象可派发；所有认领在同一锁内，首个持久CLAIMED之后其他调用看到CLAIMED并拒绝。因此每范围最多一个可用LocalCredits实例，且每实例至多N次前置扣减。fork子进程身份变化被拒，父退出由pidfd检查。合并得A≤Σn≤B。局部线程共享同一used锁，避免最后一信用被重复消费。

“至多一个”依据包括不重构内部对象的固定程序前提；它没有赋予同UID恶意脚本不可伪造的能力。

## S1–S9
|情形|源码处理与占用|静态结论 / 后续证据|
|---|---|---|
|S1 预留前崩溃|尚未拿到新对象，无child许可；R保持|PASS_STATIC；运行前中断待测|
|S2 PREPARED后崩溃|旧intent为PREPARED或counter不一致，下一次锁检查拒绝；N按可能生效保守占用，整批关闭|CONDITIONAL_PASS；各持久缝隙待注入|
|S3 持久完成、发放前崩溃|R已增加N，原事实保留；新controller重复只取得created=False；原owner无法重生|CONDITIONAL_PASS；耗额度零执行待测|
|S4 发放/认领后崩溃|UNCLAIMED至CLAIMED之间仍覆盖N；CLAIMED拒绝重复；claim完成前异常无局部对象；完成后异常全N持续占用|CONDITIONAL_PASS；claim前后故障待测|
|S5 重复task_id|锁内先验证健康intent，再验证请求与区间；同请求返回旧事实，不提供新派发；冲突拒绝|PASS_STATIC；重复提交/重新ticket待测|
|S6 并发|全局同inode的flock与线程RLock覆盖余额、查重、事实写入及claim；根启动器另有launcher锁；第二owner不获原范围执行权|CONDITIONAL_PASS；双申请/双claim待测|
|S7 短写/fsync失败|_full、pwrite长度检查；异常触发永久_HALTED及best-effort STOP_REQUEST；PREP残片保留；局部故障夹具与全局分离|CONDITIONAL_PASS；真实失败传播待测|
|S8 关闭/期限|claim、dispatch、每次debit前检查STOP/CLOSED/boot/deadline；越期完成的持久占用烧掉；新批身份不同|CONDITIONAL_PASS；终止时序待测|
|S9 第N+1次|used>=N在used递增和语义操作之前抛LimitReached；每个受审调用点先visit|PASS_STATIC；N/N+1边界待测|

S5只有在活动且健康账条件下提供幂等事实。毒化、关闭、过期时先拒绝整个访问；该策略保护额度并放弃恢复可用性。S7的LimitReached发生在持久完成后时仍保持占用。模拟fault仅允许局部镜像；真实全局I/O异常会触发停止。

S8的时限语义以debit检查点为准。检查与后续CPU指令间存在调度间隔，已开始操作及内核终止需要时间；严格“截止瞬间所有指令已停止”仍为UNRESOLVED。外部stop、watchdog、1740提前停提供分层控制，当前只给条件论证。

## 崩溃边界分类
- 在counter sync之前：可能有PREP残片、部分写入；无新许可；关闭并保守占用。
- counter完成至最终intent完成：可能出现COMMIT journal/UNCLAIMED事实而全局intent仍PREP；锁入口拒绝全部后续授信。
- 最终intent完成后：若registry损坏或缺失，合作程序的旧owner不会自动重试派发；完整系统掉电恢复须遵守P3。禁止丢弃registry后保持同批继续运行。
- claim同步未返回：调用方拿不到局部对象；即使CLAIMED已落盘，N全部烧掉。
- claim返回以后：持久CLAIMED阻止第二对象；丢失局部cursor采用全额烧掉。

当前C11是单信用镜像四故障点检查；它未覆盖范围registry、claim、跨controller和全局崩溃恢复。S1–S9仍为DYNAMIC_UNVERIFIED。后续专项故障夹具需先冻结输入/源码/argv/资源上界，再独立批准执行。
