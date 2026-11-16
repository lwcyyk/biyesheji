# 完整负载与2MiB容量审查

**P1在明确前提下成立；P2和完整容量适配继续阻塞；P3待批准。** 本轮独立复核13份原证书和41类原异常，增补5类，详表共46类。

## P1：已存前缀安全

对owned文件f记已扣费用c_f、可见逻辑大小v_f、配额q_f。在新命名空间、受信不可变源码/运行时、独占写入、无外部改写、FileIO每次写至多请求长度且无seek扩洞的接口合同下，有：

`0 <= v_f <= c_f <= q_f`。

初始只允许只读approval<=8192，其余输出不存在。序列化通过后、open/write前全长扣费；短写/flush/fsync/时间门失败保留全费并poison；关闭无Python待刷payload；无删除、退款、重开、rename或磁盘临时副本。逐项相加：`S(t)<=2000167<=2097152`，余量96985。

这覆盖全部受控正常/失败/超时/收尾/部分写入前缀，以及本轮新增的回调错误路径。临时磁盘副本0；部分正式文件、确认与未知持久化占用都由原已扣额度覆盖，后两者不会再重复求和。RAM、物理簇和内核缓存不被称为已测0。禁用命令带来的不可达性未用于空泛证明。

## P2：核心事实保留有独立缺口

W01给出可逐步核对的纸面故障轨迹：在匹配冻结环境的假设下，原A01 `ActivationCases.test_A01_default_off` 的body/tearDown成功；标准库case.py:648调用addSuccess。Runner Results.addSuccess:1333先调用父类；标准库runner.py:95写“ok”状态。此时合法日志I/O失败，则Runner Results.record:1325尚未执行；最终assertion_rows:552给A01默认NOT_RUN/executed=false。已完成结果可从权威表丢失。

这条路径使用原测试和允许审查的I/O故障，没有改变断言；本轮没有注入故障。P1仍成立，完整接受也保持失败，但L0已知结果保留义务没有取得。原41类中的日志失败因此需要增加这一独立完整性子责任。

W02：原测试tearDown已把checks/calls写入模块DETAILS，而capture_details仅在整组runner返回后调用。组内中断时，当前组的原必需DETAILS尚未转移到state.details。W03：poison后的journal即使剩余65536收尾配额且存储恢复，也继续拒绝追加；保留字节本身不能保证可用性。W04：若所有合法持久化操作持续失败，任何有限预算都无法保证新完整耐久receipt。前四份见证位于sources/STATIC_COMPLETENESS_WITNESSES.json。

## 独立字节计算

| 部件 | 可核查数值B | 范围 |
|---|---:|---|
| 68项成功case核心数组 | 22366 | 固定manifest，elapsed_ns非负且接受128位，detail=None；含数组结构。 |
| 同数组elapsed_ns<10^11 | 20462 | 另加一致单调时钟/正常工作截止前提。 |
| 六个计数字段 | 68 | 每值<=68的松长度界。 |
| 68个执行ID数组 | 409 | 固定三字符ID。 |
| invocation含LF | 681 | 固定argv、32字符UTC和SHA。 |
| RUN_START含LF | 9576 | 接受python文本JSON<=8192，其余固定。 |
| D24两份原字节 | 1032/287 | 原fixture完整hash绑定。 |

这些数值由独立惰性JSON数据构造计算，未调用Runner计费/序列化函数。case核心没有覆盖全部DETAILS、来源、账本、异常及外层codec/文件共存，无法直接相加为完整正常路径上界。

来源独立边界给出的DETAILS68松原树界为4456517，journal计数8320乘单条guard为8724152320。它们远超份额，但属于过宽的独立上包络，未证明冻结68能达到这些值。不能据此声明具体超额或预算下界。原817454仍是固定历史609条编码结果。

`NORMAL_PATH_REQUIRED_BYTES=UNKNOWN`，`WORST_FAILURE_PATH_REQUIRED_BYTES=UNKNOWN`。最终三份完整payload适配262144/262144/131072，完整journal适配1048576（工作983040），以及对应的联合内容/压缩上界均待证。正式裁决为COMPLETE_PAYLOAD_CAPACITY_UNPROVEN，固定68尚无完整字节超额见证。

任意长全文的无限接口域无法全量装入固定2MiB；全部存储拒写时完整耐久性也不可实现。两项结论分别限定于表示接口域和存储可用性，均未被提升为冻结68的具体容量失败。

## flush与收尾复核

write/flush/fsync失败时保留charged；uncertain=charged-confirmed为保守上界，真实持久化未知量为UNKNOWN。BUFFERED_BYTES=0仅指FileIO用户态缓冲。pre-call attempted计数先于真正调用，异步中断可能发生其间，不能把它解释为已证的OS syscall进入次数。权威“观察”与保守“已预扣/拟尝试”需在合同中分明。

原90/115/120秒门和32次terminal预扣尝试保持。收尾保护786432字节包含于原份额。codec在工作阶段准备；收尾只读已有观测/owned证据、写固定路径和关闭owned句柄。新测试与审计工作受门约束；在途native操作晚返回、存储不可写、最后关闭不能确认或记录器分配失败均只保证保留已确认前缀/非零退出，完整收尾有条件。

W05进一步收窄时间结论：若owned日志close在120秒前启动、121秒才返回，main随后扫描并sha读取owned文件；terminal的OUTPUT读分支没有时钟门。这允许120秒后新开始证据读/hash。新写和新close的门保持，全部收尾操作都在120秒内的更强结论未取得。此为源级/接口时序反模型，未实测平台延迟，后继修复需独立授权。
