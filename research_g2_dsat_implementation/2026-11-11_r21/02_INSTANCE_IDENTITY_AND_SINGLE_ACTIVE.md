# 实例身份与Authority单活结果

日期：2026-11-11。范围：R21明确批准的九目标及离线合成验收。过程为本对话内模型辅助实现、实际执行与知情复核；外部独立核验待取得。


真实Win32测试核对当前测试宿主的TokenUser SID、PID、创建FILETIME、image，以及新测试目录/文件的最终路径、volume/file-ID与DACL。只处理自身和本轮创建的stub，系统进程枚举0。所测SID属于测试宿主，未来部署SID仍需单独指定。

TestScope仅由核验R21 receipt、请求原文哈希、固定Python和获批输出树的工厂创建。opaque证据/issuer/context保存在进程内registry；请求自报trusted、普通dict及未登记对象安全拒绝。源字节与已加载内部模块__file__/spec.origin均有核对，无法替代硬件内存证明或对恶意同SID代码的隔离。

实例记录把实际根file-ID、UUID、source/config摘要和singleton scope绑定。Store/connection/RLock在同一上下文中检查，替换connection和重复bind均拒绝。P2门始终关闭，新context不发行真实permit。

| 证据 | 结果及范围 |
|---|---|
| F24两个真实stub竞争同一物理lock | 恰好一个LOCKED，一个CONFLICT；都退出后可重新取得 |
| F19/F22异常退出 | 退出码73/74，OS释放拥有锁；partial receipt保留并进入分类恢复 |
| T39继承handle | 父句柄关闭后子句柄继续持锁；父重取拒绝；子退出后可重新取得 |
| T41指定process handle与Event | PID/创建时点不符拒绝，正确Event使拥有stub正常退出 |
| T45/T46同上下文重复start/Store/连接替换 | 一次槽/生命周期拒绝保持 |
| T33路径/DACL | 实际hardlink与file-ID检查；reparse属性通过显式注入检查拒绝，未创建真实junction |
| F25复制 | 真实新加密测试DB复制后，旧根/DB file-ID无法直接复用 |

Win32独占文件handle保护遵守该入口的同物理实例。旧Controller SingleActive保持，Authority新core在构造Store前取得自己的lease。SQL写锁、PID或路径单独出现时无法替代实例所有权。

最终6个stub的process/pipe handle均显式关闭，强制终止0，窗口均隐藏，环境为构造的公开白名单，继承句柄仅T39明确指定的一份。

R16原44项及D1-A24项重新执行通过，原读总量门、并发、重放、issuer/别名保护保持。新LiveContext的受保护读/permit额均0。持久防回滚/防克隆、真实P2接纳和跨进程一次性启动批准均未取得完整证明。

F26和T45的完整跨进程条件在最终合同验收中BLOCKED；它们的同进程单元断言实际通过。具体源码轨迹见07稿，避免把进程内registry提升为持久批准账本。
