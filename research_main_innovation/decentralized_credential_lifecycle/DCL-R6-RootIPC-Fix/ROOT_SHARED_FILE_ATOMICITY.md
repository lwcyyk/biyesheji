# Root 共享文件原子发布与失败语义

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

[root_ipc.py:91 publish](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)采取以下顺序：固定相对目标策略 → 逐级固定目录fd/metadata/ACL → 同设备检查 → Root私有暂存O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC → fd上fchown/fchmod/验证 → 完整write → 文件fsync → dirfd相对replace → 目标目录fsync → 私有暂存目录fsync → 目标lstat与暂存fd的device/inode、owner/group/mode/nlink复核 → 返回。Root输入层和out均被Root父目录固定；目标名字在rename中按目录fd解释。

成功replace的命名原子性、相对目录描述符、不同文件系统可能失败的语义来自[Python3.12 os.replace](https://docs.python.org/3.12/library/os.html#os.replace)与[Linux rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html)。目录项的持久化需要单独目录fsync，依据[fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html)。代码同时同步两个参与rename的目录；完整持久性仍依赖文件系统、存储和可信内核条件。

[open(2)](https://man7.org/linux/man-pages/man2/open.2.html)说明O_NOFOLLOW作用于末分量，因此源码逐级打开目录；新建mode受umask/默认ACL影响，发布前显式设置并拒绝ACL。按fd变更owner遵守[fchown(2)](https://man7.org/linux/man-pages/man2/chown.2.html)语义。Python网页为当前3.12分支文档；实际3.12.3的replace签名/dir_fd接口另由静态命令1/5读取。

|失败阶段|可见状态|后续处理|
|---|---|---|
|创建/元数据/写入/文件fsync失败|原目标保留；私有暂存可能留下|异常上抛；共享预算失败触发原HALTED；保留暂存证据|
|rename失败|通常保留原目标；以原始错误为准|失败关闭；无执行信用交付|
|rename成功后目录fsync/stat失败|新目标可能已可见；持久性/身份未完成确认|返回失败；沿原预算保守占用并停止；禁止退款/回滚伪装|
|目录或目标symlink/hardlink异常|策略/类型/目录检查拒绝；dirfd固定发布目标|不把resolve当作权限依据；动态对抗调度仍待验证|
|重复发布|由现有counter/lifecycle锁串行；字节可相同，inode可变化|幂等信用由原EXACT-RANGE/1提供，publisher自身不制造新信用|

当前/var/lib/dcl-r6位于ext4 `/dev/sdd`，挂载含data=ordered，见[静态环境](evidence/STATIC_NATIVE_SUMMARY.json)。本轮执行原子发布/故障注入0；上述顺序是源码事实，掉电、介质回滚、恶意Root及严格实时行为保留条件。跨目录Root发布比旧路径增加一次目录fsync，开销必须在同一300秒校准中实测。
