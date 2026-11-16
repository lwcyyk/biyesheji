# 下一项可审批决定：CPY312-UBU24/1＋L-C静态配置与适配

2026-11-10。Material Passport：REVIEWABLE_REQUEST，当前UNAUTHORIZED。本申请依据LR任务§3.3、§7、§8、§9，L-R只读审查已经完成；原AS4/P/3.14及历史结论保留。

## 1. 请求批准的范围

建议明确批准CPY312-UBU24/1候选进入L-C：使用现有`/usr/bin/python3.12`（3.12.3、包3.12.3-1ubuntu0.17、SHA256=`e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f`），免安装/下载/改默认Python。L-C仅配置准备、资源三文件静态接入、语法/单位文本校验与最终锁；不启动payload单位、不运行资源探针/动态校准/业务导入/F1/F4。

随后依真实L-C产物提出batch02申请。当前没有最终资源代码/hash/命令锁，也没有有效的资源资格收据，因此此申请不包含batch02执行许可。

## 2. 精确写入范围

|对象|允许的拟议变更|
|---|---|
|账户/组|仅新建dcl-r6专用system用户/同名组；UID/GID由系统空闲分配，结果锁定；已有同名变化即停止|
|账户数据库|useradd正常管理的passwd/group/shadow/gshadow及配套锁；禁止读取/输出秘密字段，不修改既有账户|
|Linux工作区|/var/lib/dcl-r6/lc01下src、inputs、reports、out；TCB根目录root:dcl-r6/0750，out专用身份/0700|
|源码|仅新工作区guard.py、guard_probe.py、run_batch.py允许修改；五业务文件原字节复制、hash逐项核对|
|配置|仅/etc/systemd/system/dclr6lc01.slice与dclr6lc01.service；无[Install]自动启用；允许daemon-reload加载inactive配置|
|行政编译输出|仅LCsrc/__pycache__中的八文件cpython-312字节码；原源码hash保持|
|host准备/证据|D:\毕业设计\DCL-R6-isolated-verification\lc01及研究DCL-R6-LC；仅本轮源码副本、diff、配置/授权/锁/报告|
|保持未创建/未运行|两端batch02、原batch01所有文件、既有系统单位和服务；无默认Python变更|

未发现需要新增依赖。若工具缺失、runtime/包/摘要变化、同名对象已存在、关键manager故障或权限不足，则停止相关步骤形成具体差异；不自行安装或扩展配置范围。

## 3. 拟议关键动作与校验argv

以下只供后续授权审阅，当前均未执行。Linux命令统一经固定Ubuntu-24.04的wsl --exec独立argv调用；所有写入前再次核对批准根、已有对象和源hash。

|阶段|具体命令/操作合同|
|---|---|
|工具/身份前置|ls -l /usr/sbin/useradd /usr/bin/install /usr/bin/systemd-analyze；getent passwd dcl-r6；getent group dcl-r6；sha256sum /usr/bin/python3.12|
|仅两身份条目仍缺失时|/usr/sbin/useradd --system --user-group --no-create-home --home-dir /var/lib/dcl-r6 --shell /usr/sbin/nologin dcl-r6|
|TCB目录|/usr/bin/install -d -m 0750 -o root -g dcl-r6 /var/lib/dcl-r6 /var/lib/dcl-r6/lc01 /var/lib/dcl-r6/lc01/src /var/lib/dcl-r6/lc01/inputs /var/lib/dcl-r6/lc01/reports|
|payload可写位置|/usr/bin/install -d -m 0700 -o dcl-r6 -g dcl-r6 /var/lib/dcl-r6/lc01/out|
|源码/单位安装|从新host LC工作副本逐文件传入；只限上述8源码与2单位文本，TCB源只读；保留精确来源/diff/复制前后hash|
|语法校验|/usr/bin/python3.12 -I -S -B -m py_compile /var/lib/dcl-r6/lc01/src/guard.py /var/lib/dcl-r6/lc01/src/guard_probe.py /var/lib/dcl-r6/lc01/src/run_batch.py /var/lib/dcl-r6/lc01/src/f1_model.py /var/lib/dcl-r6/lc01/src/f1_check.py /var/lib/dcl-r6/lc01/src/f4_dp.py /var/lib/dcl-r6/lc01/src/f4_reference.py /var/lib/dcl-r6/lc01/src/compare.py|
|单位文本校验|/usr/bin/systemd-analyze verify /etc/systemd/system/dclr6lc01.slice /etc/systemd/system/dclr6lc01.service|
|加载与只读验收|/usr/bin/systemctl daemon-reload；随后show两个单位的LoadState/ActiveState/Slice/AS/Tasks/Memory/Kill/Restart/权限属性；无start/enable|

编译只做语法/字节码处理，不执行八文件模块正文；py_compile会显式写__pycache__，即使-B也需上述写入许可。它无法证明导入、业务语义、内核限制或资源资格。创建/装入单位同样不等于限制已经作用于活进程。

## 4. 单位/身份属性设计

父slice为根直接子slice，TasksMax=4、TasksAccounting=yes、MemoryAccounting=yes、MemoryMax=4294967296（次级charge保护）。service的Slice=dclr6lc01.slice，Type=exec，直接ExecStart固定3.12的-I -S -B与LCsrc/guard.py，无shell/ExecStartPre/ExecStop；User/Group=dcl-r6，LimitAS=1073741824:1073741824，TasksMax=4，MemorySwapMax=0，OOMPolicy=kill，OOMScoreAdjust=0，LimitCORE=0。

Restart=no、RemainAfterExit=no、Delegate=no、KillMode=control-group、KillSignal=SIGKILL、SendSIGKILL=yes；RuntimeMaxSec=1740仅辅助，TimeoutStartSec=15、TimeoutStopSec=5。L-C不启动此service，外部绝对停止事件的完整接口/文本须在静态交付中补齐并列入下一批最终锁。

能力/ambient清空、NoNewPrivileges=yes、ProtectSystem=strict、ProtectHome=yes、ProtectControlGroups=yes、PrivateDevices=yes、PrivateTmp/PrivateNetwork、RestrictNamespaces=yes及RestrictAddressFamilies=AF_UNIX；源码/runtime只读、仅out可写，屏蔽/mnt、/init、/dev/hugepages、WSL管理库及systemd/D-Bus/用户manager代理入口。具体路径存在性和属性兼容性先审后冻结，缺关键封闭条件即停止，禁止静默删减安全属性。特殊映射/A4仍须单独审计。该设计针对固定验证程序/故障模型，任意恶意代码沙箱的一般保证仍未取得。

## 5. L-C完成与batch02下一门

L-C交付：新源/单位/diff/hash、五业务一致证明、语法/配置结果、实际UID/GID/目录权限、runtime闭包和所有最终管理/启动/停止命令、首入口/AS/任务/角色/特殊映射/计时责任。原v3及失败原件完全保留。失败时保留已做变更与日志，停止，不自动清理历史或新开窗口；清理仅限经批准的新对象。

未来batch02另申请：固定平台/启动身份/runtime/八源/输入/命令、统一100万访问与1800秒窗口、AS4完整内存条件及C00–C12真实校准。语义独立验收和正式F1→F4均包含在获准的总账；资源资格通过后才可业务运行。

本轮只提出这项具体申请，没有执行useradd/install/reload/py_compile/verify，也没有创建上述工作区或单位。主机制门CLOSED、严格分离0继续保持；候选凭据机制实施仍须先有可证伪分离声明与必要代价实例。
