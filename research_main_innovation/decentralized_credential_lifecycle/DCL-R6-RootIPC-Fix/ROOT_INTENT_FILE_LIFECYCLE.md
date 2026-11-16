# 共享 intent 的真实权限生命周期

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

RI-1：PASS_STATIC，依据batch05冻结源码与真实元数据/日志。原预算intent与C09持久交接对象分别追踪；本次真实故障发生在预算intent。

1. 原guard.py:470–481由Root初始化counter，写初始COMMITTED intent，再chown为999:989；初始mode0600。out目录由冻结准备命令设为999:989/0700，输入/批根为Root:989/0750。
2. payload每次访问在`_counter_lock`取得线程锁与counter flock后读取intent（原509行）。Root需要独立重算并把审查访问纳入同一全局预算，因此C09H审查调用34次`reserve_counter`；后续S与17门审查走同一预算入口。Root具备读取原账权限，也确实需要按照原计费合同推进共享账。
3. 原`atomic`在out创建0600临时文件，`root_record=False`分支保留当前writer身份；Root euid0调用后临时文件为0:0。写入/文件fsync后`os.replace`将新inode置于共享intent名字，原payload owner随旧inode离开路径。原`atomic`此分支没有发布前fchown/fchmod。
4. batch05 Root审查最后COMMITTED intent时间3898.266588342，before37292/after47293；下一C09 uid999读取在3898.529937533前触发EACCES，STOP_REQUEST明确指向该路径。命令26确认intent0:0/0600、counter/journal999:989/0600。
5. STOP_REQUEST=T0+20.861903589，CLOSED=+20.909951317，payload组空=+20.927591657；Root最终清理=+300.043546214。303组事务内容配对完整，入口读取发生于新事务之前。

根因轴：文件路径为冻结正确路径；内容/额度配对健康；Root替换导致owner改变，0600使uid999缺少读取权限。目录本身允许uid999遍历/读写；原子rename保留临时inode的metadata。mode创建受umask影响，常规umask只会收紧所请求位；实际观察0600。历史临时文件本体/umask值和已被替换的旧inode未单独捕获，源码链与最终stat支持上述解释。旧代码的resolve/O_NOFOLLOW只覆盖部分步骤，历史源码缺少完整目录fd抗替换；当前记录没有实际符号链接攻击证据。

|对象|实际/未来路径|创建者|写入者|读取者|删除/替换权|owner:group/mode|持久化合同|
|---|---|---|---|---|---|---|---|
|batch06根 / inputs|/var/lib/dcl-r6/batch06[/inputs]|Root|Root|Root；989遍历/读|Root父目录|0:989/0750|目录创建与未来发布目录屏障|
|out|…/out|Root准备|999；Root TCB|999/Root|999拥有其内容；Root可管理|999:989/0700|同一ext4设备|
|共享counter|out/visits.bin|Root初始化后chown|999及Root审查；同一flock|999/Root|out的999/Root|999:989/0600|原24B counter与fsync算法保持|
|共享预算intent|out/visits.bin.intent.json|Root初始化；双方发布|999及Root审查|999/Root|out的999/Root|999:989/0600|PREPARED/COMMITTED原协议；Root发布前设置元数据|
|共享journal|out/visits.bin.journal.jsonl|首个payload事务|999及Root append|999/Root|out的999/Root|999:989/0600|原append与fsync保持|
|C09 ready引用|out/C09.ready.json|999|冻结C09 payload|Root核ticket/身份/账；999|out的999/Root|999:989/0600|原marker；仅作为待核引用|
|Root私有目录|inputs/root_private|Root准备|Root|Root|Root|0:0/0700|无POSIX ACL；独立暂存与原始审查记录|
|Root暂存对象|inputs/root_private/.publish.<pid>.<nonce>|Root|Root持有fd|Root；目录阻断payload|Root|按目标fchown/fchmod；外层0700|内容+元数据fsync→rename→双目录fsync→stat|
|Root私有日志/普通退出记录|inputs/root_private/c09_events.jsonl；waitpid_*.json；ipc_case_*.json|Root|Root|Root|Root|0:0/0600|日志fsync；记录Root受控发布；原始waitpid保留|
|Payload可读Root资格|inputs/C09H_QUALIFICATION.json；ROOT_IPC_QUALIFICATION.json；RANGE/GATE/RESOURCE等|Root|Root|Root/989|Root输入目录|0:989/0640|Root完整审查后发布；payload仅读保护收据|
|持久commit / ACK证据|inputs/c09_commit.json；c09_handoff.json；c09_exit_witness.json|Root sender/receiver/parent各职责|Root且生命周期锁|Root/989用于FORMAL/恢复核验|Root输入目录|0:989/0640|原持久ACK、waitpid、revision与摘要合同保持|
|Root控制socket / 生命周期锁|inputs/c09_control.sock；c09_lifecycle.lock|Root|Root认证调用方|Root|Root输入目录|0:0/0600|SO_PEERCRED＋稳定身份；锁串行闭合/分类|

删除能力由父目录w+x控制；out中的uid999可替换自己的共享账对象。Root私有与保护收据位于Root拥有的输入层。当前原文件/错误日志/完整ZIP逐流核对见[原始审查](evidence/HISTORICAL_RAW_REVIEW.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[batch05首次失败](<../DCL-R6-batch05/BATCH05_COUNTEREXAMPLES.md>)。
