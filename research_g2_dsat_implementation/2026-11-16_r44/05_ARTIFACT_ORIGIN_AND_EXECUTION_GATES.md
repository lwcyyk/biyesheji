# 产物、来源与执行门

当前driver最多显式创建8个native产物：RESULTS、stdout、stderr、TEST_MANIFEST、SOURCE_LOCK、STATE_WITNESS、RESOURCE_LEDGER及失败时EARLY_FAILURE。未实现physical_journal的65536B槽位未分配。

一次性xb/claims和precharge使这些产物的显式payload上界为933888B，没有driver临时副本、rename或自动重开。完整正常/失败producer需求依旧未证；序列化在长度检查前分配，traceback格式化还可能引入读取/内存，文件cap约束受控存储前缀，内存和完整内容适配各有证明责任。

54个内部变体保存末态witness，逐事件/完整fired计划仍留内存。强制终止时可能没有持久化case前缀，结果知识必须UNKNOWN，不能据IO字节或存活文件恢复PASS。

## 父产物与隔离

父观察器不得预建child的verification_runs，因为现有child admission要求该父目录也不存在。建议父证据放独立observer_run_001，源文件/事件schema和候选字节仍待实施推导；至少增加一个directory和一个witness文件，必须联合计费。

若采用child8文件+parent1文件，最大总数可在9内；名称/角色与原未使用physical_journal不同，仍需明确批准。不能静默复用child stdout/stderr。观察器cap、采样数量及自身内存/查询开销目前为null。

新鲜目录/xb在独占可信宿主前提下避免直接覆盖旧文件。更强的底层身份核验可按已打开句柄的[VolumeSerialNumber+FileId](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info)比较；不同系统/FS支持需要检查实际返回。本轮未查询文件ID，未证明并发敌对宿主下的重解析安全。

## 运行时来源

需要锁定当前CPython EXE/DLL、stdlib源码/缓存/frozen/builtin及loader、zlib/binascii、hash/crypto native、sqlite3/_sqlite3/SQLite、ctypes/libffi，以及kernel32转发/KernelBase/NTDLL/OS构建。Driver只对SUT原字节compile，stdlib仍有独立加载责任；-B不等于全部缓存读取被禁止。

仅有源码不直接调用网络/SQLite不能证明所有动态模块无副作用。原G4七变化/五缺失与旧pin保持，RUNTIME_ORIGIN_UNPROVEN。版本标签和API网页不能代替已安装二进制/签名来源。

## A—F门

| 门 | 当前值 | 范围 |
|---|---|---|
| A 预算结构完整 | true | 八类字段/单位/未知/审批均登记 |
| B 完整候选额度充分 | false | 局部非null候选有依据，完整数值缺失 |
| C 正式额度批准 | false | 原max为null，研究者未确认候选 |
| D 外部监督规格明确 | true | 会计/身份/内存/请求/退出及盲区已定义 |
| E 外部监督已实现 | false | 拟脚本不存在，OS能力没有成为项目实现 |
| F 动态执行资格 | false | 资源、监督、来源、负载、命令与独立运行批准未满足 |

当前命令argv=null、command_executable=false、executed=false。T20桥接、来源修复、资源批准与监督器实施分别登记，28项执行保持独立授权。G2完整L0、G3部分批准、G4待核及D1-B1部分实现未被改写。
