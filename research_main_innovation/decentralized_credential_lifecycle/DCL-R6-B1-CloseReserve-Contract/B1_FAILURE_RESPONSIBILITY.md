# Root、管理器、存储和外部TCB责任

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

|责任者|现有动作与证据|失败责任边界|
|---|---|---|
|Receiver Root|原pidfd观察、quota候选终态、808/817异常链、MR收据|自身死亡/marker缺失时不能凭本地_HALTED证明全局停止|
|直接父协调者|真实os.waitpid、原状态/exit_code发布、旧有限异常回收|死亡或发布失败后精确亲子见证可能永久缺失|
|systemd与kernel|stop/kill、pidfd、身份与cgroup empty观察|正确来源需新鲜绑定，失败/阻塞和实际退出时刻分别核验|
|RootIPC/BC.Store|权限、类型/无链接、编码、原子替换与fsync顺序|当前没有独立物理容量底线或任意介质故障成功保证|
|存储保障provider|拟提供close data/inode/metadata/temp底线及排除其他writer|实际provider、配额/分配凭据、持久性/故障域均null|
|外部guardian/host|拟在Receiver退出后提供独立身份绑定witness与保留来源|当前专用可保证渠道未绑定，不能依赖必定成功的后层归档|
|native/admin|按实际close、exit、预算、原件和空间前提完成或保留失败/UNKNOWN|部分产物不获得完整完成状态|

source的primary cleanup与fallback会尝试停止payload、Root角色回收及最终收据，真实Root/manager责任见当前调用段。[src/manager_recovery.py:369](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:369) [src/manager_recovery.py:291](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:291)

外部TCB合同需要指定操作者、准确监控对象/boot/PID-start/unit generation、停止动作、保存路径/权限/字节、期限与失败出口。仅有“外部会处理”不足以实例化该来源。必要安全证据应在后层archive开始前取得保留保障，index或admin receipt可以引用已有原件。

当前最小缺口是定量wire、物理资源/排他底线和独立caller-exit保留责任。这些责任可以针对B1关闭子集定义，完整4,450原件集合由后层负责。与受信kernel/Root故障模型一致的UNKNOWN和原预算保持规则保留。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
