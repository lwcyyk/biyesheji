# R17最终裁决与下一步

**研究者已选“全新隔离实例”；具体环境仍未锁定。** 本轮完成现有材料核对、D1启动副作用和独立P1a/P1b边界、三个不可执行命令锁及现场验收矩阵。源码、历史记录保持原字节，测试/服务/进程查询/DB/key/RPC/P1均0。

## 十四问

| 问题 | 准确回答 |
|---|---|
| Q1 合法H2环境已存在？ | 本轮仅确认新建路线，未确认任何当前运行实例或新root。旧M1/L1记录与R16内存夹具不能替代本次指定。 |
| Q2 实例/版本如何锁？ | 研究者指定root/owner/Python/data范围，再用部署SHA、受控加载、OS PID/创建时点、每启动新epoch、DB/connection和listener关联。实际值未取得。 |
| Q3 serve副作用？ | 读私密配置、EventLog、rw SQLite/WAL/PRAGMA、可能Schema/genesis、新key使用、marker/config、TLS私钥、端口/请求线程和ready写入。 |
| Q4 A1可生产激活？ | hook和单次门可复用；当前CLI不传ticket，API为authorize_offline，缺真实Admission/dormant源/元数据/安全生命周期桥。只能登记静态接口条件，尚无可执行完整D1。 |
| Q5 真epoch与授权ID？ | 未来由受信启动器绑定OS创建信息及部署清单生成；P2外部批准绑定该epoch/真实source/scope。当前参数字符串不是现场证明。 |
| Q6 issuer/别名/重启？ | A1同connection/auth/epoch/scope进程级K阻止重建issuer/别名；真实唯一Store、其它connection和重启旧授权失效由D1/P1/P2增加约束，内存表无持久性主张。 |
| Q7 新部署读key/写DB？ | 全新genesis需要新state key加密读取、DDL/INSERT和TLS key加载；数据seed另计。现有Schema2启动仍写marker/config，不能登记纯只读。 |
| Q8 最小修改/命令/回退？ | 缺专用runtime桥、启动/metadata脚本及可能的post-Store/dormant hook。当前argv=null；以后只停拥有且身份匹配的进程，新root失败保留证据，不覆盖或删除旧数据。 |
| Q9 P1a可读什么？ | 指定PID/创建信息/exe/部署/endpoint/epoch及批准的DB/key逻辑引用、挂载状态；不读完整argv/env/secure/token/key/state。 |
| Q10 P1b必要？ | 未定，取决于P1a证据。若需另批，仅一个ro连接，各一次PRAGMA user_version和journal_mode，world/key/decrypt0。 |
| Q11 仍需什么？ | 新root、负责人/服务主体、Python、合成范围及端口策略。首次询问的“1”已记录，不再要求重选。 |
| Q12 三命令均存在无占位？ | 否。旧CLI存在但不满足H2激活目标；专用完整入口缺失，且实际环境/进程/路径未定。三个command_executable均false。 |
| Q13 现在能申请哪项？ | 可提出剩余环境信息确认；D1/P1a/P1b执行申请目前只有明确边界的待填模板，不具有执行就绪条件。缺失代码亦需独立批准后实现。 |
| Q14 距P2还缺什么？ | 专用bootstrap/依赖/部署与实际版本、真实source/epoch、scope/grant/rid和身份/读取权、key/整行解码、真实客户端通道、精确命令/预算/日志和独立P2批准。 |

## 状态

A1_IMPLEMENTED、A1_SYNTHETIC_TESTS_PASSED保持；H2_TEST_ENVIRONMENT_LOCKED=false，H2_TEST_ENVIRONMENT_UNRESOLVED=true。

DEPLOYMENT_ACTIVATION_SPEC_READY仅指本轮生命周期/权限/验收范围已定义；执行就绪=false，bootstrap和真实元数据接口仍缺。D1_AUTHORIZATION_PENDING、P1A_AUTHORIZATION_PENDING、P1B_AUTHORIZATION_PENDING、P2_NOT_AUTHORIZED、REAL_AUTHORITY_READ_NOT_RUN、S3B2_NOT_AUTHORIZED、S5_NOT_AUTHORIZED、SOURCE_OR_REFINEMENT_GAP和ANALYSIS_ONLY保持。

## 独立申请的准确范围

**当前唯一推进项：补齐H2_TARGET_SELECTION_REQUEST的剩余非秘密环境信息。** 选择新建已确认，其余值不由Codex代定；此确认本身不执行或批准部署。

环境及缺失代码固定后，D1申请必须逐项包含：排他新root、一个Authority服务主体/进程、真实依赖/来源版本、端口/ACL、新测试key/TLS配置、明确初始化与seed操作、SQL/key/日志/文件预算、关闭P2读权、拥有进程停止与保留失败记录。已有root或可能接触旧数据时停止，另行审定。

P1a申请仅一个已知PID及批准非秘密metadata路径，无SQL、key或RPC；P1b另列唯一DB、只读/WAL条件、两PRAGMA预算与物理副作用。三项authorization_id、实际argv与目标目前均UNRESOLVED，批准值为PENDING。

D1中新合成key/加密genesis与P2解密读取分开；P1a/P1b不取得任何key使用或整行解码权限。真实状态seeding若使用旧RPC写handler，会伴随read_state与解密，必须独立明确批准，不能藏进D1默认初始化。

下一份输入补齐owner/root/Python/data/端口策略后，可以围绕该具体新环境完成缺失实现和D1精确执行申请；如果这些信息仍缺，保留所有实际值UNRESOLVED，不再重复A1验证。环境选择与D1/P1/P2执行许可分别管理。

本轮为知情模型辅助静态审查；A/B/AB学术创新、typed O/B2、Native来源与持续性、S5及既有文献限制沿原判。
