# LC：inactive资源单位

2026-11-10。Material Passport：STATIC_CONFIGURATION_PASS。实际文本副本位于host lc01/units；Linux安装仅两个获准单位。命令22 verify=0，25为一次授权的daemon-reload；26/27/50读回均inactive/dead，service MainPID=0、ControlGroup为空、UnitFileState=static。

|字段|实际静态值|
|---|---|
|父slice|dclr6lc01.slice，根直接子slice；TasksMax4、MemoryMax4294967296、两Accounting=yes|
|service|dclr6lc01.service；Type=exec；Slice=dclr6lc01.slice；User/Group=dcl-r6|
|AS双限|LimitAS/LimitASSoft=1073741824|
|二级保护|MemoryMax4294967296、MemorySwapMax0、OOMPolicykill、OOMScoreAdjust0、LimitCORE0|
|停止|Restartno、Delegateno、KillModecontrol-group、KillSignal9、SendSIGKILLyes|
|时限|启动15s、停止5s、RuntimeMax29min；仅静态配置值|
|身份/访问|NoNewPrivilegesyes、capability/ambient为空、ProtectSystemstrict、ProtectHomeyes、ProtectControlGroupsyes|
|隔离|PrivateDevices/Network/Tmp=yes；RestrictNamespacesyes；地址族仅AF_UNIX|
|写入|仅lc01/out；/mnt、/init、hugepages、WSL库和管理socket/用户manager入口被列为不可访问|

UnsetEnvironment同时清除预加载/库路径/审计及Python路径变量，防止这些入口改变固定映像。该值已读回，与-I/-S及固定源码路径共同构成候选启动合同。

ExecStart为固定Python -I -S -B执行lc01/src/guard.py --role controller --batch-root /var/lib/dcl-r6/lc01 --case C00。LC根缺动态授权且代码仅接受batch02动态范围；静态部署不包含任何启动许可。没有[Install]、enable或restart操作。

目标Exec前AS/UID/namespace设置、后代继承与父总task4有官方接口依据，但当前没有活进程/enforcement证据。三角色主线程＋监督线程＋W预计占3task，子探针占第4槽；全部子service同一父总限制。cgroup memory是charge次级保护，允许暂超的官方边界继续适用。

外部停止服务仅在未来batch02申请中列出，其root角色在payload父slice之外，使用CLOCK_BOOTTIME、pidfd及固定绝对时限；未知Launcher退出关闭整树。C09唯一预声明故障后允许同boot/T0/账的一次恢复，Parent组代次变化和charge峰值分别留证。当前没有创建/启动该停止服务或任何瞬态case单位。

既有失败范围仍为mnt-e.mount，保持原状；未访问/mount /mnt/e。没有修改其他单位。官方systemd255支持与本机属性读回分开登记，verify及inactive读回无法授RESOURCE_GATE_PASS。
