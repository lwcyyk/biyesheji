# F24管道异常分类与留证

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助源码修订、纸面分支复核与静态取证；动态验证与外部独立复核待取得。

**PIPE_EXCEPTION_POLICY_STATIC_PASSED / R24_PIPE_POLICY_STATIC_VERIFIED。F24_FIX_NOT_YET_EXECUTED。** 本轮没有通过动态注入或F24单项运行证明实际分支覆盖。

## 来源与限定

R22首轮F24在竞争败者stdin.close处出现`OSError(errno=22)`；原stdout与ERROR堆栈保持。此前补丁只以poll已退出判断所有OSError，本轮将接受条件收窄。

本机固定CPython3.12.14的`Lib/subprocess.py`第1140–1163行在`_stdin_write`中单列BrokenPipeError与Windows EINVAL，并明确EINVAL也可能发生在仍存活且关闭pipe的子进程上；第1563–1595行显示Windows poll/wait使用保留handle获取退出码。路径、SHA和摘录见`sources/CPYTHON_PIPE_REFERENCE.txt`。R24进一步要求**已确认整个精确子进程退出**。

## 操作与政策

| 操作点 | 可接纳错误 | 必备条件 | 处理 |
|---|---|---|---|
| stdin.write | OSError/EINVAL22或BrokenPipeError/EPIPE32；winerror均须缺失 | 原Popen、原pipe、原handle和PID归属一致，错误后poll确认退出 | 保留异常，标记输入控制传输未确认，继续close/wait/输出收集 |
| stdin.flush | 同上 | 同上；缓冲flush进入同一底层write路径 | 独立记录flush结果，继续清理 |
| stdin.close | 同上 | 同上 | 检查实际closed状态，仍开则按同一政策进行最终关闭 |
| poll | 接纳集合为空 | 精确保留的Popen | 原错误保留，退出不明进入RECOVERY_REQUIRED |
| wait | 接纳集合为空 | 固定剩余观察窗 | 超时本身失败；仅精确拥有对象可终止并在既有5秒窗回收 |
| stdout/stderr read | 接纳集合为空 | 已确认退出且原拥有pipe | 各读4097B以检查4096B上限，不完整明确失败 |
| stdout/stderr close、handle close、持久化 | 接纳集合为空 | 精确拥有资源及新RUN | 保留清理异常，继续尽可能完成其他资源关闭并抛回主异常 |

EPIPE32依据固定标准库对BrokenPipeError的处理，R24同时要求实例类型与errno吻合；原历史仅实际见证EINVAL22，EPIPE分支保持待动态覆盖。EBADF9、EIO5及native winerror109/232等均无许可路径，当前未依据本轮材料接纳它们。单独满足poll非None不会通过错误码判断。

## 逐分支纸面检查

1. 原对象被替换、scope不符、PID/handle不符：在I/O前拒绝，不能借其他对象清理。
2. EINVAL/EPIPE且poll为None：记为非预期主错误；存活peer提前关pipe不构成接受依据。
3. EINVAL/EPIPE且精确进程已退出：记录预期竞态，退出码保留，stdout/stderr、pipe关闭和handle关闭仍须完成。
4. EBADF/EIO或任何带未审定winerror的错误：即使已退出也保留并报告。
5. pipe错误之后poll再出错：先保留最初pipe错误，再记录poll清理错误，原主异常顺序保持。
6. wait超时后成功回收：超时仍为失败，无法转换成成功；存在所有权不确定性则保留句柄和RECOVERY_REQUIRED。
7. stdout或stderr读取失败/超限：complete字段为false，有限数据仍保存，原错误传播。
8. 关闭后仍有pipe未closed：显式CLEANUP_FAILED；不会仅凭一次close调用宣称回收。
9. 留证失败：保留原主异常和留证错误；无历史输出fallback，失败记录在可写的新根由runner继续承接。

## 证据字段与原始异常

每个正常注册子进程保留PID、创建FILETIME、SID/image事实、原process handle、原三条pipe对象及创建时fd。异常证据包含操作点、异常类型、errno/winerror、退出码、stdin.closed、原pipe归属、输入控制传输影响及是否预期。

原异常对象及traceback在`rec.exception_objects`保留；公开JSON记录完整类型/错误码和最多1024字符、经canary及临时测试秘密值清理的原异常repr。非预期主异常以原对象/traceback重新抛给unittest。主异常、后续清理异常分列。公开证据保持秘密值边界，内存中的原对象保留与脱敏字段各自注明。

每子进程新增`child_NN_cleanup.json`，与完整stdout/stderr路径、退出码、complete字段、所有pipe/handle关闭结果关联；单次scope.write_new仍受原2MiB上限。至多8份新增诊断文件，包含在原512路径和64MiB额度内。cleanup JSON自身写入失败无法在同一失败文件中自证成功，错误会留在返回的清理记录/原异常链及runner失败记录中。

## 原断言和额外验收

54项测试源文件完全保持。runner增加独立的结果完整性检查：每个worker按原manifest核对预期退出码、stderr为空、输出complete、pipe/handle关闭、没有主/清理错误及没有强制终止。F24正常双方应exit0；X01/crash仍按其故障合同接纳73或74。该检查不增加或替换54个测试ID；它防止F24原单活断言PASS覆盖异常退出或不完整日志。

本政策适用于已完成注册并进入finish_owned_child的F24及同一有限worker清理通道。launch原有注册前错误路径、原生OS不可中断故障和未确认退出情形没有由本次静态复核获得全面运行正确性证明；它们继续保留失败/不确定责任。
