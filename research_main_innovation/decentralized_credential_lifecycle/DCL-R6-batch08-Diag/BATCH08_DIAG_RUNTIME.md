# 运行时、资源边界与关闭

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

原生CPython3.12.3 `/usr/bin/python3.12`、SHA e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f；native artifact_check及内存语法编译完成，冻结kernel/systemd/架构/来源断言通过，systemd输出255.4-1ubuntu8.18、page4096。没有安装依赖或修改WSL全局配置。

Root协调器438/start4792，scheduler796/start4949，C00实际进程811/start4978；boot均0cc7ff50-243e-41d0-bf3f-ba45b3f95695。C00 startup中的RLIMIT_AS soft/hard均1073741824，实际kernel/proc和manager值已取证。after-watchdog组观测pids.current=3，父pids.max4/memory.max4GiB；观察charged peak=43937792B（41.90234375MiB），精确树RSS及Root峰值未认证。

|run-boot journal单位|MONOTONIC µs|原始消息|
|---|---|---|
|dclr6batch08-stop.service|49576360|Starting dclr6batch08-stop.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/cr01/src/guard.py --role external-stop --batch-root /var/lib/dcl-r6/batch08...|
|dclr6batch08-stop.service|49577165|Started dclr6batch08-stop.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/cr01/src/guard.py --role external-stop --batch-root /var/lib/dcl-r6/batch08.|
|dclr6batch08-c00.service|49824658|Starting dclr6batch08-c00.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/cr01/src/guard.py --role controller --batch-root /var/lib/dcl-r6/batch08 --case C00...|
|dclr6batch08-c00.service|49853222|Started dclr6batch08-c00.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/cr01/src/guard.py --role controller --batch-root /var/lib/dcl-r6/batch08 --case C00.|
|dclr6batch08-c00.service|50206928|dclr6batch08-c00.service: Deactivated successfully.|
|dclr6batch08-stop.service|59834021|dclr6batch08-stop.service: Main process exited, code=exited, status=125/n/a|
|dclr6batch08-stop.service|59834154|dclr6batch08-stop.service: Failed with result 'exit-code'.|

批次按C00_DIAGNOSTIC_COMPLETE正常关闭，T0+10.267560352，首次组空T0+10.275995718；普通父waitpid raw0/exit0，Windows WSL子进程exit0。事后UID999/Root角色为空、父cgroup不存在。事后boot=84029165-9734-4479-8ea1-10d14af113cd的not-found/default单位属性仅作清理观察，不拼入旧运行资格。

14秒屏障只接受获准暂态，300秒/1800秒窗口及原AS4-PAYLOAD/1解释保持。C00与模拟安全检查通过仍缺其余C/S/H/完整门，资源总资格未取得。
