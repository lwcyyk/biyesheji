# F24关闭竞态修复的静态验收

审查日期：2026-11-12（Asia/Shanghai）。过程：本对话内知情模型辅助静态源码、历史记录与文档取证；本轮运行证据为零，外部独立核验待取得。

## 裁决

**PATCH_PRESENT；PATCH_SCOPE_VALID=FALSE；F24_FIX_VERIFIED尚未成立。** F24本轮为NOT_RUN。阻塞发生在suite启动之前，原授权额度保持可用。

## 原始失败与版本

原始证据：`D:\毕业设计\research_g2_dsat_implementation\2026-11-11_r22_d1b1_closure_offline\new54_001\stdout.log`第57–68行；同run的`RESULTS.json`保留完整堆栈与F24 ERROR。

```text
F24 -> self.finish(one); self.finish(two)
finish_owned_child -> process.stdin.close()
OSError: [Errno 22] Invalid argument
```

补丁引用：`D:\毕业设计\research_g2_dsat_implementation\2026-11-11_r22\sources\PIPE_CLOSE_FIX.diff`；摘要`3bfb405bf8ec1604873e49b8d7273d23bee21739b1248192064155eb6adfe459`。避免复制历史源码。Windows文件：

- 首轮版本：`d937297ce4ecb64837b816da3aec3e70cce9bf5a4b420f45bbe86baf7c3b04d9`。
- 当前版本：`0df81f8aba187ac3e4623ee436295e05e15179fc822e8a2d2416348810c91123`。

历史F24观察到一方LOCKED、一方CONFLICT。胜者PID102532/创建FILETIME134388889324360800；败者PID97484/创建FILETIME134388889324880575。两者最终创建者退出记录均为0、stderr均0，stdout完整文件保留。原F24异常时刻缺少单独的poll/句柄快照，最终退出记录不能固定该时刻的stdin.closed值或内核退出时点。败者17.953秒为亲本观察/推迟回收窗口，内核寿命未单独测量。

## 已具备的保护

`finish_owned_child`第545–597行核对Popen在当前scope的拥有表内并拒绝finished重入；操作前检查stdin.closed。补丁在close抛错时要求该保留Popen的poll结果已经有退出码。该结果会保存到returncode，随后wait、读取限长stdout/stderr、写拥有日志并关闭pipe/process handle。CPython3.12.14本机`Lib/subprocess.py`第1563–1595行核对Windows poll/wait依赖保留进程handle和GetExitCodeProcess。

这些是静态正常路径结论；本轮未取得新的退出/清理见证。最后再次close各stream是正常资源回收中的幂等关闭意图，首个close异常后的实际stream状态未被历史记录完整捕获。

## 需要收窄的接受条件

关闭处理块捕获`(BrokenPipeError, OSError)`，仅以`poll()!=None`判断接纳。函数未检查errno/winerror，也未记录被接纳异常的类型、错误码和stdin最终状态。此前write/flush处理还有一处同类`except ...: pass`。

纸面控制流检查：假定当前Popen确属本scope、子进程已退出、stdin.close抛出非预期`OSError(errno=5)`且stream随close进入closed状态。现有close处理块会通过poll判定并继续，错误类别未保留。此分析没有执行故障注入，也未声称真实F24已遇到该错误。它足以指出本轮要求“非预期I/O异常持续暴露”的未满足前提。最终stream重复close是否抛错随状态变化，无法作为错误分类的保证。

未来修订需把预期退出竞态的可接受错误集合和证据条件写清；其余异常持续传播/进入明确失败，并在安全清理后保留主异常、真实退出码和原始输出。任何新修订都需单独授权。

## F24冻结断言的范围

F24第305–311行核对LOCKED/CONFLICT、调用双方finish并重取锁。finish辅助函数核对没有强制终止、pipe与process handle已关闭，保存退出码/日志；F24本身没有断言两方退出码都等于0或stderr为空。故未来即使冻结F24显示PASS，仍需用实际双方记录独立检查异常退出与完整输出，才能作本轮增强验收。本条是审查发现，原断言保持原字节。

同时，补丁异常块没有独立分支计数/异常见证；单个正常F24完成只能支持其实际覆盖的路径。不存在异常日志时，应分别陈述真实清理成功和异常接纳分支的静态依据。

## 当前责任与处理

当前需要独立审批的最小修订责任：收窄close及关联write/flush的错误接纳与记录；保留主异常及精确拥有资源的清理；让R23证据根/授权入口可审查且旧索引保持；按双方实际退出码和完整日志执行结果验收。此责任清单没有授予实现权限。源码、测试、预期和R22记录均保持。
