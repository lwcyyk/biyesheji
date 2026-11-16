# 差异、授权与完整性

正式授权来自研究者本次提交的G2-R14附件，路径和SHA固定于APPROVAL_RECEIPT.json。R13原申请approved=false和复核记录原字节保留；本轮独立receipt记录H1 approved=true，H2/B2/S5=false。

实施前核对R13全部5报告、6主JSON及来源记录，复核13项源码与21件交付；全部R13实际文件共22件。R13_reconfirmation原记录亦核对。旧921次比较、280项冻结快照、源码/交付/QA和本轮来源绑定共1259次比较（899不同路径），实施前后匹配。

## 获准差异

- 新增3个Python文件：宿主473行、测试635行、runner244行。
- 新增fixture子树内4份JSON；其中Schema副本与原R13 Schema hash相同。
- 已存在工程文件修改0；所有变化均在四个获准目标和本轮新记录/运行根内。

逐文件最终hash和执行hash见CODE_DIFF.json与SOURCE_LOCK.json。完整新增Python差异见sources/NEW_CODE.diff，源码快照分别随每轮保留。合成秘密输入以hash登记，公开diff不展开canary原值。

storage/services/protocol、R12适配器/测试/runner/夹具、migration、R07 S1/S2、R10 S3-A、独立checker、旧研究与实验结果均在指定保护清单内。保护结论按清单路径给出，不声称盘点了所有运行副本或未列出的生产文件。

## 修订责任

实质工程修复只有新宿主返回失败时的计费保护：finally固定operations增量，并在锁定一读合同下以正增量支持源尝试计数。H13通过实际失败/修复链验证。未更动原R12错误码、规范请求摘要或下游S1/S2/S3语义。

测试增加H13返回边界故障子场景和逐返回读数核验，属于原“异常＋副作用准确”责任；24个冻结ID及原期望保持。末轮夹具校正外scope创建者为DISPATCHED_UNKNOWN、spent=1/reserved=0，与窗口unknown列表相容。完整source历史可达性和原生材料真实性仍未声称验证。

实际Schema对整数上界、固定gap码与H1合成注册作了收紧，说明见02报告；原R13文稿保持原字节。旧CLOSED/1、legacy O、a/o/instance和Native当前性层次沿原合同。

## 执行封闭性

冻结命令、解释器hash和3.12.14版本在runner预检中核验。-B禁写bytecode。限定新24项发现，无旧115/46/33项或整仓调用；无新依赖、NetworkX/求解器/checker执行。

runtime audit捕获SQLite/socket/process/private文件及输出根外写入；最终计数均0。源模块没有实际EventLog、AuthorityStore、Controller或Provider初始化。读取额度和遥测均用替身建账，真实数据库和密钥成本独立保留为未测量。

交付最终QA只做文件/hash/JSON/范围和canary检查，无新增项目测试；结果见sources/DELIVERY_QA.json。
