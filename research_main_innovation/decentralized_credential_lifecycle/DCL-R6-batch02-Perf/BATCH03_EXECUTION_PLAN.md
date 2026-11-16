# batch03计划：先静态修复锁，再独立运行许可

Material Passport：PLAN_ONLY，batch03=UNAUTHORIZED_NOT_CREATED。本轮仅写研究文档/派生CSV与JSON，没有代码、单位或执行目录。

## P-R03静态修复阶段（需新许可）

候选准备根为host `D:\毕业设计\DCL-R6-isolated-verification\lc03`、Linux `/var/lib/dcl-r6/lc03`，当前均未创建。仅复制正确batch02/FROZEN_LC的八文件；五业务字节不变；新guard/probe实现A0，run_batch只作版本/根/锁接线。Runtime仍CPY312-UBU24/1，AS4/UID999/GID989与已知依赖沿用，重新核现场漂移，不安装依赖。

必须改的真实位置：guard.reserve_counter支持正整数amount、global/phase cap锁内检查、范围owner/epoch、一致意图/短写、持久后截止复核；Budget新增精确prepay接口；guard_probe.prepaid_child替换N次同步循环、单次委派/操作上界/失败不重试；补每阶段真实开始/返回时间及grant/child事件。现有case/AS映射/权限/计时/故障矩阵保留。

现源码硬编码ROOTS、batch02授权ID、unit/stopper名及父根；batch03无法只换argv运行。新版本必须独立命名、移除对旧B02写入资格，保护历史。修复后才核代码/pyc/单位/输入/所有argv摘要。当前无法提供尚未获准编写的新源码hash，不能伪造最终执行锁。

## 新B03独立执行阶段（需再批准）

执行根为`D:\毕业设计\DCL-R6-isolated-verification\batch03`与`/var/lib/dcl-r6/batch03`，当前未创建。父slice拟为dclr6batch03.slice，固定case/formal/独立停止者命名为dclr6batch03-*.service，最终逐名展开进锁。单批1000000访问、1800秒、1740提前停、每进程AS1GiB、父总tasks4；主选cal100000/300保持。

|顺序|必须实际完成/证据|
|---|---|
|环境/源锁|实际kernel/boot/systemd/runtime/UID、全祖先/源/输入/单位/argv，唯一B03身份；拒绝残余旧账|
|入口C00/C01|实际限制/映射/身份/组/停止/正常路径；不复用B02局部PASS当新资格|
|C02|一次精确N持久范围→交付→**真实allocator child启动并结束**；localAS96MiB、持有/释放计量、实际操作≤N|
|C03/C04|范围委派、共享/继承、第五task；全部角色同一父界|
|C05/C11|保留旧17单步测试，新增范围不交叠/不足拒绝/完整故障点；真实总账不注入破坏|
|C06–C12其余项|绝对时限、C/W/Launcher故障、逃逸/代理、身份/关闭/恢复；同账同窗，无免费新窗|
|资格/兼容|原件与hash齐备才授相同锁的资源资格；受限环境中验证五业务接口/语义条件|
|F1→F4|原域/顺序/不变量/费用与独立参考/重放/G64/变异，使用统一剩余额度|
|关闭|到期/失败/未知即停，确认整树退出，封存实际日志/时间/额度/范围/ZIP|

遥测保存lock/check/各sync开始与返回、范围R前后、grant_emit、child_spawn/ops/exit，使用有界缓冲汇总，写不出来标未知并依fail-closed规则停止；不把测量日志变成另一条逐事件同步路径。所有诊断工作及信用都包含在同批1000000/1800与cal软预算，不能另起免费微基准。

可选最小诊断点为C05局部镜像中amount1/17/128与并发9+9/9+8、C11的范围故障；C02自身是N32896的大范围真实性/性能验证，无需复制大规模额外压力输入。静态目标完整cal最大预付约3.7万信用量级（4KiB假设），仅是计划上界；以最终源码/真实页大小和账核对为准。

## 可审的拟议入口与停止条件

拟保留外层接口：

```text
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/lc03/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch03
```

这是未来接口合同，当前程序尚不存在，不能声称现在可执行。只有修复/编译/属性静态验证和全命令hash锁实际完成，才提交最终B03启动/恢复/校准/正式/封存命令。任何未填实的源码/命令字段阻止新执行许可。

任何关键FAIL/INCONCLUSIVE/信用不明/限制失效/错误输入源立即停止。C02仅完成预付仍UNRUN_MEMORY_CHILD，不授PASS。软窗口450/600只是备选新合同差异，当前主选不变更；未来如需改变，另批并计算模型剩余active时间。当前batch02仍关闭、原32191不回收，batch03目录/账/程序/单位全未创建。
