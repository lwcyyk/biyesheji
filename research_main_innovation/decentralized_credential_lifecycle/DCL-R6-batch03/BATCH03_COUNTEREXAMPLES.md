# batch03反例与实现缺口
Material Passport：协议反例机器搜索0次；控制流静态复核完成。

## 实际协议结果
F1/F4均UNRUN_RESOURCE_GATE，观察到的本批协议反例数量0，搜索覆盖为空。不能据此赋予任何有限性质PASS_BOUNDED。

## 首次阻断：冻结测试能力和必需准入条件缺口
证据类型：STATIC_CONTROL_FLOW_WITNESS；机器执行次数0。
输入族：13份冻结case的局部status均为PASS，精确范围S1–S9必要动态receipt缺失。
度量：缺失一个必要range验收时，是否仍能创建FORMAL。
当前方法：BF-static-1 guard.py:746–755按case结果产生资格后调用launch_one('FORMAL')；262–273仅校验case名称、结果hash、boot及source_manifest。
预测差距：当前程序无法按本次§5/§6的附加条件阻止这一状态进入FORMAL。

最小缺失例为S9：三个child均按合同最多N次调用，没有N+1次访问动态夹具；全部旧case的局部PASS也不能补足该项。C11的四项故障只作用于局部单信用mirror，range registry/claim崩溃缝隙和实际fsync失败同样缺覆盖。源码摘录和hash在evidence下。

本次在启动前拒绝完整launcher，实际越权转换0次、预算不一致0个运行样本、监督器运行故障0个样本。此处登记的是准入覆盖缺陷，协议语义和运行中资源违例均未被机器检查。首次事件原样保存在FIRST_BLOCKING_EVENT.json；历史失败保持。
