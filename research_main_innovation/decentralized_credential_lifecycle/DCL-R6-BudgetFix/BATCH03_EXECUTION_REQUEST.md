# batch03独立执行授权申请
Material Passport：REVIEWABLE_REQUEST；BF-static-1冻结产物；batch03=UNAUTHORIZED。本文及未来命令表仅供审阅，本轮创建/启动batch03、C00–C12、性能探针、F1/F4执行均为0。

## 申请范围与前置
申请在下一轮获得明确新资源窗口后，使用唯一lc03输入执行：校准C00→C01→C02→C03→C04→C05→C06→C07→C08→C09（预定launcher退出23、同批恢复一次）→C10→C11→C12；全部PASS且实际资源检查满足时，由同一冻结launcher自动进入FORMAL，固定F1→F4。审批需明确接受本轮条件安全证明及尚缺范围租约动态故障证据的范围。当前源在C12全PASS后自动进入FORMAL；若未来只批准校准，应先形成独立受审新版本与哈希，再运行该窄范围。

当前可逐argv审阅并申请的执行范围是上述冻结程序及其既有故障case。S1–S9范围registry/claim专项故障夹具尚无冻结代码和命令，保持独立未决；本申请不把C11镜像结果提升为精确范围故障认证。若下一轮要求先完成全部S1–S9动态证据，再决定FORMAL，需先静态补充有界夹具/人工准入门并重新冻结；当前BF-static-1保持原哈希。

## 审批必须绑定的字节
- guard.py=752c92f6114ce7c2ec9d45d39e4d46256b778ee91ce3a59ec55f37b6a27e4a02。
- guard_probe.py=32ed91e5135e09454d6634bf369193c7ccf4e8ae669e523b1dd781ed96109de3。
- run_batch.py=c88fc3b07e6feddf5d2aa96adf3b3b63fc3f6f9897d585f42d6882a5279a63e7，五业务摘要见SOURCE_DIFF_INDEX。
- static_manifest=7c320d6183dff88bb032abd33ed2ff882301a7d06a8bac53e9c19bd327e7f41f。
- execution_lock=5090e398d32295513b51249ac9942d9ce9c97fc37bc5d2f11242dd11347a3260。
- child_contracts=d78be83c648b76a391708eddbb601724f83277392ae8fbdd3daf95d0e522eb7f，精确N=32896/4096/1；协议EXACT-RANGE/1。
- Python /usr/bin/python3.12，3.12.3，e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f；CPY312-UBU24/1。
- 拟用slice=e4bdea70e3e13ad7a3a431652ba8634bfa527e1aba0a0037a1bbb7e6698b89c2；瞬态service按execution_lock的14组完整argv及属性建立。旧LC service摘要仅作历史参照，下一批实际服务由锁中systemd-run建立。

## 资源与资格
总访问≤1,000,000；总墙钟≤1,800秒；T0+1740提前停止；校准共同T0+300及100000访问；单进程LimitAS=1GiB soft/hard；父slice TasksMax=4、MemoryMax=4GiB，服务同限制、swap0、OOMPolicy=kill。UID999/GID989既有身份复用；账户/依赖/运行时变更需独立授权。

AS4-PAYLOAD/1仅覆盖普通AS计费映射的RSS条件上界，特殊内核映射单列评审。执行receipt需接受ORDINARY_AS_ACCOUNTED;KERNEL_SPECIALS_SEPARATELY_REVIEWED。实际cgroup成员、pids.max、AS、权限与不可访问管理通道均须由C00–C12重新核验；C00/C01旧PASS不会转移到batch03。

## 准备与确切命令
[execution_lock.json](evidence/execution_lock.json)是JSON字面argv权威清单，[FUTURE_COMMANDS.md](evidence/FUTURE_COMMANDS.md)逐项展开5个准备命令、14 payload、外部stop、launch和预定resume。外层Windows前缀为：

`C:\Windows\system32\wsl.exe --distribution Ubuntu-24.04 --exec`

准备命令明确申请创建batch03根/inputs/reports和dcl-r6专有out；将lc03/inputs/dclr6batch03.slice以root:root0644安装至/etc/systemd/system/dclr6batch03.slice，verify后daemon-reload。当前这些动作执行次数0。准备前先重核全部16 source/cache、runtime31+1224树锁、合同和拟用单位hash、实际账户、内核/manager、目录冲突及来源；任一不明停止，不生成授权锁。

新授权到达后，将该次明确授权的原文保存为batch03/inputs/BATCH03_AUTHORIZATION_TEXT.txt，并建立root拥有且组可读、其他不可写的execution_authorization.json。字段为batch_id=batch03、scope=CALIBRATE_THEN_F1_F4、profile=CPY312-UBU24/1、limits=[1000000,1800,1740,1073741824,4]、本版manifest/lock哈希、该次授权原文真实hash及special_mapping_scope。未来授权文本及其hash由批准后真实输入产生；本轮receipt缺失，不能以本静态任务授权代替。

启动与唯一预定恢复命令分别为：

```text
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/lc03/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch03
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/lc03/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch03 --resume
```

恢复仅用于C09预定exit23，须先见root持久result_C09=PASS、状态AWAIT_EXPECTED_RESUME、resume_count=0；同boot/T0/deadline/visits，全批最多一次。未知退出关闭整批。payload与external-stop只由授权launcher在锁定时序调用，不独立启动或自动重试。out在首次launcher前为空；窗口与账只由批准后的launcher初始化。

## 输出与停止
Linux=/var/lib/dcl-r6/batch03/out，host证据导出目标=D:\毕业设计\DCL-R6-isolated-verification\batch03；研究结果另建DCL-R6-batch03。当前三个新批目录均未创建。运行后封存原账、registry、journal、intent、所有票据/授权/单位读回、stdout/stderr、timing、C00–C12及模型summary，附冻结lc03来源副本与完整hash包；封存失败保持未封状态，禁止以缺件发布PASS。

预算上限、300软窗、1740提前停、boot/身份/hash/权限漂移、余额模糊、短写/fsync失败、watchdog异常、资源资格FAIL、C02未真正启动或缺少退出证据、未知进程退出、语义反例均停止。到达资源界限按INCONCLUSIVE_LIMIT或资源失败登记，不升级到形式化通过。FORMAL只在当前批全部校准PASS后进入；F1基线/变体/重放/键谓词表，再F4固定样例/G64/独立参考/变体，保持单worker与五业务字节。

## 性能与动态验收
核对一次N范围事务真实耗时、9+2同步机会的真实syscall时间、局部扣减成本及调度间隙；C02必须有持久claim、操作计数、child输出、进程启动/退出观察，且在T0+300内完成；账须连续、R覆盖所有可能执行。C03/C04同核一次认领。单纯提速保持独立性能结论，资源资格与模型结论按各自门判定。

S1–S9后续有界测试设计：以这三个固定task为输入，逐个在PREP/counter/registry/final-intent/claim前后中断；同请求与冲突请求各两次，双controller/双claim各2参与者；本地扣减N与N+1，关闭/过期/boot变化各1夹具。每个受损全局账独立关批，额度保持全N占用；禁止复用模糊账续跑。测试预算、代码、argv与每个新窗口须另锁再授权，当前测试次数0。

## 历史保护
batch02全部32191消耗、失败与ZIP、batch01的27/118.7340827保持。误路径47项保留只读及blocked by policy，不迁移、不删、不绕策略。来源冲突/目录已存在时拒绝初始化。当前RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，主机制IMPLEMENTATION_GATE=CLOSED。
