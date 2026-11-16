# LC：专用身份与持久工作区

2026-11-10。Material Passport：已获准的有限配置＋只读验收。创建前getent用户/组及目标目录/单位文件均缺失；没有覆盖同名资产。

|对象|实际结果|
|---|---|
|账户/组|dcl-r6，UID999，GID989，唯一组989；用--system --user-group --no-create-home、nologin创建|
|TCB目录|/var/lib/dcl-r6及lc01、src、inputs、reports为root:dcl-r6/0750|
|可写输出|/var/lib/dcl-r6/lc01/out为dcl-r6:dcl-r6/0700|
|源码/输入|root:dcl-r6/0640，payload只读|
|编译缓存|src/__pycache__为root:dcl-r6/0750，八pyc为root:dcl-r6/0640|
|单位文件|/etc/systemd/system/dclr6lc01.slice、.service为root:root/0644|
|host工作副本|D:\毕业设计\DCL-R6-isolated-verification\lc01，保存八源、单位和输入/锁|

命令10为批准的useradd，11为id结果，12/13为目录创建，28/51为权限读回。没有读取shadow/秘密字段，账户采用无密码参数的系统创建流程。py_compile显式生成缓存后，仅调整批准的八pyc与缓存目录的组/权限，保持root拥有。

Linux活账未来留在ext4本地；当前out未初始化任何访问账/批次窗口。预算格式保留8字节头＋used/cap的两个小端uint64，采用线程锁＋fcntl文件锁、PREPARED/COMMITTED意图、完整写/fsync/目录fsync。模糊预留毒化后续准入，未用预付信用不回收。子探针的有限操作由Controller先收费，处理数必须≤预付上界；总访问保证采用持久占用的保守上界。

预算与日志组件在payload内计量；系统manager、外部Launcher/停止服务、pre-exec助手及平台TCB单列。普通UID没有单位文件写权限，namespace配置限制组写入/管理代理。实际MAC/namespace/锁和故障行为仍待后续校准，当前权限核对只依据真实属主/模式/配置。

本轮具体创建的是lc01。Linux /var/lib/dcl-r6/batch02与host batch02保持未创建；下一阶段创建新根须另行许可。host复制只用于静态副本/后续封存，复制前后保留原始字节hash，历史batch01只读保留。

WSL在准备期间boot_id发生变化，静态文件与账户持久保留；各快照的原始标识本地保存。未来计时状态绑定启动时实际boot_id，拒绝旧时标/自动补窗。ext4宿主崩溃持久性与停止响应尚无校准，不能由mkdir或fsync代码推出运行资格。
