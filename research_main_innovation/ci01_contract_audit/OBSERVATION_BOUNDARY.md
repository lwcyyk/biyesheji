# 观察、时序与运行者知识边界

## 本轮新取得的事实

在正常控制N01中，A0.RT撤销后A0的userinfo返回401，B0及新发行B1返回200且主体匹配。B重新授权后，旧A0.RT重试返回400 invalid_grant。[N01原始观察](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run01/N01_normal_observations.json)

在主见证W01中，A1在父RT撤销响应之后仍获得userinfo 200，AT与RT内省均为true。该观察位于B的新批准/重新授权之前。A1迟到响应交付后，固定序列通过原生revoke(A1.RT)收尾，终点A0/A1均拒绝，B0/B1仍接受，A1.RT再次刷新返回400 invalid_grant。[W01原始观察](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run01/W01_delayed_refresh_observations.json) [主事件](D:/毕业设计/research_main_innovation/ci01_contract_audit/EVENT_WITNESS.jsonl)

因此，本条轨迹中的新B授权与A1的存活不具有“B使A重新生效”的因果证据。A1已经在该新授权之前可被资源接受。真正的反例对象是“撤销已消耗旧RT并收到200，足以宣布整个登记后代范围已停止”。

## 时序约束

|轨迹|客户端可观察顺序|额外依据|可以给出的服务器判断|
|---|---|---|---|
|W01|refresh请求完成到采样器seq167，随后父revoke发送seq170并返回seq171，B新批准阶段seq195，B1发行后迟到响应交付seq215|S1的AddToken/DeleteToken在RefreshToken返回前执行，S2随后响应。运行文件匹配指定发行包|可在源码符合性前提下确定本次A1创建先于后续父revoke请求。具体DB提交时刻未测|
|历史concurrent_race-1|旧revoke和refresh请求区间重叠，revoke响应先返回，随后refresh响应及新AT active|历史客户端日志和本版本函数路径|保留满足观察与源码依赖的全部交错，不从响应先后选定一个全操作线性化顺序|
|userinfo检查|接受检查请求在父revoke响应之后才发出|真实GET响应和正确sub、签名/账户/受众检查|确有后续资源接受，范围限于该userinfo端点|

RefreshToken由多个读写步骤组成，当前没有完整事务线性化事件。历史成功竞争可能包含旧token读取后发生撤销、再插入新token，也可能先完成刷新再处理未知旧token撤销。应以偏序约束表示相容顺序，未列举的相容交错继续保留。[函数路径](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/token_oauth_util.go) [历史原日志](D:/毕业设计/auth-lifecycle/results/experiments/survey04/survey-casdoor-concurrent_race-1.jsonl)

## 运行者与评分者

`runner_visible.jsonl`只包含交付给运行者的响应和实验流程标记。完整HTTP日志记录采样器暂存响应及评分者的检查，原始日志共307事件，运行者投影29事件。投影没有independent_acceptance、native_record_witness或提前交付的held响应。源码中的sample只输出观察并返回None，固定方法序列使用已交付响应中的材料。[运行者视图](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run01/runner_visible.jsonl) [核对记录](D:/毕业设计/research_main_innovation/ci01_contract_audit/EVIDENCE_AUDIT.json)

该隔离在取证程序的数据流和日志投影层成立，采样器与观察者仍处于同一Python进程。操作系统进程隔离、恶意观察者和计时非干扰均未验收。取证调度可以知道被缓冲HTTP已经完成，运行者在迟到交付前得不到其内容或独立评分结果。

## 授权来源与材料来源

g0/g1是本轮预先授权实验中的任务批准标识。进入该阶段是取证程序的实测事件，用户实时确认、批准签名和生产批准数据库尚无对应证据。Casdoor password grant只证明其原生认证条件，A/B逻辑任务及批准代次由可信客户端责任链提供。

