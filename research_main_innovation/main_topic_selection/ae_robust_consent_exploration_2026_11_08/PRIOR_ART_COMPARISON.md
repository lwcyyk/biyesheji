# 有界误差查询的定点先例比较

2026-11-08。本轮公开检索工具恢复可用，取得了两份正式会议记录直接链接的 PDF。本文只对实际读取的模型和指定结果作比较。

|项目|本轮判定模型|Optimal Reconstruction from Linear Queries|Density-Dependent Group Testing|
|---|---|---|---|
|未知对象|任意 \(\theta\in\{-1,+1\}^d\)|\(x\in\mathbb R^d\)|带独立 Bernoulli 先验的缺陷集合，重点为稀疏区间|
|目标|判断是否全为 +1|控制重建向量的欧氏误差|恢复完整缺陷集合|
|查询|两个归一化彩票的效用比较，可有正负权重与常数项|欧氏单位向量的线性测量|选择检测池，给定密度相关测试函数|
|返回|一比特符号|带误差的实数|以 \(f(\rho)\) 概率返回 1|
|误差|每次绝对值至多 \(\eta\)，可自适应对抗|每次测量的对抗性加性误差|声明的随机测试模型|
|正确性|所有输入与误差序列均精确正确|最坏重建损失|指定概率下的集合恢复错误率|
|策略|允许自适应|允许自适应|已读主模型采用非自适应设计|

**COLT 2026 来源。** Yuval Filmus、Shay Moran、Elizaveta Nesterova，*Optimal Reconstruction from Linear Queries*，PMLR 336，2428–2476。官方入口链接的 PDF 共 49 页，内部页码 1–49。

实际核读 PDF 第 1–4 页的模型和主结果，并查看第 5 页的可行域说明与相关定位。第 1 页完成图像复核。

其查询满足 \(\|v\|_2=1\)，返回实数 r 且 \(|r-\langle v,x\rangle|\le\delta\)。本轮模型的归一化来自概率分布，控制的是正负权重的总量。归约需要同时处理返回信息、目标和归一化。源重建下界不能未经推导用于一个判定位。[正式入口](https://proceedings.mlr.press/v336/filmus26a.html)

**AISTATS 2025 来源。** Rahil Morjaria、Saikiran Bulusu、Venkata Gandikota、Sidharth Jaggi，*Density-Dependent Group Testing*，PMLR 258，3628–3636。官方链接 PDF 共 50 页，含附加材料。

实际核读 PDF 第 1–4 页的模型、相关工作及算法定义，第 4 页完成图像复核。后续页仅作标题和关键词定位。

其主模型以 \(f(\rho)\) 描述阳性概率，给定缺陷先验并恢复集合。本轮则要求对所有二元向量和有界对抗误差正确判定。已读的具体模型没有直接提供所需参数代入，完整覆盖继续待核。[正式入口](https://proceedings.mlr.press/v258/morjaria25a.html)

**仍需追踪的直接前作。** 密度检测论文第 2 页引用阈值群组检测，包括在阈值间允许任意回答的模型。本轮尚未核读这些原始结果。池大小受限的检测、加权测试、统计查询及近似比较的现有结果也可能给出短推论。

本轮没有因两份论文模型不同而作全局无先例判断。当前状态为 SCOPED_COMPARISON_COMPLETED_PRIORITY_OPEN。

官方记录及检索响应保存于 sources/PRIMARY_RECORDS.json、sources/WEB_SEARCH.json。下载来源、哈希和实际阅读范围汇总于 sources/SOURCE_MANIFEST.json。结构预检均为 PASS，页数一致，warnings 为空，结构检查仅用于文件与页码取证。
