# batch05 实际命令索引

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

31条native调用的精确argv、UTC起止、原始stdout/stderr及SHA见各result JSON。命令计划在启动前追加，随后保存真实结果；PowerShell封装本身exit0与内部Linux退出码分别记录。实际测试入口仅命令24一次；native resume0。

|编号/argv与双流|分类|实际exit|墙钟ms|用途|
|---|---|---|---|---|
|[01](<evidence/commands/01.result.json>)|B05_PREFLIGHT_READ_ONLY|0|752.138|batch05启动前只读核验1|
|[02](<evidence/commands/02.result.json>)|B05_PREFLIGHT_READ_ONLY|0|268.872|batch05启动前只读核验2|
|[03](<evidence/commands/03.result.json>)|B05_PREFLIGHT_READ_ONLY|0|282.385|batch05启动前只读核验3|
|[04](<evidence/commands/04.result.json>)|B05_PREFLIGHT_READ_ONLY|0|268.370|batch05启动前只读核验4|
|[05](<evidence/commands/05.result.json>)|B05_PREFLIGHT_READ_ONLY|0|279.953|batch05启动前只读核验5|
|[06](<evidence/commands/06.result.json>)|B05_PREFLIGHT_READ_ONLY|0|265.142|batch05启动前只读核验6|
|[07](<evidence/commands/07.result.json>)|B05_PREFLIGHT_READ_ONLY|0|292.230|batch05启动前只读核验7|
|[08](<evidence/commands/08.result.json>)|B05_PREFLIGHT_READ_ONLY|0|258.019|batch05启动前只读核验8|
|[09](<evidence/commands/09.result.json>)|B05_PREFLIGHT_READ_ONLY|0|248.346|batch05启动前只读核验9|
|[10](<evidence/commands/10.result.json>)|B05_PREFLIGHT_READ_ONLY|0|265.822|batch05启动前只读核验10|
|[11](<evidence/commands/11.result.json>)|B05_PREFLIGHT_READ_ONLY|0|258.760|batch05启动前只读核验11|
|[12](<evidence/commands/12.result.json>)|B05_PREFLIGHT_READ_ONLY|1（ps空，预期）|263.565|batch05启动前只读核验12；ps exit1空为无残留|
|[13](<evidence/commands/13.result.json>)|B05_PREFLIGHT_READ_ONLY|0|252.016|batch05启动前只读核验13|
|[14](<evidence/commands/14.result.json>)|B05_AUTHORIZED_RESOURCE_PREPARATION|0|272.994|冻结准备动作1：仅batch05目录或单位|
|[15](<evidence/commands/15.result.json>)|B05_AUTHORIZED_RESOURCE_PREPARATION|0|353.730|冻结准备动作2：仅batch05目录或单位|
|[16](<evidence/commands/16.result.json>)|B05_AUTHORIZED_RESOURCE_PREPARATION|0|296.447|冻结准备动作3：仅batch05目录或单位|
|[17](<evidence/commands/17.result.json>)|B05_AUTHORIZED_RESOURCE_PREPARATION|0|294.915|冻结准备动作4：仅batch05目录或单位|
|[18](<evidence/commands/18.result.json>)|B05_AUTHORIZED_RESOURCE_PREPARATION|0|557.321|冻结准备动作5：仅batch05目录或单位|
|[19](<evidence/commands/19.result.json>)|B05_RECEIPT_OR_FINAL_PREFLIGHT|0|261.450|安装本次batch05授权原文|
|[20](<evidence/commands/20.result.json>)|B05_RECEIPT_OR_FINAL_PREFLIGHT|0|259.114|安装明确批准Root协调器及handoff的新执行收据|
|[21](<evidence/commands/21.result.json>)|B05_RECEIPT_OR_FINAL_PREFLIGHT|0|250.904|专用slice属性核验，保持inactive|
|[22](<evidence/commands/22.result.json>)|B05_RECEIPT_OR_FINAL_PREFLIGHT|0|259.034|新授权/目录权限|
|[23](<evidence/commands/23.result.json>)|B05_RECEIPT_OR_FINAL_PREFLIGHT|0|288.128|T0前当前boot|
|[24](<evidence/commands/24.result.json>)|B05_AUTHORIZED_FROZEN_LAUNCHER|125（首次失败后的最终退出）|300583.932|batch05唯一首次启动：批准Root父协调器/子Launcher、C09H34、C/S/门及资格后的F1/F4；首次关键失败停止|
|[25](<evidence/commands/25.result.json>)|B05_FROZEN_EVIDENCE_EXPORT|0|1684.151|首次关闭后立即按冻结17-unit清单导出本boot全部原始journal；不恢复或重跑|
|[26](<evidence/commands/26.result.json>)|B05_POSTFAILURE_READ_ONLY|0|245.083|首次失败后的真实主账/收据/socket权限，保持原件不变|
|[27](<evidence/commands/27.result.json>)|B05_POSTFAILURE_READ_ONLY|1（ps空，预期）|245.790|关闭后专用UID残留进程；exit1空为正常|
|[28](<evidence/commands/28.result.json>)|B05_POSTFAILURE_READ_ONLY|0|246.501|关闭后的manager状态及PID|
|[29](<evidence/commands/29.result.json>)|B05_POSTFAILURE_READ_ONLY|0|249.704|关闭后parent组不存在核对|
|[30](<evidence/commands/30.result.json>)|B05_POSTFAILURE_COORDINATOR_AUDIT|1（ps空，预期）|320.034|已关闭批次Root父协调器/子Launcher当前存活与阻塞点，仅核当前已记录两个PID|
|[31](<evidence/commands/31.result.json>)|B05_FINAL_FROZEN_EVIDENCE_EXPORT|0|313.254|Root协调器已退出后的补全journal导出，保留25首次导出与最终全部17-unit记录|

命令25保留首次停止后导出的17-unit运行boot journal，命令31保留Root退出后的最终导出；两份都保留。原始stderr中的WSL localhost代理提示属于环境信息；权限错误、C09_NOT_READY和Linux exit125按各原始记录单独裁决。

本报告构造及逐字节核对在host Python运行，属于离线归档操作；没有调用冻结payload、运行模型、发起额外Linux测试或权限修复。生成脚本见[BUILD_REPORTS.py](evidence/BUILD_REPORTS.py)。