A0.RT→A1的来源来自冻结调用序列和实际响应。JWT及token记录没有直接携带本研究任务批准代次，日志标签本身也不构成原生签名收据。HTTP记录保留方法、路径、字段名和响应的安全投影，具体输入token值的绑定由冻结源码及材料别名推导，另存为SOURCE_DERIVED。该层级不能被提升为独立抓包或服务端提交证书。[源码推导绑定](D:/毕业设计/research_main_innovation/ci01_contract_audit/REQUEST_BINDINGS_FROM_SOURCE.json) [冻结源码快照](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run01/source_snapshot/collect_evidence.py)

历史JWT验签的离线重算需要原始JWT及当时JWKS。本轮保留材料摘要和核验结果，复现以冻结实现的新采样为入口。

## 保留、后代与迟到隔离的范围

本轮B在关键切点均可用，连续前缀结论还依赖冻结环境、源代码效果以及无其他管理操作等前提。A的后代范围限定为登记的一次刷新A1，实际恶意主体可能继续派生或建立其他支持的情形尚未被本次采样穷尽。

迟到结果一直关联A-refresh-1和A.g0，B1关联独立的新发行。取证变量及事件没有把A1改标成B1。该事实只支撑取证序列的来源分配，应用控制器在重启/回滚后能否保持同样隔离，仍为OBSERVATION_INSUFFICIENT。若A已取得A1并能在其撤销前继续刷新，须把进一步后代和竞争全部加入后续模型。

userinfo使用无cookie的Bearer请求，S6标明这种请求的会话状态仅保留内存。独立观察未借管理员身份访问userinfo。其他业务资源、会话Cookie、离线JWT、跨应用SSO以及外部效果E各有不同接受规则，当前研究结论绑定本次端点与profile。[Bearer过滤器](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/auto_signin_filter.go) [会话持久化规则](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/session_provider.go)

响应中的ID token也只保留摘要，其跨RP使用未进入本轮接受检查。清理成功特指四个测试用户删除、登记AT/RT在所选在线接口失效、已登记迟到结果全部交付，以及当前管理会话logout返回成功。

## 证据文件的类型

EVENT_WITNESS.jsonl仅含新采样事件及其原始seq/hash定位。HISTORICAL_EVENTS.jsonl继承历史竞争日志。PAPER_EVENTS.jsonl记录旧快照双历史和未实施组合的纸面推演。SOURCE_DERIVED记录通过版本源码解释原生动作，分类依据与运行结果状态分别登记。

## 两项源码驱动补充

C01在与主见证相同的password grant配置下，仅用client_id、RT、grant_type和scope执行两次刷新，均返回200并产生可被userinfo接受的后代。每次随后撤销已消耗的父RT，当前后代仍活跃。最后撤销当前A2后，其无secret刷新返回400，userinfo拒绝，B0仍接受。这支持两步原生能力见证，更长链的结论须声明其守卫和调度前提。[C01记录](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run02_secretless/observations.json)

C02对同一本轮新建用户使用相同过滤查询。普通Bearer得到HTTP 200、业务status=error，应用client_id/secret经Basic认证得到status=ok及两项记录，其中AT/RT句柄摘要分别匹配A1与B0。查询参数只需已知账户标识，不需要A1句柄。它确认了可用的原生枚举能力，同时说明HTTP 200与业务成功应分别判断。[C02结果](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run03_listing/result.json)

这两项补充于执行前分别登记，原主见证的动作、目标和结果继续绑定其旧冻结副本。补充仅观察能力，当前运行者没有据此自动使用管理列表完成恢复。四个条件累计511事件、44项接受检查，分类预算全部满足。[统一核验](D:/毕业设计/research_main_innovation/ci01_contract_audit/EVIDENCE_AUDIT.json)

## 文档保证的使用范围

RFC 7009 §2.2规定，被成功撤销或已经无效的token都可得到200。§2.1讨论同一授权grant上的相关材料处置，对支持AT撤销的AS提出相应SHOULD要求。Casdoor的RevokeToken接口注释也把200描述为revoked或unknown。主见证中的旧RT在轮换后已失去其记录，因此200本身无法提供当前后代清单。是否违反更强的产品承诺，仍需明确产品对authorization grant及后代的定义，本轮按实测契约能力裁决。[RFC原文](D:/毕业设计/research_secret_recipe/sources/rfc7009.txt) [Casdoor接口注释](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/controllers/token.go)
