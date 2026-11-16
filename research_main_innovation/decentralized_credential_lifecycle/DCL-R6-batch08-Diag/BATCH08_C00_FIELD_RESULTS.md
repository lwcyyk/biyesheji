# C00八项真实字段结果与历史定位边界

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

**C00_PASS**：原生C00 readiness通过并取得Root机器result_C00 PASS；所有最终8项在两轮READY检查中均MATCH。无稳定失配、读取错误或身份变化。

|check_id/编号|字段|expected|首次observed|首次结果|最终双侧observed|最终结果|
|---|---|---|---|---|---|---|
|CR-01|Uid|[999]|None|NOT_READY|[[999], [999]]|MATCH|
|CR-02|Gid|[989]|None|NOT_READY|[[989], [989]]|MATCH|
|CR-03|Groups|[989]|None|NOT_READY|[[989], [989]]|MATCH|
|CR-04|CapEff|0|None|NOT_READY|[0, 0]|MATCH|
|CR-05|NoNewPrivs|1|None|NOT_READY|[1, 1]|MATCH|
|CR-06|LimitAS|1073741824|['1073741824', '1073741824']|MATCH|['1073741824', '1073741824']|MATCH|
|CR-07|LimitASSoft|1073741824|['1073741824', '1073741824']|MATCH|['1073741824', '1073741824']|MATCH|
|CR-08|ControlGroup|/dclr6batch08.slice/dclr6batch08-c00.service|['/dclr6batch08.slice/dclr6batch08-c00.service', '/dclr6batch08.slice/dclr6batch08-c00.service']|MATCH|['/dclr6batch08.slice/dclr6batch08-c00.service', '/dclr6batch08.slice/dclr6batch08-c00.service']|MATCH|

CR-01 Uid、CR-02 Gid、CR-03 Groups来自实际/proc/811/status集合；CR-04 CapEff十六进制转整型0，CR-05 NoNewPrivs为1。CR-06/07来自systemd硬/软AS属性字符串，CR-08来自manager ControlGroup路径；独立辅助门还核对实际/proc/limits soft/hard1GiB、实际/proc/cgroup及parent4tasks/4GiB。

首次manager为STARTING且MainPID811已存在，CR-01…05按冻结合同defer，observed=null/NOT_READY；CR-06…08当时已MATCH。这里没有把未读值当错误或通过，STARTING期间Root票据未发放，controller尚未开始计费probe。随后READY两轮才实际读取五项凭据并得到匹配。

双次读原文与诊断JSON的observed由离线独立parser逐项重算一致，未调用目标collector或修改判据。每项read_time/来源、PID/starttime/boot和证据SHA见[C00_FIELD_ACTUAL](evidence/C00_FIELD_ACTUAL.json)及3份原始ready_C00记录。

**旧batch07具体失败字段仍C00_FAILED_FIELD_UNRESOLVED。** 本轮证实非零MainPID可与合法STARTING并存，并支持加入exec-ready屏障；batch07没有保存同刻UID/GID等值，本轮早期也有意不读最终凭据，因此无法倒推它当时是哪项失配。当前全部MATCH不能重写旧聚合拒绝或认定旧配置错误。
