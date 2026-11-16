# 资源资格门的强制证据规则

Material Passport：BF-static-2/r4；STATIC_CONTROL_FLOW_PASS；动态资格NOT_OBTAINED。

## 固定顺序

C00–C12 → RANGE的34个S1–S9正反job → root独立原始证据重算 → 资格门正向控制及17项负向检查 → RESOURCE_QUALIFICATION → F1→F4。
只有匹配校准专用授权时，最后一步改为停止并封存；关闭后的窗口不会用于后续FORMAL。

每个C结果须为当前批root记录的PASS且摘要匹配。S集合必须恰为34个被冻结job，覆盖S1–S9；safe结果须PASS，mutant须MUTATION_DETECTED。UNRUN、FAIL、INCONCLUSIVE、MUTATION_NOT_DETECTED、EVIDENCE_MISSING、HASH_MISMATCH、UNEXPECTED_RECOVERY及缺件均拒绝。单独一份accepted/PASS JSON无法产生资格。

## 原始重算

独立检查器读取并复算：

- 24字节counter的魔数、cap与used。

- PREP/COMMIT请求、范围、task唯一性及不重叠性。

- 完整持久屏障的实际顺序、实际短写/EIO触发证据。

- claim唯一性、局部debit上界、许可后实际语义文件的数量与内容。

- S2保守占用、恢复无新grant、关闭/过期/错误身份拒绝及N+1拒绝。

- worker真实握手/父进程wait记录、单调时间、绑定与完整闭合。

- 所有意外拒绝原因、额外违例和非预期模糊终态。

真实全局journal另作流式检查：PREP/COMMIT连续配对、counter/intent一致，boot/batch/T0/源码/合同绑定，生产精确task对应32896/4096/1且不重复，其余主账交易均为单信用。主账模糊、残留intent临时文件或超额均阻断。

## 保护收据与FORMAL再准入

root仅在RANGE服务结束并确认组空之后重算原始证据。生成root拥有、payload不可写的 RANGE_QUALIFICATION、GATE_NEGATIVE_AUDIT，并用它们的摘要绑定RESOURCE_QUALIFICATION。收据含当前batch、boot、T0、完整源码manifest、执行锁、输入摘要、原始文件摘要、检测结果、预算真值和实际时标。

FORMAL入口在导入业务语义前重新核对C结果、S/GATE根收据、源码与绑定、全部原始文件摘要，并再次核验真实全局账。正式scope必须是CALIBRATE_S1S9_THEN_F1_F4；校准专用scope拒绝FORMAL。校准共同deadline仍为T0+300，资格生成及root审查也占该窗口；1740/1800与访问硬界保持。

## 信任与边界

可信root启动器/manager、固定哈希程序、内核及fsync/rename/目录同步合同仍属TCB。字段伪造、陈旧/跨批收据、缺原始账、输入/源码漂移均有拒绝路径。同UID任意恶意Python、root或内核失陷、存储回滚与掉电持久性没有获得新认证。预期模糊合成账以保守占用、CLOSED和不可重用处理；主账须独立健康。当前仅有静态证据。
