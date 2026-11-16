# 诊断结论、旧字段未决与观测缺口

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

本轮没有新的C00稳定身份/资源失配、读取错误或不安全READY见证。真实路径为STARTING→READY→再次READY→原C00 probe PASS→47安全/17变异接受→C00_DIAGNOSTIC_COMPLETE关闭。17个合成错误见证是预期检测成功，不能视为生产代码被观察到相同失误。

旧batch07失败原因继续未决。当前首次STARTING只实际观察manager AS/CG匹配，最终凭据被有意defer，历史中缺失的Uid/Gid/Groups/CapEff/NoNewPrivs值无法补齐。结构性“MainPID存在且exec尚未确认”在本轮真实出现，支持原就绪竞态假设；无法唯一定位旧8路OR的真实触发项。

新增/保留观测缺口：READY包含pidfd与前后身份检查成功的控制流证据，但独立pidfd检查时间、后侧starttime原始stat和wait_native精确返回时刻未打点。八字段与双源读取原件完整，D08-4总体保守记FIELD_EVIDENCE_PARTIAL。将来需要细粒度时序证明时，可独立静态增强这些打点；当前禁止为补记录修改源或重跑本批。

当前没有凭空修复某个UID/AS字段的依据。后续可以准备完整条件链的独立版本/执行准入，同时保留测时责任；已经CLOSED的batch08不能恢复或自动转换Full。源含固定batch08命名，新独立批次需要匹配命名/摘要/锁及明确Full批准，当前没有创建batch09，也没有自动进入任何后续项目。

总体结论只涉及已运行的C00和获准64，未新增F1/F4模型安全结论。[字段实值](evidence/C00_FIELD_ACTUAL.json)、[时序区间](evidence/READINESS_TIMELINE.json)、[独立检查](evidence/REGRESSION_REFERENCE_CHECK.json)。
