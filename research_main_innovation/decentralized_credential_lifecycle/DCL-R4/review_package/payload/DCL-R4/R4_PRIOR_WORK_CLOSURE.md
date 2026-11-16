# DCL-R4：直接先例与来源闭合记录

2026-11-10。沿用R1–R3的实际读取范围，本轮定点补查作者入口、ePrint、出版方及构建来源。检索用公开题录/URL，私有项目上传、作者联系与工件运行均为0。`SOURCE_UNRESOLVED`随文保留。

## 1. 题录、取得范围与影响

|来源/版本|作者、日期与正式地址|实际取得范围/来源状态|机制重叠及证明边界|当前影响|
|---|---|---|---|---|
|PBFT，OSDI1999，173–186|Miguel Castro、Barbara Liskov；[官方全文HTML](https://static.usenix.org/events/osdi99/full_papers/castro/castro_html/castro.html)|R3实际核读§§2–4的模型、服务、签名算法/checkpoint/view-change/确定性|提供固定成员SMR基础；本目录的跨成员Seal连接层另给条件证明|保留同epoch标准依赖；未把原文当作本RHO重配置协议的证明|
|BFT-SMaRt官方Wiki，R3读取的活文档|项目维护者；文档精确commit尚未固定；[项目说明](https://github.com/bft-smart/library/wiki/How-BFT-SMaRt-works)|state transfer与experimental/TTP-driven reconfiguration段；项目文档|标准状态转交/成员治理直接相关；任意无交集重配的定理未由该段获得|成熟工程组件线索；真实库到oracle精化待做|
|Foundations of Dynamic BFT；S&P2022 / ePrint2022/597|Sisi Duan、Haibin Zhang；ePrint received 2022-05-17；[ePrint](https://eprint.iacr.org/2022/597)，DOI [10.1109/SP46214.2022.9833787](https://doi.org/10.1109/SP46214.2022.9833787)|R4再次核ePrint题录/摘要、两作者主页；出版方落地只得空壳，PDF依旧不可取。正文SOURCE_UNRESOLVED|摘要明确动态成员与部分同步Dyno；具体安全定义、重配置条件、模型/定理及实现尚未核读|动态BFT直接先例继续登记；D1尚无可依赖的Dyno正文定理/性能对比|
|AID-Guard，arXiv:2608.21159v1|Yingzhe Tong、Leyu Dai、Songhui Guo；2026-08-21；[正文](https://arxiv.org/html/2608.21159v1)|继承R2 §II–IV机制/证明草图及R3 §III-D重核；本轮未重跑工件|当前授权、不可变请求、预算UNKNOWN、终态fence/单继任直接相关；可信边界与Provider合同限定|继续支撑强G业务状态层构造；发表成熟度按预印本记录|
|Root-Scoped Quiescence，arXiv:2609.21284v1|Genliang Zhu、Chu Wang；2026-09-18；[正文](https://arxiv.org/html/2609.21284v1)|继承R2 §§3–5/附录A及R3 A.3；工件执行0|责任转交、支持保持、root/sink/channel cut、不透明历史边界；原生符合性另需证明|B独立路径与原生截止已有直接近邻；维持覆盖判断|
|EFFECTBOUND，arXiv:2609.02866v1|Igor Santos-Grueiro；2026-09-02；[正文](https://arxiv.org/html/2609.02866v1)|继承R2 II-C/III/IV/附录C关键段与R3 C-E；Lean运行0|原生合同、有限模型、配置历史、声明保持与真实精化边界|继续支撑强G原生/配置层；R4补费用/活性责任未建立独立优先权|
|SC-A2A Gateway，IEEE Access14:163751–163772|Hyunwoo Kim、Mpyana Mwamba Merlec、Inseong Jeon、Hoh Peter In；继承IEEE索引日期2026-10-13；DOI [10.1109/ACCESS.2026.3742942](https://doi.org/10.1109/ACCESS.2026.3742942)|继承Crossref题录与IEEE索引摘要；R4 S2/OpenAlex入口不可读；本地OpenAlex投影全null，已改标SOURCE_UNRESOLVED。正文/实现仍缺|摘要支持session grant、链策略/审计的广义重叠；预算、UNKNOWN、旧bearer、在途截止、重配等具体覆盖待正文|来源缺口保留；缺失正文不充任新颖性证据，也不承担完整覆盖证明|

Dyno DOI由继承题录线索及本轮作者到出版方入口交叉定位；正式出版页码等未在本轮新增正文中认证。SC-A2A精确日期引用继承IEEE索引，Crossref本身的published年与created时间分别记录；引用最终参考文献时仍应复核正式出版页。

## 2. R4窄范围补查日志

`evidence/web/web01.json`：Dyno中国ePrint PDF、SC-A2A SemanticScholar/OpenAlex公开URL读取均失败。

`web02.json`：Dyno作者主页线索；modernc sqlite固定包页面不可读；Go官方buildinfo源码说明读取嵌入工具链/模块元数据的用途。

`web03.json`：Haibin Zhang主页的Dyno及同题论文入口；仍指同ePrint正文路径，未取得额外定理。

`web04.json`：官方release API失败；固定Casdoor commit的build.yml可读，工具链及frontend/GoReleaser步骤得到交叉证据。

`web05.json`、`web06.json`：Sisi Duan主页到论文DOI/ePrint的确切链接；ePrint题录/摘要可读，CSDL正文未取得。未以同名系统或其他动态BFT论文替代Dyno。

记录保留URL、定位、实际读取范围与失败状态；不复制整篇论文。空/错误API结果不能写为题录核验通过。来源链条不足时优先继续其他证明任务，当前窄查在这些入口收敛。

## 3. 强G及原创性裁决

[R3强G两轮反证](../R3_STRONG_G_REASSESSMENT.md)逐项保留。G可采用同等或更强成熟动态SMR、持久工作流、受控秘密使用、独立Q_B/Gate/根、全部故障/期限前缀检查、资源扩展知识博弈及相同压缩/优化；全部资源和native尝试同等计费。

R4的Ready角色拆分、费用标签/进展义务、部署控制矩阵和S2(T)见证均可由G采用。在已给逐事件构造中，现有功能与native序列可匹配，双方C_N相等；该结论属于构造覆盖，新增性能实测为0。通信/资本/持有费用尚无必要下界，保持待比较。CUT-ALL等对双方成立，无法用双方不可行输入形成优势。

I1/I2/I3继续COVERED_BY_G / MODEL_BLOCKED；严格分离实例0。来源覆盖状态PARTIAL，公开原创性NOVELTY_UNVERIFIED。新的原生调度优先权也需系统查重和独立运行证据，当前仅作为具体固定源码语义发现。
