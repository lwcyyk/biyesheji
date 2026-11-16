# LR证据索引

2026-11-10。Material Passport：本地来源链/行政核对；程序运行类别分别登记。

|证据|内容|
|---|---|
|[授权文本](evidence/LR_AUTHORIZATION_TEXT.txt)|用户LR专项原文|
|[收据](evidence/LR_AUTHORIZATION_RECEIPT.json)|有限目录/只读与版本查询/禁止范围|
|[启动前命令计划](evidence/LR_COMMAND_PLAN.json)|每条精确argv、目的、登记时刻|
|[总执行记录](evidence/LR_COMMAND_RESULTS.json)|35条实际调用、双流/时间/退出/分类|
|[解释器摘要](evidence/commands/08.result.json)|规范文件SHA|
|[版本](evidence/commands/09.result.json)|唯一Python执行，仅--version|
|[包依赖](evidence/commands/10.result.json)|本地包状态/版本/Depends|
|[manager](evidence/commands/12.result.json)|真实Version/SystemState/默认AS|
|[失败单位](evidence/commands/14.result.json)|仅mnt-e.mount的清单观测|
|[根资源](evidence/commands/15.result.json)|根slice无限值|
|[目录](evidence/commands/25.result.json)|候选路径缺失|
|[ELF](evidence/LR_ELF_AUDIT.json)|本地UNC读取已发现8MB文件、ELF64/DT_NEEDED/PT_INTERP；未复制/执行loader|
|[运行时候选锁](evidence/LR_RUNTIME_CANDIDATE_LOCK.json)|版本/解释器/14关键文件摘要，PROPOSED_NOT_ADOPTED，完整闭包未锁|
|[五业务源锁](evidence/LR_BUSINESS_SOURCE_LOCK.json)|原字节摘要复核，编译/导入0|
|[依赖摘要](evidence/commands/35.result.json)|直接库/loader及关键stdlib文件|
|[行政等待事件](evidence/LR_QUERY_ORCHESTRATION_EVENT.json)|18号等待期间8项计划启动前拒绝，随后按序执行，无Linux重跑|
|[入场锁](evidence/LR_BASELINE_LOCK.json)|P全60文件及根导航快照，P输出62项初核|
|[历史核对](evidence/LR_HISTORY_INTEGRITY_CHECK.json)|P/Envelope/Repair/batch01/v3与ZIP保持|
|[交付核对](evidence/LR_DELIVERY_CHECK.json)|命令/原流hash、必需文档/JSON/链接/范围|
|[输出锁](evidence/LR_OUTPUT_MANIFEST.json)|LR文件及四根导航；排除自身和交付核对避免循环|

raw路径为evidence/commands/NN.stdout.txt、NN.stderr.txt，每条同时有NN.result.json。原始流按字节保存；WSL原生UTF-16LE前缀与Linux UTF-8错误按分段解码。boot_id、包/系统路径信息只留本地原件，报告省略唯一设备标识。没有读取私人目录或凭据。

现场Linux调用35条，另有host静态ELF/源码读取与文件hash。临时行政调用/解析没有生成验证/监督程序，未计入MODEL_CHECK或RESOURCE_GATE。后续L-C命令仅存在申请文本，未执行。

P旧输出manifest的四根导航从LR/evidence/navigation_before验证；更早各阶段仍沿用各自快照。旧manifest原字节保持；行政hash通过不授语义、资源或独立外部认证。
