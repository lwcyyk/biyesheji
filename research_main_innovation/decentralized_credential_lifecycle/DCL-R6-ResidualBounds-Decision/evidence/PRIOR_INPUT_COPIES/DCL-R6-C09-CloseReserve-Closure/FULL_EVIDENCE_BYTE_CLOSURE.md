# 完整证据字节闭包与分层依赖

## Material Passport

DCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。

**COUNT_BOUND_PROVED：条件性继承旧scope；BYTE_BOUND_PROVED：完整资源合同尚未取得；CAPACITY_CONTRACT_NOT_READY。** [FULL_CAPACITY_GAP_TABLE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/FULL_CAPACITY_GAP_TABLE.json)列出15项具体缺口；[MANIFEST_ZIP_BOUND_ARITHMETIC.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/MANIFEST_ZIP_BOUND_ARITHMETIC.json)提供manifest/ZIP代数。

旧封闭完整scope仍为raw≤4450、native成员≤4451、行政导出≤4452，普通成功行政ZIP≤4467。其前提为原源码/输入、单次activation、最多一次resume、固定actor/首错展开、无外加写者。mr_events.lock覆盖修正保持，PT-only的pt_expected_abort在该scope不可达。C09主日志已经占raw一个路径，行数增加不新增文件数。新quota/关闭/测试/外部oracle的真实集合差需要重算，旧值未自动覆盖新实施。

令R为全体raw唯一路径字节和，M_N为native manifest，Z_N为nativeZIP，H为host原始流/审计输入，S为源锁输入，M_A为行政manifest：

\[U_N=R+M_N,\quad Z_N=ZIP(U_N),\quad E_A=R+M_N+Z_N,\quad U_A=E_A+H+S+M_A.\]

U表示每层ZIP未压缩输入，E_A表示实际snapshot导出字节。Root原件和admin快照都保留时，新增磁盘保留还需计算两份E_A、host原件、M_A、行政ZIP和最终收据；source locks既有原件与新副本按实际路径区分。含在行政ZIP中的nativeZIP是一个独立成员，同时raw原件又被复制，两个成本均保留。

|组成|可核实子界/接受界|未闭合义务|
|---|---|---|
|C09 main|345148，v2条件；原源码无quota|待批未生效；关闭/其他原件未涵盖|
|关闭core|160＋H次尝试；237/260/1223/565等单项界|R/T/E/V、跨角色失败传播及其他关闭对象|
|其他logs/预算|条件校准journal15441008；全1m窗口471876988|writer生成与range/terminal32MiB接受条件统一|
|readiness/RootIPC/MR|read cap4MiB/128KiB；readiness602×131072=78905344|aggregate、失败staging、捕获前helper输出|
|S1–S9与Gate|trace cap乘积48×256×4096=50331648；固定测试列表|registry/journal/metadata/派生证明与异常联合字节|
|F1/F4及模型文件|固定输入/任务数和访问限额|状态/策略/trace/report编码、峰值对象分配|
|native metadata/ZIP|下述条件格式代数|R未闭合；格式和压缩参数前提；整文件hash内存|
|admin audit/host/raw streams|128次quiescence采样、一次host调用、旧读取cap|环境/proc角色数组、原始stdout/stderr、嵌入审计、最终错误收据|

单成员当前仅有部分读取接受cap和额外off_t64表示界；没有完整资源兼容的最大生成字节。假设4450个regular raw均受signed64 off_t约束，可给粗表示和41044005564003752341150 bytes；该值不会变成可用容量或完成保证。

Native manifest用RootIPC pretty indent2。取ASCII相对名F≤1535、off_t decimal≤19、clock宽度25/20，逐行语法代数得到M_N≤7436121。现有读取接受4MiB；粗界高于cap仅说明此证明无法覆盖接受要求，未证明真实固定路径可达到该极值。需要继续用实际路径族收紧，或在未来明确批准的版本内重新制定合同。

ZIP32既有profile下，4451项头部粗界14074084。若整个已接受U_N≤33554432，ZIP_STORED条件界47628516；另证pinned zlib默认参数compressBound式时，deflate条件界47696620。压缩后更小没有作为前提；这些粗界超cap也没有被当成实际必然超限。源R、native/行政两个归档输出的可用上界仍为空。

递归核验见[ARCHIVE_RECURSION_REVIEW.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/ARCHIVE_RECURSION_REVIEW.json)与[EVIDENCE_LAYER_DAG.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/EVIDENCE_LAYER_DAG.json)。现行native按basename排除自身manifest/ZIP，然后只加入manifest一次；固定写者还需避免嵌套同名碰撞。control与ROOT不同域，行政outputs不会回流Root集合；最终收据及windows_entry的STARTUP_FINALIZATION_ERROR位于行政ZIP前像外。独立oracle只读或在前像外写收据，当前没有自动“直到成功”的归档递归。

DAG按首次成功、写者静止的native构建再接行政层分相。失败/部分native之后新增的SEAL_ERROR或处置记录只能进入随后真实可取的raw/admin集合；它们不会追加入已经消费的native前像。部分包始终按部分包裁决，不能用后层报告把它升级为完整封存。

新增识别的容量边界：STARTUP_NATIVE_AUDIT在export之前保存，files尚为空；完成export后stdout包含完整files和first_failure摘要；host最终收据又嵌入stdout解析对象。它们是不同实际视图，字节须分别计入。最终finalization-error也可能嵌入preserved audit，属于旧4452快照原件集合之外。数量有限不自动给这些内容一个可部署的字节界。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。
