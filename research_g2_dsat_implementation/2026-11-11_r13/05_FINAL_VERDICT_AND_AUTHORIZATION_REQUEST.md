# R13最终裁决与H1/H2申请

2026-11-11，Asia/Shanghai。本轮完成H0静态审查；H1工程实施、项目测试、H2真实读取、B2与S5执行均为0。当前对话内知情模型辅助审查；外部独立安全核验待取得。

## 结论

**下一轮优先审定H1内部宿主组件的开发与24项纯离线验收。** 推荐宿主为现有Authority服务进程，复用已初始化Store和R12净化适配器。Controller继续通过现有Client参与原业务流程。新RPC、真实数据库/key访问和部署激活分别保持后续授权门。

H1规格已经具备可审查的文件清单、身份/scope合同、单次读路径、测试矩阵和命令。H2还有实际来源与调用入口缺口，`REAL_READONLY_CALL_READY_FOR_AUTHORIZATION=false`。H2文书为精确的**待填值申请模板**，当前缺少安全可执行命令，不能直接用于调用。

## 十四问

| 问题 | 准确回答与证据 |
|---|---|
| Q1 可信宿主？ | `services.serve(role="authority")` 的已初始化Store所在进程；Controller是RPC客户端，缺少本地Store引用。[S02:43–56,277–283] |
| Q2 可靠读路径？ | 持有实例RLock且连接空闲时的 `AuthorityStore.read_state`，经R12适配器一次调用。逻辑世界无DML；execute遥测、fsync、额度与key读取需明确许可。[S01:93–120;S05:433–461] |
| Q3 初始化/恢复/连接写入？ | 构造器会创建目录、rw连接、配置WAL、migration、genesis、marker/config。旧recover特殊分支世界只读但有遥测/key，Controller.recover还网络/缓存/日志写。[S01:47–91,129–133;S02:70–79] |
| Q4 新读入口？ | 需要新的**内部宿主守卫/摘要方法**；可复用原read_state，独立SQLite连接和公开RPC均无本期需求。真实进程内部触发入口仍需另审挂载。[02稿§1,§4] |
| Q5 key/解码/净化边界？ | 全部在Authority可信域。现存单密文行会解码整个state，即使只输出一个tuple也会内部触及其它scope；H2须明确批准该解码域。key不复制到Controller/Agent。[03稿§4] |
| Q6 R12隔离能复用？ | 代码和schema原字节复用，已有合成handle/嵌套canary结果继承。真实字段内容、宿主日志/异常与OS边界仍需H1/H2证据；首期摘要省略所有行和材料ID。[S05:258–309,471–579] |
| Q7 身份与scope？ | 既有Handler识别配置Bearer及operation，但Authority旧call不接收identity，缺per-task B1权限。新增宿主从受信认证事实和独立读取策略发行一次permit，严格绑定单tuple/reader/epoch/输出mask。[S02:301–320;02稿§4] |
| Q8 Agent跨域防护？ | 首期新接口仅限管理宿主内部，Agent出口为空；拒绝正文路径/身份/选择器，所有scope字段精确匹配。多tuple集合展平有笛卡尔积风险；旧status的disposal过滤缺口沿用。[S05:94–131;S02:94–102] |
| Q9 revision与来源？ | 一次SELECT配对a/W；源内核原完整请求digest、handle/grant/origin及attempt/release。a在AAD之外，真实性依赖可信OS/DB；instance/o缺失，摘要也缺外部签名和防整体回滚能力。[S01:21,114–120;S05:258–309] |
| Q10 并发影响？ | 同实例RLock排序本地写；外部连接可提交新版本，结果仅对应读快照点。AS异步状态和持续失活仍独立，Native currentness保持UNPROVEN。[03稿§5] |
| Q11 最小真实调用？ | 一个已批精确tuple、已有至少一条请求、一次B1/最多4条只读验证SQL/一次key读取/重试0；内部净化≤64KiB且≤32记录，最终摘要≤4KiB。源路径/身份/tuple/管理触发命令当前null，执行阻塞。[04稿§3;授权JSON] |
| Q12 H1修改与测试？ | 仅新增内部host模块、新专用测试、全新fixture子树、限定runner；24项H01–H24。storage/services/R12和旧代码原字节保持，无新RPC/实际部署。命令使用既有隔离Python与-B。[04稿§1–2] |
| Q13 H2还缺什么？ | H1结果、已认证管理通道、当前读取策略、指定环境/实例/DB路径/tuple、key和整行解码权限、加载源码与库版本、进程内挂载及精确命令、日志/额度/证据目录/并发前提。激活若需重启或新接线差异须另列授权。[H1_H2_AUTHORIZATION_REQUEST.json] |
| Q14 下一轮？ | 先H1开发/离线验收审批。H2当前缺可执行入口和实际授权值，尚无直接进行受控真实读取的充分条件。H1通过后只推进H2具体申请，不自动执行。[本稿申请及04稿] |

## H1具体申请（当前approved=false）

