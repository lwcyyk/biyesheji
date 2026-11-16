# LR：文件系统与持久账路径

2026-11-10。Material Passport：ls/df/既有mountinfo审查；无mkdir/chown/写Linux文件/持久性测试。

## 1. 实际事实

命令25：`/var/lib`为root:root、0755；`/var/lib/dcl-r6`及`/var/lib/dcl-r6/batch02`均ENOENT，exit2。命令26显示其挂载祖先为根ext4，Available=986,347,912个1024-byte块（查询时值）；`/mnt/d`为9p，Available=190,176,216块。该值为文件系统可用空间观测，未认证WSL稀疏VHD的宿主剩余容量/实际可持续分配或磁盘配额。

P阶段mountinfo已给出Windows D盘经DrvFS/9p对应/mnt/d，现有研究报告位于host的D盘。正式Linux预算/状态/journal建议使用ext4内部路径，退出后再跨平台复制封存，按原始字节比较摘要。

失败单位mnt-e.mount与候选路径分开处理。当前不访问/修复/mount该路径；manager degraded和其他失败状态在后续配置前复核。未来首次部署保持相同根文件系统类型、boot_id与所需挂载属性审查。

## 2. 候选目录与权限

L-C静态准备工作区拟为`/var/lib/dcl-r6/lc01`，独立于尚未授权的batch02。根目录TCB拥有；src/inputs/manifest由root写入后只读，专用dcl-r6身份仅能写out下预算/日志。未来batch02使用独立`/var/lib/dcl-r6/batch02`及host封存目录，需对应新授权，不在当前创建。

批准前仅有路径/权限设计。实际UID/GID、目录属主/模式、namespace写入白名单、symlink/路径逃逸防护、可用空间与读写失败停止均待L-C建立及后续校准。Linux看不到/不能写旧batch01的策略须明确，host旧目录与程序原件保持不变。

## 3. 持久性责任

现有v3 write采用临时文件替换，durable_json对文件flush/fsync后replace；尚无Linux目录fsync接线。未来迁移需区分文件持久化、目录项持久化、完整短写检查与崩溃后的模糊意图。建议采用PREPARED→已确认全局额度→COMMITTED的保守流程，rename后同步父目录；任何fsync/锁/短写失败停止grant并封存残片，不回收不确定额度。

ext4提供合适的本地文件系统候选，未证明WSL宿主崩溃/断电时所有写缓存的最终持久性。重启后boot_id不符或日志不完整便关闭原批次、不自动恢复；未来授权的崩溃/中断校准给出实际证据。当前用户态FS读取无法替代这些保证。

host复制用于封存，源/目标路径、时间、完整文件清单和逐文件SHA保持来源链；复制耗时另列，不增加模型工作或刷新deadline。当前只有LR报告/证据和根导航写入，Linux工作目录及两端batch02均未创建。
