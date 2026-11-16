# F24实际修复验证

执行与审查日期：2026-11-12（Asia/Shanghai）。证据类型：本对话内知情模型辅助实际离线运行、源码/日志核对；外部独立核验待取得。

**F24_FIX_VERIFIED=true，范围为本轮真实同实例竞争及已触发的EINVAL22清理路径。** F24执行PASS，6条冻结内部断言全部满足；原断言和预期保持。

## 两个真实拥有进程

| 角色 | PID | 创建FILETIME | admission | 退出码 | 亲本拥有窗口 |
|---|---:|---:|---|---:|---:|
| 胜者 | 63148 | 134389255173820729 | LOCKED / true | 0 | 1.047s |
| 败者 | 44172 | 134389255174376717 | CONFLICT / false | 0 | 1.016s |

创建与退出均由本轮creator journal记录，PID/创建时点/SID/image绑定原拥有Popen。败者异常行另记录原pipe身份校验和创建时stdin/stdout/stderr fd为7/8/9；没有用外来对象代替stdin。

## 实际操作序列

| 败者操作 | 本轮结果 | 接受证据 |
|---|---|---|
| stdin.write | OK | 写入缓冲成功；不据此推断peer已接收 |
| stdin.flush | OSError22 / winerror=null | 错误后poll返回exit0，原pipe归属已核对 |
| stdin.close | OSError22 / winerror=null | 再次poll返回exit0；异常后stdin.closed=true |
| wait | OK，exit0 | 精确保留Popen完成wait |
| stdout/stderr收集 | complete=true | stdout完整CONFLICT结果，stderr 0B |
| pipe与process handle关闭 | true / true | 原对象关闭，清理状态COMPLETE |

两条错误均保留`OSError(22, 'Invalid argument')`的原repr、类型、errno、winerror、操作点、退出码和stdin状态；expected=true完全符合R24允许集合。它们标记stdin控制信号传输未确认，败者本已退出；没有把未确认输入解释为额外成功接纳。

本轮胜者write/flush/close均为OK；双方primary_error=null、cleanup_errors=[]、强制终止false。双方正常退出后F24重新取得同物理instance锁，完成末条冻结断言。

## 授权与支撑证据

F24持久链重新核读为UNCLAIMED→CLAIMED→STARTED→FINISHED，仅一个CLAIMED、一个STARTED、一个effect。链摘要、模式计数、原文件引用及全部pipe操作在`R25_F24_WITNESS.json`。

原始`child_05_cleanup.json`、`child_06_cleanup.json`及stdout/stderr保持在run根；完整最终清理结果也存在RESULTS.owned_children。独立cleanup文件在写入自身完成前序列化，因此其中不包含最后的cleanup.persist成功行；文件存在、摘要以及最终RESULTS中的成功行联合提供写入完成依据。

## 动态覆盖边界

这次确实触发原相关close异常，同时触发flush异常，取得原R22缺少的实际分类/退出/回收证据。EPIPE32、EBADF9、EIO5、native winerror、存活peer提前关闭pipe、poll或日志失败等分支本轮未额外注入，继续标为静态审查依据。未扩大为所有错误码及任意OS故障的动态验证结论。

本轮没有任何新增F24单项运行或第二轮suite；原R22 ERROR和旧堆栈继续原字节保存。
