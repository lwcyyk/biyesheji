# 阶段一致性合同

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

**Root的phase读取和成对发布共享原pt_phase.lock，只有完整、匹配且可用的运行检查点允许后续动作。**

锁限定Root当前批次的root_private/boot；文件仍为Root:Root/0600，无ACL或UID权限扩展。获取使用非阻塞flock，最多512次尝试，截止取now+2秒与已有预窗/运行期限的较小值。每轮先查STOP/CLOSED和期限，只有锁竞争时进行短轮询。sleep没有提供任何状态有效性证据。

Root持锁后校验当前身份、window、counter不可变身份、初始化ID、phase、sequence及phase_record_sha256。writer仅在同一临界区内依序持久化phase/events与公开q，完成原RootIPC文件/目录同步后释放锁。Root reader使用同一锁覆盖两份记录的读取和比较。稳定失配、缺件和IO错误立即拒绝；writer中途失败留下的部分提交不会被读方补写或猜测修复。

线性化依据为公开Root记录完成发布并在临界区结束后可供Root读方验证。phase与q之间的暂态只有writer持锁期间可出现，其他Root读方等待获取该锁。进程崩溃后若文件留下稳定失配，后续校验拒绝并交给原关闭路径。kernel flock、原子rename、fsync、受信存储与正常返回/调度属于明确环境前提，未获得实时系统证明。

Payload继续只读Root:989/0640的原子公开点，验证固定phase/seq、身份/window/counter及committed字段，保留运行检查点缺失拒绝。Payload没有Root锁或私有目录权限，阶段更新仅由当前Root scheduler完成；首个工作服务在Root require_work成功、提交完成之后启动。CLOSED/STOP仍由原RootIPC检查和新守卫支配，ARMED不替代C00、S套件或资源资格。

2秒限定的是锁重试/许可时段，消耗同一运行墙钟；发生阻塞IO或不可调度时仍依赖原停止TCB与环境响应假设。全链300秒性能及真实锁等待、IO中断和调度均待动态核验。终态只读seal适用性检查使用显式terminal_inspection，保留阶段完整性核验；它没有工作发放动作。

[实现](evidence/SOURCE_FINAL_R3/src/startup_lifecycle.py) · [28项静态检查](evidence/SYNTAX_AND_CONTROL_FLOW_CHECK.json) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
