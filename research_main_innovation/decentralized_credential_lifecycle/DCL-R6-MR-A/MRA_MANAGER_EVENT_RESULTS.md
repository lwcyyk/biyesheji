# systemd manager事件结果

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

冻结预检进行了3次MR_PREFLIGHT_REVIEW，实际失败单位集合均仅含mnt-e.mount，按既有基线规则接受，整个过程只读。事后failed集合仍仅mnt-e.mount，没有本批C06/C07/C09服务退出事件，历史batch09单位实例分支本次没有触发。

manager版本、当前boot、Root/权限及源/工具摘要由原生预检fresh核对，systemd查询正常返回。实际错误来自初始MR query先调用RootIPC运行态检查点，检查点要求batch_state.json存在；该文件本应在后续初始化中创建。它与过去的UNREVIEWED_MANAGER_FAILURE是不同的新初始化顺序错误。

本次未生成本批管理器退出审查证书，也没有真实C09后恢复证据。UNREVIEWED_MANAGER_FAILURE处理正确性保持UNRUN，不能用基线mnt-e被接受替代本批预期退出或异常退出验收。

[实际manager摘要](evidence/MANAGER_EVENT_ACTUAL.json) · [首次异常](evidence/FIRST_FAILURE.json)。
