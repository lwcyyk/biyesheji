# 静态ABI、路径及资源审查

当前源码SHA为 `953d15d7b000b02014062924f80a40d537cba214e17e3459070000f70b8f16d1`。AST解析和调用路径核对完成，目标Python按PE Machine=AMD64及8字节指针gate限定。

| 结构 | AMD64字节数 |
|---|---:|
| SECURITY_ATTRIBUTES | 24 |
| IO_COUNTERS | 48 |
| FILETIME | 8 |
| STARTUPINFOW | 104 |
| STARTUPINFOEXW | 112 |
| PROCESS_INFORMATION | 24 |
| JOBOBJECT_BASIC_LIMIT_INFORMATION | 64 |
| JOBOBJECT_EXTENDED_LIMIT_INFORMATION | 144 |
| JOBOBJECT_BASIC_ACCOUNTING_INFORMATION | 48 |
| JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION | 96 |
| PROCESS_MEMORY_COUNTERS_EX | 80 |

布局按Windows LLP64固定DWORD/BOOL=4、WORD/WCHAR=2、HANDLE/SIZE_T/ULONG_PTR=8及自然对齐作独立整数推导。当前工具没有调用ctypes.sizeof，也没有导入Supervisor。28个API的DLL、argtypes/restype、返回判定及源码位置见R45_WIN32_API_ABI_AUDIT。

CreateProcessW使用STARTUPINFOEX总cb112并显式cast为LPSTARTUPINFOW，mutable Unicode command buffer保存至调用完成。HANDLE_LIST数组24字节、JOB_LIST数组8字节，属性backing storage活到Delete。错误读取在API返回后立即保存，BOOL、invalidHANDLE、DWORD(-1)、WAIT_FAILED和VOID各按接口语义处理。

## 策略与路径

PolicyValidator检查原8类名称、批准值、批准记录对policy正文的摘要绑定，原Driver实际CLI及8文件输入目录、来源闭包批准与OSbuild、资源映射、逐指标资源上界证书和完整产物证书。null额度在WindowsApi创建前拒绝，Job/Child creation均false。

runtime较大二进制逐块哈希，原控制文档有独立读入大小域。路径检查绝对路径、ADS/穿越和重解析，已存在来源要求单链接。具体输出是批准后继根下observer_run_001，child的verification_runs由Driver独占创建。两个输出角色及stdout/stderr管道不与历史文件混用。

文件身份/来源检查依赖不可变可信输入和独占目录条件，native并发替换及异步异常需要未来集成验证。只读policy布尔值须有研究者控制的摘要绑定材料，当前旧G4锁未自动重接纳。

## 成本与执行门

Supervisor显式最多一个Job、一个Child、两pipe、8个owned Win32句柄和一个witness文件句柄，另有有界属性缓冲与chunk。额外线程创建0。pipe内核实际缓冲、native模块活动、JSON/错误内容完整需求以及父内存峰值继续未知。

输出普通记录只能消费witness总cap扣除失败reserve后的空间，最终receipt可用原reserve。共同2MiB约束要求child+parent cap和及真实producer证书同时满足。当前全部8类approved_maximum仍null，命令argv=null。

局部源级组件静态通过。总体R45_STATIC_PREFLIGHT_BLOCKED由当前批准、来源闭包、完整负载、独立OS集成与执行门决定，动态运行数0。
