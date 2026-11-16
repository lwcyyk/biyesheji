# 四份 O 与保守责任保持

## 实际绑定

O_before由专用数据库读取；O_projection由固定R07输出关系及fixture关联给出；O_proof_context为原包bindings.O_before；O_after为实际事务结果。base/after用新typed域摘要，projection/context使用原绑定算法，所有字段独立保存。

| 案例 | 数据库before | projection/context | 默认after | 实际结论 |
|---|---|---|---|---|
| A08 | 原夹具5项先持久化并读回 | 各6项，新增close:c2 | 6项 | 新材料责任保留；请求/来源快照不被重绑；o增加 |
| A24 | 5项 | 各6项，新增await_terminal:i1 | 6项 | H=0归档；await/window/effect和来源前提继续待结；global=false |

T001、T008、T020给出实际断言及前后摘要。base与proof摘要保持其实际差异；原包未改名或重新生成。

## 固定覆盖规则

每个初始typed项持有完整旧描述及opaque风险hold；来源关系由固定源bundle与scope绑定。保留旧项或增加可信投影项为默认策略。替换仅允许pending_source完整继承旧描述、origin、scope、依赖及hold，并以同库不可变risk对象支撑；close:u仅添加已知材料责任。该新增close项独立于“u一定由被替换尝试创建”的断言。

T017实际保存替换与同库对象，独立oracle展开retained旧描述，证明原风险集包含于结果风险集。T018移除retained、伪称covers或遗漏组件均遭拒绝，原world/事件/接受对象保持。提案中的covers列表、accepted或source布尔值无法建立信任。

T016保留UNKNOWN的settle/source/unseen债务；T019使用既存VAR_MISSING_D_A，独立核R=0/H=1后仍保留材料/来源债务；T021只增加B执行责任并保留A/V；T042空F保留原更宽O并新增investigate，未获得空世界许可。后来新增的O经a/o与base摘要保护，旧包无法覆盖。

## 证明范围

本轮验证可信合成初始化、固定已核数学包、受信事件适配与保守规则下的责任保持。合成domain事件的全部新风险由受信输入显式提供，测试覆盖撤回/迟到/第三批准/O/B等已冻结事件。真实源是否完备、真实writer是否全部接入、未来创建/后代/业务sink的实际范围依旧需要S3-B精化。

S3-A的所有接受回执固定native_admission=SOURCE_OR_REFINEMENT_GAP、global_complete=false；数学H=0与当前原生关闭分别管理。旧phase、spent、grants、window、CLOSED/1及真实UNKNOWN未被写入或清除。
