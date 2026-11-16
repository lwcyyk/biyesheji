# C00原八项条件与batch07逐字段裁决

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

**C00_FAILED_FIELD_UNRESOLVED**。八项从实际冻结service_confirmed的OR表达式提取，数量与源码逐项绑定，字段定义均有直接源码依据。

|check_id|真实字段|原源码行|expected|原读取来源|batch07 observed/裁决|原拒绝表达式|
|---|---|---|---|---|---|---|
|CR-01|Uid|335|[999]|/proc/MainPID/status|未保存；无直接MATCH/MISMATCH|set(map(int,status['Uid'].split()))!={999}|
|CR-02|Gid|335|[989]|/proc/MainPID/status|未保存；无直接MATCH/MISMATCH|set(map(int,status['Gid'].split()))!={989}|
|CR-03|Groups|336|[989]|/proc/MainPID/status|未保存；无直接MATCH/MISMATCH|set(map(int,status['Groups'].split()))!={989}|
|CR-04|CapEff|336|0|/proc/MainPID/status|未保存；无直接MATCH/MISMATCH|int(status['CapEff'],16)!=0|
|CR-05|NoNewPrivs|336|1|/proc/MainPID/status|未保存；无直接MATCH/MISMATCH|int(status['NoNewPrivs'])!=1|
|CR-06|LimitAS|337|1073741824|systemd show C00 service|未保存；无直接MATCH/MISMATCH|info.get('LimitAS')!=str(G.AS_CAP)|
|CR-07|LimitASSoft|337|1073741824|systemd show C00 service|未保存；无直接MATCH/MISMATCH|info.get('LimitASSoft')!=str(G.AS_CAP)|
|CR-08|ControlGroup|338|/dclr6batch07.slice/dclr6batch07-c00.service|systemd show C00 service|未保存；无直接MATCH/MISMATCH|info.get('ControlGroup')!='/'+G.PARENT+'/'+t['unit']|

八项运行时实际值、读取时刻与C00 MainPID/starttime都未持久化；原检查发生于Root scheduler，但Root PID886不代表C00 MainPID。OR具有短路语义，不能推断每个后续子表达式都曾完成计算。原函数确实取得unit_show与/proc/status对象，当前只剩聚合拒绝和控制流见证。

LimitAS/LimitASSoft来自manager属性，分别指冻结配置硬/软值1GiB；原第八项读取manager.ControlGroup路径。MainPID、ActiveState/SubState、Type、父slice TasksMax、实际/proc/limits和实际/proc/cgroup在新版本中另列为明确标识的辅助门，历史八项定义保持。

历史间接证据：冻结argv请求User/Group与AS，父kernel快照pids.max4/memory.max4GiB，journal为Starting-only；这些不能证明八项中某项匹配或失配。事后不同boot的not-found/default属性全部排除，禁止把LimitAS=infinity填入observed。

[机器逐字段审计](evidence/EIGHT_FIELD_HISTORICAL_AUDIT.json)、[原源码](evidence/original/src/boot_continuity.py)、[batch07原始失败](../DCL-R6-batch07/BATCH07_COUNTEREXAMPLES.md)。