建议研究者确认以下完整范围后，再进入后继工程任务：

> 我批准R13规定的H1可信宿主内部组件开发与24项离线验收，仅新增 `D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_authority_read_host.py`、`tests\test_dsat_authority_read_host.py`、`tests\fixtures\dsat_authority_read_host\`、`scripts\run_dsat_authority_read_host_tests.py`。实现受信宿主上下文接口、精确singleton tuple读取权、一次permit、reader/epoch绑定、空闲连接与RLock守卫、原R12一次净化调用及独立最小摘要出口。身份/策略/连接/状态均使用新合成输入和替身，实际身份发行链另审。使用既有隔离Python和-B，只运行H01–H24；新文件范围内允许最小修复和有限suite重跑，保留全部失败run。结果限 `D:\毕业设计\research_g2_dsat_implementation\2026-11-11_r13_h1_offline\`，每次新run、单轮120秒软预算、无新依赖。原R12适配器及storage/services/protocol/migration/S1/S2/S3-A/历史结果保持原字节；不导入/构造运行服务、不打开SQLite、不读真实key/config/state、不启动进程或网络、不新增RPC、不重跑旧115/46/33项或整仓、不调用求解器/检查器、不进行部署激活/B2/S5。Native与完整数学输入缺口保持，math_ready=false、current_native_eligible=false、global_complete=false。需要更改旧文件、连接真实Store或扩展测试范围时，提交新的具体申请。

批准文本、四个完整目标路径、拟议命令和资源界另以机器格式冻结。H1当前全部NOT_RUN；本轮文件只包含设计和申请。

## H2申请模板与阻塞

拟批准事项：仅在指定环境和现有Authority进程中，以指定管理身份、独立读取权和精确tuple，执行04稿的单次读取及验证序列，输出固定管理摘要。key只在原Authority域使用一次，整行解码范围需要明确同意。已有服务、连接、key、WAL/SHM和业务授权保持原有生命周期，自动重试0。

待填写：`environment_ref`、`authority_process_ref`、`authority_instance_locator`、`database_path`、`authenticated_principal`、`authentication_evidence_ref`、`read_permission_ref`、`read_scope`、`approved_existing_request_ref`、`key_access_boundary`、`whole_state_decode_approval`、`loaded_build_refs`、`internal_invocation_entry`、`deployment_activation_scope`、`exact_command`、`evidence_output_root`、`log_policy`、`writer_observation_conditions`。值当前全部null；路径或账号未被猜测。

当前最关键阻塞是：serve内的Store只为闭包局部对象，已有命令均不能直接触发新内部读。`cli init/serve/request/trace/m1` 会初始化、加载配置、启动或调用旧服务，无法代替本申请。H1离线通过后，应围绕实际选定宿主设计可审查的进程内管理触发与激活差异，再固定真正命令。过程若要求服务重启、读取运行配置或新端点，逐项单独申请。

H2申请模板的审阅完成，与可执行H2请求就绪分开登记。当前没有询问或使用真实密钥值，也无需研究者将密码、Token或key粘贴至对话。

## 状态表

| 状态 | 当前值 / 前提 |
|---|---|
| TRUSTED_HOST_IDENTIFIED | true；源码中的Authority进程，不表示已验证运行实例 |
| READONLY_CALL_GRAPH_REVIEWED | true；锁定源码及静态闭包 |
| B1_SECRET_BOUNDARY_REVIEWED | true；设计与继承的合成结果 |
| HOST_WIRING_SPEC_READY / TRUSTED_HOST_INTERFACE_READY | true；H1内部组件规格 |
| H1_READY_FOR_IMPLEMENTATION_REVIEW | true；approved=false，未写实现代码/运行测试 |
| H2_READY_FOR_AUTHORIZATION_REVIEW | false；执行级申请缺源值、入口及命令；模板已备 |
| REAL_READONLY_CALL_READY_FOR_AUTHORIZATION | false；与H1就绪分别判断 |
| H2_AUTHORIZATION_PENDING | true；H1和运行取证仍为依赖 |
| REAL_READONLY_CALL_NOT_RUN | true；真实调用0 |
| S3B2_IMPLEMENTATION_BLOCKED | true；B15/B27/B28及生产typed O/o/CAS/migration/旧writer门保持 |
| S5_NOT_AUTHORIZED | true |
| SOURCE_OR_REFINEMENT_GAP | true；本地revision/净化无法补Native全源和持续性 |
| ANALYSIS_ONLY | true；H0完成 |

## 唯一下一项动作

**审定并独立批准上述H1四目标、24项纯离线接线任务。** 成功取得宿主组件的权限、单次读和净化摘要证据后，才有依据形成绑定实际环境的H2可执行申请。若精确scope、来源绑定或秘密出口失败，收缩/修复此组件并保留H2阻塞；B2/S5及算法创新资格继续分别管理。

本轮因R13请求第十一、十二节的明确授权边界停在H0。继承结果、静态支持、后继离线实现和真实安全保证各按证据范围登记。
