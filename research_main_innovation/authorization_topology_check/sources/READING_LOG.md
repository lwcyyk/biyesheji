# 来源、版本及证据等级

日期2026-11-05，主文稿AT-CHECK-1。使用academic-research-suite的文献/来源核验流程，全部分析在当前会话完成。深入对象仅为resource_pool与langfuse_tracing/ticket_triage；HITL_DISCOVERY.json中的其他关键词命中仅用于发现。

## 1. 应用源码与配置

来源：[temporalio/samples-python官方仓库](https://github.com/temporalio/samples-python)，本轮取得main ZIP，注释固定commit `c46e6156694e93a12d6e666cec1691fd02a067a7`。[固定源树](https://github.com/temporalio/samples-python/tree/c46e6156694e93a12d6e666cec1691fd02a067a7)

归档temporal_samples.zip，SHA256 `e57fb6bb8a173cfa4b2d0ba9e60fa6db2a7401844d8a368b05f9678f09b93227`，1395条成员。SOURCE_LOCATIONS.json保存22个关键class/function的精确行号；片段源文件保存在samples_snapshot，原归档未改。

|路径（samples_snapshot内）|实读范围与用途|
|---|---|
|resource_pool/README.md|全部：长持锁、其他方案、termination/timeout caveat、作者定性性能提示|
|resource_pool/shared.py|全部：AcquireRequest/Response、DetachedResource、AcquiredResource.detach；未发现业务Approval schema|
|resource_pool/pool_client/resource_pool_workflow.py|全部：init、三个Signal、query、assign、FIFO/first-free、CAN；重点81–97的通知后登记顺序|
|resource_pool/pool_client/resource_pool_client.py|全部：动态handler、获取/释放Signal、wait、reattach、finally、timeout告警|
|resource_pool/resource_user_workflow.py|全部：两Activity持有区间、完成后注入失败、detach与continue-as-new；Activity本身只log/sleep|
|resource_pool/starter.py、worker.py|全部：默认连接、共同task queue、4个User Workflow、2个资源、一个Worker进程、结果/cleanup|
|tests/resource_pool/workflow_test.py|全部：8个User/3个资源的官方测试规格、mock activity、固定资源及互斥/最终空闲断言；本轮未运行|
|langfuse_tracing/ticket_triage/README.md|全部：官方流程、运行依赖、预期trace、replay/restart例；预期图未标为实测|
|同目录workflows.py|全部：顺序execute_activity、approval wait/snapshot/branch、Update/validator、重试policy|
|同目录activities.py|全部：数据类、外部LLM配置/调用、local account table、draft只返回文本|
|同目录worker.py、starter.py|全部：默认本地Temporal、一个注册Worker、自动发送一次decision、可选decline/停顿、LLM与遥测依赖|
|tests/langfuse_tracing/test_ticket_triage.py|全部：mock活动、in-memory exporter、正反分支expected span tree、replayer断言。本轮未运行，未取实际history|
|tests/langfuse_tracing/conftest.py、helpers.py|测试隔离和span处理：原样测试可避开Langfuse/真实LLM；不能据此当作生产效果验证|
|tests/conftest.py|local/time-skipping/外部server分支；默认local，CLI下载版本v1.10.0及特性参数|
|pyproject.toml、uv.lock|相关依赖、Python范围和锁定包；不是已安装工具链|
|langfuse_tracing/README.md、telemetry.py、verify_trace.py|部署/观测流程及验证范围。validate trace只涉及span结构/usage，无法认证退款或工具效果Exactly-once|
|langfuse_tracing/langfuse/docker-compose.yml、.env.example|只读配置。固定Langfuse标签与未固定基础镜像分别登记；没有读取本机真实env或操作账号|

官方示例和测试都是**L1可执行规格**。没有作者同case实际history或本轮运行记录，L2为NOT_RUN/NOT_COLLECTED。源中“exactly once”相关测试聚焦span去重，未转换成业务调用语义。

## 2. 依赖源包与版本核对

`uv.lock`相关条目汇总于LOCKED_RELEVANT_DEPENDENCIES.json：temporalio1.35.0、openai2.54.0、opentelemetry-api/sdk1.42.1、protobuf5.29.6、pytest7.4.4及pytest-asyncio0.18.3等。它们来自源码锁，不代表本轮环境已安装。

使用锁中给出的官方PyPI sdist URL取得temporalio-1.35.0.tar.gz，SHA256 `c7a14f29909f8d847f78de49305af89c0ec5aea39272cd4050124386ac3ca295`，与uv.lock一致。[发布元数据](https://pypi.org/project/temporalio/1.35.0/)

实际提取并定向读取：

- sdk_snapshot/temporalio/testing/_workflow.py：start_local参数及说明，100–158；确认dev_server_download_version是CLI下载版本。
- sdk_snapshot/temporalio/workflow/_activities.py：ActivityCancellationType及execute_activity默认参数，72起及相关签名；默认TRY_CANCEL，不能由该参数名推断真实外部效果终止。
- sdk_snapshot/temporalio/workflow/__init__.py与worker/_workflow_instance.py：API导出/外部Signal和执行入口的相关定位；未声称完整核读整个运行器，也未证明全部异步交错。

没有安装SDK、启动测试server或执行样本。源包签名/软件供应链安全审计不在本轮结论内；本轮只核对字节哈希。

## 3. 继承的理论与项目裁决

继承authorization_workload_evidence下三份用户指定材料，INHERITED_INPUTS.json固定其哈希。所选τ-bench历史切片继续按单执行者批量接口覆盖，未重新扩大任务数据。

复用Balegas等2015 bounded counter与Bailis等2014 I-confluence PDF/文本/结构sidecar。使用范围沿用已读的权利分配/副本假设及Definition6/Theorem1，不宣称二者自动给任意程序的高效判定或最优协调点算法。[既有Balegas原文](https://arxiv.org/pdf/1503.09052) [Bailis原文](https://arxiv.org/pdf/1402.2237)

本轮额外核对`D:\毕业设计\research_recipe_r3\VERDICT.md`以保持论文B版口径：资源谱为条件性数学贡献候选，近邻及原生前提/数学外审各自未决。该历史文件中的RAG全文获取状态已有后续资产审查纠正，本轮没有把旧缺口当作当前事实。

已有K1标量额度、K2私有取位、整份prepared state/SC-MC成本选择及七项机制裁决均保持。CS03未取得工件与历史数字等级未变，未新增密码学需求或MPC实现。

## 4. 成本推导的证据等级

MINIMAL_WORKFLOW.json给出两个来源约束的规格切片。资源池的排队/授予顺序为允许的调度选择，非真实message timestamp。票据Update可早到来自starter/test与run代码，不新增“分类后人工批准”条件。

3N个逻辑Signal、starter名义9个Activity、批准路径3个Activity/2次LLM请求等均为**源码路径计数**。retry、CAN、Temporal底层RPC、持久化、模型计费和遥测另计；sleep/timeout是配置值，不是测量。成本公式不是对所有可替代协议的通用下界。

原文README对资源池吞吐的“几十而非几百”描述登记为作者定性陈述，无本轮样本/硬件支持。没有将其提升为无法被通用方法避免的代价下界。

## 5. 获取和运行决定

GitHub连接器tree只读请求返回MCP传输错误，后续从官方codeload/raw及锁指定PyPI公开URL取源；RETRIEVAL_ARCHIVE.json和RETRIEVAL_SDK.json保存状态/哈希。没有外部通信发布、账号或业务操作。

raw/RUN_STATUS.json说明本轮不运行：当前路线由L1拓扑/检查位置/接口决定，暂无一个运行事实能使新理论对象成立；有限tests只能补实现运行证据，无法替代全交错证明。没有以未跑生产日志维持EVIDENCE_GAP。

若研究者以后决定复用官方测试，隔离入口可从下列命令开始（本轮未执行）：

```powershell
uv run --group dev pytest tests/resource_pool/workflow_test.py -q --workflow-environment local
uv run --group dev --group langfuse-tracing pytest tests/langfuse_tracing/test_ticket_triage.py -q --workflow-environment local
```

应在独立源码副本运行，使用官方local fixture，先冻结实际Python/uv/CLI/服务版本、下载及本地监听费用。票据测试使用mock活动和内存观测；完整starter则依赖LLM端点与Langfuse，不能混计。新增取证代码不改变工作流合同，候选机制仍须另过分离门。

## 6. 复核文件

SOURCE_LOCATIONS.json提供函数精确范围；SOURCE_MANIFEST.json绑定全部新增源/文稿；DOCUMENT_VALIDATION.json记录链接、JSON、源归档一致性及算术检查。所有源提取、TOML/AST和算术处理属于文档取证，未运行Workflow或实现候选方法。
