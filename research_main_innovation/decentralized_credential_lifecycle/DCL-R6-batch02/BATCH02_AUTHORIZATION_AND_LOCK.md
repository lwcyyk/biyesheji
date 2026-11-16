# batch02授权与实际锁

2026-11-10。Material Passport：AUTHORIZED_EXECUTION，当前CLOSED_RESOURCE_GATE_FAILED。用户本轮明确许可AS4/CPY312下的冻结校准及资格通过后的F1/F4，无需重复申请。模型门在C02失败后保持关闭。

|对象|实际绑定|
|---|---|
|授权|evidence/BATCH02_AUTHORIZATION_TEXT.txt；原文SHA=2a19a7b0906e8e93336bf6b86de69121288fa581a01dbe47f4c7b4bcc74bef87|
|运行时|Ubuntu-24.04，kernel6.18.33.2-microsoft-standard-WSL2，systemd255.4-1ubuntu8.18；Python3.12.3|
|解释器|/usr/bin/python3.12；e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f|
|静态manifest|cf9442307d99f82dcec8fb542373340f9c2531ca58e9c7aa8be09edf2eab0ebd|
|执行锁|85cd66643b0ee1f933bb035e220591ef0ce4c106e7cc71bf632702cd3b5c0be9|
|身份|dcl-r6 UID999/GID989，唯一组989|
|源码|实际复用/var/lib/dcl-r6/lc01/src；八源及缓存匹配，五业务不改|
|工作根|/var/lib/dcl-r6/batch02；host D:\毕业设计\DCL-R6-isolated-verification\batch02|
|单位|新dclr6batch02.slice、root停止者及实际C00/C01/C02瞬态service；未到达其余case/FORMAL|

启动前53项原生摘要全部一致，含31关键文件、16源/缓存及输入/两个LC单位。旧账/同名根与单位不存在后才创建；新父sliceverify/reload并读回TasksMax4、MemoryMax4GiB。Root收据采用本次真实原文hash，资源资格来源仍由真实OS/完整校准判定。

实际启动为冻结argv：

```text
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/lc01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch02
```

外层WSL进程exit65，耗时300.701767秒。未使用--resume；C09未到达，当前关闭状态不授任何重启或剩余额度使用资格。所有实际命令与双流保存于[evidence/B02_COMMAND_RESULTS.json](evidence/B02_COMMAND_RESULTS.json)，实际子argv/身份/配置在原始ticket/startup/result中。

原WindowsWS4 E2仍UNRESOLVED；本轮只使用已授权AS4普通映射/特殊区单列、TCB与调度假设。没有改源码、输入或执行顺序，没有安装、其他发行版/Docker启动或外发。
