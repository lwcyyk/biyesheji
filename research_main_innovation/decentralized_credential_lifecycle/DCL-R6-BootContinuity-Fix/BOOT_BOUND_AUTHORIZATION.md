# 同boot一次性启动资格与执行凭据

Material Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。

启动资格同时绑定batch07、当前boot_id、同一Owner PID/start_ticks、source manifest、执行锁、授权原文摘要、Boot合同、当前Root cgroup和初始有效期。资格由新boot的真实观测生成；旧记录仅保留历史，不改写为当前代次。

[boot_continuity.py:225 prepare_activation](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)在受保护Root私有目录创建`activation.json`（O_EXCL）与排他flock，任何失败保留已认领状态。持久claim先于exec：包含nonce、完整ticket、initial_entered和resume_issued。没有第二个初始激活入口；ROOT已存在或已有state/counter/CLOSED即拒绝。

ticket还写入带WRITE/GROW/SHRINK/SEAL封印的memfd，fd和lock fd显式设为跨exec继承。Guard验证封印、内容摘要、设备/inode、当前持锁文件身份、Owner和boot，再把initial_entered持久化为true。普通JSON或环境变量中的数字单独不足以形成资格。检查点：[boot_continuity.py:284 read_capability](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)、[boot_continuity.py:299 guard_admission](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)。

内核对象随原进程/实例结束而失去存活见证，持久claim则保留。新boot即使复用相同PID/start_ticks也不满足boot相等；新入口遇到已准备批根/原claim/预算拒绝。memfd/sealing及exec fd继承参考[Linux memfd_create](https://man7.org/linux/man-pages/man2/memfd_create.2.html)、[execve](https://man7.org/linux/man-pages/man2/execve.2.html)，实际平台兼容性待授权验证。

C09预定退出23仍由原持久ACK、receiver、父waitpid、fresh-read和一次分类机制证明。只有原Guard返回验证后的23，外层同一Root进程才进行一次内部resume；新认领位先消耗，原T0/deadline/stop_at和counter读取核对，原handoff.resume_admission保留。初始10秒期限只作用于首次激活，内部恢复使用原运行窗口，无法得到新T0或新预算。

Root/Windows操作员继续属于TCB，授权文件沿用原可信操作流程与受保护安装；本版没有宣称能抵抗恶意Root或伪造Windows操作员。新执行授权必须明确接受单会话exec、同进程C09恢复、source-only封装与预检TCB界。
