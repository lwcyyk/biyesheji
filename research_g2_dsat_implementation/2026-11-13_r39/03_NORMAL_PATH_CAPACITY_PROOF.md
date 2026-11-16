# 正常路径计数与容量

完整正常L0字节数仍为 **UNPROVEN**。本轮取得了独立源码计数公式，并没有用历史平均长度替代最大值。

## 609与136

历史609为一次旧运行观察：raw/classified各254、snapshot开始/结束各8、原TEST_ASSERTION68、FAILED5、PROVENANCE_CHECK1及其他记录。旧运行有后置来源失败和原容量失败，最终阶段存在RECOVERY_REQUIRED。

R38新增136是68个TEST_CASE_STARTED与68个TEST_CASE_EVIDENCE相对旧逐项68记录的增量；A1/H1/D1A分别增加40/48/48。它们追加到F08原journal，文件数不变。只有完整成功遍历时才生成全部204条逐项记录。

历史旧阶段、去重结果、源码版本和错误分支已经不同，609+136=745不构成当前必然记录数，也不构成未来最大值。

## 当前源码公式

正常路径固定部分232条：PRECHECK/RUN_STARTED2、8个snapshot对16、TESTS_RUNNING3、逐项204、PHASE_ASSERTIONS_FINISHED3、TESTS_FINISHED1、RESOURCE_AUDIT1、FINALIZATION_READY1、FINALIZED1。

记O为去重后的ORIGIN_OBSERVED数量，C为去重后的ORIGIN_CLASSIFIED数量，W为WRAPPED_ORIGIN_OBSERVED数量，则：

`N_normal = 232 + O + C + W`。

每snapshot库存<=512、最多8snapshot，故O,C各<=4096；正常A17排除提前crypto，两个包装模块仅在D1A_loaded、D1A_finished及post审计最多各出现，W<=6。得到需求的松上包络8430。源码尝试guard仍为8320，成功写入的记录还受1MiB journal总guard限制。8430仅为松包络，其可达到性仍待证明；触及guard的需求轨迹会导致完整提交失败。

若额外证明源库存单调且元数据/文件身份稳定、每个最终module只产生一个raw/classified键，则可进一步得到1262上界。该稳定性尚未从当前冻结输入域全称推出，不能选择它代替8430或实际可达极值。

## 尺寸

raw值guard1048576B、压缩buffer guard1114112B、base64内容最多1485484B。stage按转义JSON<=256、phase最长9、ID3、UTC32、seq4位和两个64hex链字段代入实际结构，完整表示的统一producer封套松界为 **1486196B**；原成功单行guard为1048576B，含LF。这两项含义分别为完整表示上包络与接受门，后者不能证明前者一定装入。

新原结果单对象schema已有1425B松界，但完整CASE_EVIDENCE含原详情和前置回执，snapshot及最终汇总还会重复部分事实。journal全序列、最终RESULTS/ORIGINS/LEDGER和receipt的联合wire上界仍不足以证明各自适配。

`NORMAL_L0_REQUIRED_BYTES=UNKNOWN`。固定invocation681、RUN_START9576、D24 1032/287及源级单对象界仍有效；历史817454只保留其固定数据范围。
