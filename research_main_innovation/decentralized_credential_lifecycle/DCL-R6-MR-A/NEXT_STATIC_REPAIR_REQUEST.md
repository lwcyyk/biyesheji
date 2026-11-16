# 下一最小静态补缺建议

本次冻结r5的有限A在运行窗创建前失败，源码保持。下一修订需新明确静态授权，建议只处理以下相依职责：

1. **PRE_WINDOW与ACTIVE检查点分离。** 初始只读health查询位于T0之前，仍需核boot、SOURCE/receipt、sealed初始身份和STOP/CLOSED；此时允许state尚未建立。运行及恢复阶段继续严格要求state/预算。采用显式phase约束，禁止把所有query统一改成allow_uninitialized。
2. **使用已有启动TCB上下文关闭预窗失败。** 原sealed/activation记录已有preflight期限和Owner/child身份，可在T0缺席时提供受认证的关闭边界；R和T0保持null，禁止临时造新的60秒预算窗或把账状态填0。保留Root父停止兜底的实际证据和每次后备失败。
3. **预窗证据封存分支。** 无batch_state时保留源码/授权/claim/首错/退出原件，形成明确的PRE_T0_ABORTED封存；不依赖只存在于运行窗的BOOT_START/state。原生seal失败与行政ZIP始终分别裁决。

对应新测试应包括：合法初始health能进入T0；已有窗口缺state仍拒绝；预窗query异常/错误boot/STOP/CLOSED；无T0错误自动关闭及原始退出/封存；运行和恢复语义保持。仅创建和静态审查后重新冻结，再申请新独立有限A；当前batch10已经CLOSED及认领消耗，即使无预算账也保持关闭。

其余manager实例审查、ACK/Receiver/waitpid、预算核心、C00Ready、RootIPC、原C/S/门18及资源上限保持，F1/F4继续关闭。下一批次编号和阶段B规划须由新锁统一登记，当前不自动创建任何批次。
