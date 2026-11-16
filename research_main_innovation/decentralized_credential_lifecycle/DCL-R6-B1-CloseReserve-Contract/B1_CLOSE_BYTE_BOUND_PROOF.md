# B1关闭字节边界

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

**PARTIAL，B_B1-close=null。** 逐字段语法复核采用原compact/RootIPC编码和明确ABI宽度，并对E域作范围收敛。原件唯一集合、失败staging与累计生产写量分别计量。[B1_CLOSE_BYTE_ALGEBRA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/B1_CLOSE_BYTE_ALGEBRA.json)

|记录|条件encoded bytes|
|---|---:|
|ABORTING|237|
|external_closing|260|
|normal waitpid|1223|
|fallback waitpid|565|
|marker|144＋R|
|固定43字节quota reason marker|189|
|通用Root MR marker|194|
|first，R_MR≤38|25092＋T＋B|
|cleanup state / attempt行|997＋11T＋B / 998＋11T＋B|
|stop_result|1151＋E＋ΣV_j|

R为包含引号的reason JSON token，R_MR固定调用值与R_budget异常str分开。T为异常类名token，B为三份原budget hash/size或UNKNOWN/type映射，E仅来自stop_tree的lock/marker发布try中的repr，V为12个原kernel值token。B≤69＋3max(106,29＋T)，健康B≤387。compact ensure_ascii=True每code point最多12，RootIPC UTF-8/转义最多6；字段键、括号、分隔符、缩进及LF都已按实际codec计入。

PID正int32≤10、ticks/device/inode/预算长度u64≤20、clock_ns≤20、binary64 JSON≤25、waitstatus≤11、stat_ctime_ns≤29及冻结namespace是明确条件。EIO/乱码或profile外数据不能借这些条件获得正常完成证据。[原逐字段代数](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/CLOSE_SCHEMA_BYTE_ALGEBRA.json)

对A6/S8/W1/H0的E域，沿实际生产次数求和得核心累计生成字节包络。

\[W_{E,core}\le179815+138T+18B+8E+8\sum V_j.\]

按实际唯一目标计稳定数据，再单列不同临时路径，可得两个保守式。

\[B_{stable,E}\le44708+78T+8B+8E+8\sum V_j.\]
\[B_{failed-stage,E}\le23275+66T+6B+8E+8\sum V_j.\]

路径类合并后为67983＋144T＋14B＋16E＋16ΣV。它是同一稳定路径一次、每个实际临时路径一次的粗并集上界，单项极大值未被证明同时可达。生产量式是另一保守包络，条件参数给定后可取适用上界中较小者。

健康串行Receiver示例中，原始quota故障代码31字节ASCII、AdmissionBlocked类名16、首个reason25，健康budget387且notes为空。于是first≤941、marker≤183、cleanup≤1119，14次数据发布的累计字节≤9272＋2ΣV。该示例仍欠完整V profile及真实物理保留。

正常handoff新增/替换的4个稳定载体为stop_result、handoff、result_C09、batch_state，保留字节≤7098＋3ΣV。计入verified/resumed两次state和batch更新，6次发布累计≤11189＋4ΣV。cleanup在3个真实稳定载体中各出现一次，源码写入次数中复制4次，按真实对象计量。[NORMAL_HANDOFF_BYTE_MODEL.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/NORMAL_HANDOFF_BYTE_MODEL.json)

最终合同按唯一必要目标求ΣN_iL_i，加实际失败metadata/staging、所选quota补充、外部退出证据和引用index。encoded数据与物理allocation用不同单位。完整T/E/V、外部witness/index字节和FS metadata/provider参数未实例化，完整关闭数值保留null。[最小合同草案](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/proposals/B1_MINIMAL_CLOSE_RESERVE_DRAFT.json)


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
