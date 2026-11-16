# Root/Payload 最小权限与职责合同

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

采用固定路径的三类发布策略，复用通用私有暂存及目录fd方法。对最强通用基线预测差距0；[研究分离门](SEPARATION_AND_SCOPE.md)保持关闭。

A类共享对象：预算intent由999与可信Root审查共同推进，目标999:989/0600，双方仍使用原counter flock。C09 ready由payload产生，Root按ticket/身份/原账核验；C09 sender为Root scheduler，payload无需获得控制socket写权限。

B类Root私有对象：内部事件、普通waitpid记录及IPC原始审查置于root_private/0700，文件0:0/0600。Root原始记录只由独立检查器读取；合成fixture无法写入真实counter/CLOSED等路径。

C类Root保护且payload必读的收据：C09状态、commit/退出见证、C09H/IPC/RANGE/GATE/RESOURCE资格为0:989/0640，输入目录0:989/0750。payload可核验原资格与摘要，写入/删除由Root输入目录边界阻断。活receiver的RPC确认仍是持久commit之外的必要条件。

实现位于[root_ipc.py:21 policy](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)、[root_ipc.py:72 directories](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)及[root_ipc.py:91 publish](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)。Root目标采用精确名单；仅IPC合成固定文件名放行故障钩子；真实全局账故障注入继续拒绝。每级目录逐项O_DIRECTORY/O_NOFOLLOW打开，校验owner/mode、设备及无POSIX ACL。发布前fd上fchown→fchmod→metadata/ACL校验，避免umask或继承ACL改变预期授权。

审查结果：payload缺少Root私有目录访问权及保护收据写权；socket仍0:0/0600，SO_PEERCRED、稳定PID/boot、窗口与锁摘要保持；Root发布路径无需接收任意用户指定路径；迟到ACK受CLOSED吸收及fresh-read约束。原预算审查对payload可写内容的信任继续依赖冻结payload/原健康账验证，任意恶意同UID程序和Root/内核失陷超出现有边界。

更强威胁实例：恶意同UID写者可在原预算读取前替换intent路径，旧`read`仍是普通路径读取；同时也可篡改其拥有的counter。本轮Root发布不会跟随该链接写到外部目标，原预算读取核心保持。对任意恶意同UID的完整读路径/账真实性保证仍为UNRESOLVED；扩大该模型需要单独批准预算I/O重构。本轮没有作出这一扩展保证。

RI-2=CONDITIONAL_PASS：源码权限边界已实现；实际DAC、ACL拒绝、原子替换失败行为和跨身份回归全部UNRUN。未来batch06预检及内置目录检查拒绝未审查ACL/目录元数据变化。当前只读审核的源目录和/var/lib/dcl-r6前缀无POSIX ACL，运行目录尚未创建。
