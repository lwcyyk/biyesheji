# DCL-R3终稿复查记录

2026-11-10。同一知情对话内按源码、分布式协议、费用语义与反方审稿角色分别推导，外部独立评审未取得。新原生实验/机器验证0。

## 三个审查检查点

|检查点|发现的主要问题|处理|
|---|---|---|
|源码/范围|仅从SQL语句分开无法独立排除ORM隐藏事务；名义grant不等于存储分类|补固定XORM/SQLite及session锁证据；明确SOURCE_FEASIBLE的部署条件；修订入口矩阵|
|协议/组合|两个静态quorum不自动连接；只传root不能保证对象可用；Seal并未冻结Native世界|唯一child＋验根全状态＋固定genesis；明确Ready/Activate；新增空窗Closure_env与cost_envelope|
|终稿/目标|顺序Seal会暂停主Q，可能破坏原B Gate支持；检测后失效不排除先前泄露效果；费用公开时不能人为隐藏|I7和单路径失败裁决；DYN1/鲁棒未观测闭包；费用观察前提与阈值证明；G取得全部同等修正|

## 额外一致性修订

- 明确WAIT_ACTIVATE→RECOVERING；F复制哪些字段、重置哪些epoch局部字段。
- 拒绝未证明代码/schema/profile升级借重配置进入；共同root不包含副本私钥/局部PBFT投票缓存。
- 将提案中的父配置身份与尚未产生的父Stop链接分开，明确承诺依赖DAG，避免Cfg→Stop→Cfg或RHO自指哈希。
- Seal前Abort清pending、保留业务义务；Seal后无自行改选child/回退。
- 业务去重跨epoch，PBFT内部client序号与业务intent分别处理。
- 新增GetAccount缺session token时的条件创建路径，未把UserInfo读路径改判为创建。

## 来源障碍与独立性

PBFT PDF多入口失败，官方分节HTML成功；Dyno ePrint PDF403，官方元数据/作者列表可读；SC-A2A官方正文/公开代码仍缺。UCON取得作者PDF并限定核读段落；XORM1.1.6原文与SQLite官方规则可读。所有失败/读取范围保存在web记录，未猜测正文。

R3 web记录保存URL、定位命令、实际返回行范围和失败状态；论证与来源含义由审查稿记录。原工具结果包摘要另存WEB_RAW_RESULT_HASHES.json，用于过程版本识别；它不承担原论文完整性或语义证明。

纸面规格完整性只在明示模型中授予条件状态。旧委员会签名生命周期、真实独立故障域、V/Gt防回滚、DB/二进制符合性、完整外部入口/效果及实际部署仍需证据。I1/I2/I3两轮后均未存活严格分离，建议归档其独立主创新主张。
