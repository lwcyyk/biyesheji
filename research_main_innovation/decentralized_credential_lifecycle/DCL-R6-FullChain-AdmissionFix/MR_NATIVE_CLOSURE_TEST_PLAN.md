# MR原生异常关闭专项A测试计划

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


未来A前置：完成生产容量最大清单、选定版本合同、集成入口与补充合同摘要、重新冻结源码/argv/新身份，获得独立动态授权；复核既有条件性glibc来源和当前boot。当前所有动态步骤UNRUN。

冻结依赖拟为：单会话/PreT0/WORK/C00→PT/PF/TR/RA/Ready/MR64→C01–C08→C09H/IPC/BC→真实C09及ManagerRecovery→C10→本批专用fault单位→未审查失败拒绝→自动关闭。A不进入C11/C12/S34/门18/F1/F4。

1. 验证当前scope/版本/合同/argv/专用单位空状态、独立Stop责任及C10 PASS，预付512；旧账不改写。
2. 专用单位仅复用当前Payload sandbox，worker输出当前boot/PID后exit79；Root最多64次采样、5秒观察。丢失live身份/查询超时/原始journal缺失即首次失败关闭，重试0。
3. 核对InvocationID、ExecMainPID、ExecMainCode/Status、时间、failed集合精确增量及既有未审查拒绝。保存原始查询stdout/stderr和journal。
4. 记录原始单位/预算/窗口后沿原M.abort自动STOP/CLOSED，协调者waitpid见证scheduler78，Root/独立停止器分别保存责任及错误。
5. 事后独立oracle从真实快照读取mr_native_case/first_failure/close/CLOSED/STOP/registry/waitpid及预算字节，核预算摘要、原始计数、身份与时间。原生和行政包需各自逐成员检查、相互绑定；caller自身退出另由外部只读审查。
6. 自动主路径、外部停止兜底、自动行政、后备归档和CLEANUP_UNKNOWN分别裁决；人工关闭/缺源/丢Root均禁止登记主路径成功。

新增oracle的data API已跑21个主机夹具；from_snapshot文件API与真实systemd/封存路径仍待原生准入。其admin独立包核验标记是明确外部前提，当前自动行政衔接尚未实现，未登记为PASS。

[入口](maintenance/mr_native_entry.py) · [独立oracle](maintenance/mr_native_oracle.py) · [动态前提](NEXT_DYNAMIC_AUTHORIZATION.md)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
