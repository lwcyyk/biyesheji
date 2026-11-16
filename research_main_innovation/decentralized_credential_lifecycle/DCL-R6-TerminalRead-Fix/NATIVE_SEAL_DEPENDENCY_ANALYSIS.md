# native seal依赖分解

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

**期限辅助读取是已确认的直接阻断，后续native成功仍为UNRESOLVED_DYNAMIC_UNRUN。**

|实际步骤|历史PFA执行范围|新版本静态接入与剩余条件|
|---|---|---|
|原state/window读取|state原件存在；适用性读取后在_phase_deadline的G.state被CLOSED拒绝|独立只读读取既有window，不调用活动态入口|
|phase/预算完整审查|PFA前缀和独立行政审计证明数据一致；旧终态路径未完成|Root身份/phase/seq/init/窗口、counter/intent/journal完整核验|
|内部状态读取|正常路径无mr_close_state，原行政结果UNKNOWN|原状态规则保持，缺件UNKNOWN，不由组空推定|
|协调器/角色/组及child回收|实际waitpid0、stop0、组空可用；底层打包未到达|原M.seal退出/单sealer规则保持；原G.seal停止器等待之后再验证当前退出前提|
|原执行锁/源码|原生预检fresh绑定通过|终态读取再验证同一原batch/source/lock/receipt和activation|
|生成seal输入审查|历史未进入|caller写独立pre-native review，包含活态接口对CLOSED的真实拒绝证据|
|Native manifest/ZIP持久化|未执行，无原生ZIP/manifest|保持原生成格式及写者，需真实IO/退出/期限证据|
|完成后审查|原自动行政成功、native UNRESOLVED|已存在Native包需成员/CRC/SHA/关键当前原件一致才读作COMPLETED；行政仍独立裁决|

原M.seal、M.permit_external_seal及MR管理器审查整体归一AST相同；新增检查在P.seal_applicability和G.seal读侧接入。前者不再使用活动态phase guard，后者不更换原停止器等待或原生打包算法。

四类状态分别处理：纯预窗无运行对象保持NOT_APPLICABLE；可信SEAL_ERROR支持FAILED；部分/不完整/损坏/错误身份或窗口不适用保持UNRESOLVED；既有完整ZIP经过实际逐流核验才COMPLETED。输入前提满足仅返回native_ready，不能预填COMPLETED。

重复审查只读取已有包；未验证的现有部分包和原失败不会触发自动重写。新boot只作历史只读核验，不发放当前native生成资格。当前尚未运行新接口或原生seal，不能由源码解除单点阻断推断全部后续步骤成功。

[具体实现](evidence/SOURCE_FINAL_R1/src/terminal_evidence.py) · [原始失败分类](evidence/PFA_ORIGINALS/native/inputs/root_private/boot/pt_seal_disposition.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
