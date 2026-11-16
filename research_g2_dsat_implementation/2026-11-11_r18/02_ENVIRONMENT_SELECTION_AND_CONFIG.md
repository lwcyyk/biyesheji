# 五项候选与完整配置

## 推荐组合

| 参数 | 推荐值 | 依据与核验 | 状态 |
|---|---|---|---|
| environment_owner | 当前请求提交的课题研究者兼研究/批准/数据保管；Codex仅在单独授权后执行；服务使用研究者控制的专用进程 | 不从Windows目录名推断姓名；本人确认角色，D1-B前另核OS主体/SID与权限 | NEEDS_OWNER_APPROVAL |
| deployment_root | **D:\毕业设计\h2_test_runtime\h2-authority-synth-001** | 位于指定研究磁盘，独立于auth-lifecycle源码、旧.runtime及研究归档；本轮Test-Path显示根及父目录均不存在 | CANDIDATE，未创建 |
| python_executable | **C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe** | 版本资源3.12.14、PE AMD64，已有匹配cryptography及依赖元数据 | CANDIDATE，实际导入待后续 |
| synthetic_data_scope | 一套新合成身份/账户/任务，1个grant＋1个QUEUED issue请求；handles/密钥未来新生成 | 复用R16结构与预算/摘要合同，不复制其canary值、spy blob或任何真实Token | NEEDS_OWNER_APPROVAL |
| port_policy | **127.0.0.1:27443，固定单端口TLS，失败即停、无自动替换** | 当前Client允许该格式且避开18080/18081/8080；本轮未查询占用或bind | CANDIDATE，运行前检查 |

environment_id候选为h2-authority-synth-001；这是新提案，不冒充已存在实例。当前交互Windows主体可作为受信进程候选，实际账户/SID不从用户名推断；目录/数据/进程隔离不能替代对恶意同OS主体的强沙箱。若需更强隔离，应在D1-B前指定受限token/独立身份，不改生产ACL。

## 路径布局与现有服务合同

保留现有Authority相对路径，避免为了整齐目录改变存储合同：

- config/deployment.json：未来获批后的非秘密部署manifest。
- secure/authority.key、server.key、server.crt、authority.json：新测试state/TLS/私密角色配置；P1不读secret内容。
- authority/authority.db、-wal、-shm、database_ops.jsonl、transport.jsonl、initialized、storage_configuration.json：现有实现要求的DB/日志/marker。
- runtime/：拥有进程/epoch/单活锁、dormant metadata与停止请求；与旧.runtime分开。
- logs/：净化启动诊断；evidence/：批准与P1结果；tmp/：仅该实例临时文件。
- artifacts/src：拟议来源快照，只拷贝批准的Python/SQL源码，不拷贝.venv、.runtime、旧DB/key或研究日志。

所有完整候选绝对路径均在H2_ENVIRONMENT_CONFIG中推导并标为候选；当前实际文件值不存在。主源码在D:/毕业设计/auth-lifecycle，部署后加载位置预期来自新root的artifacts/src；实际快照SHA必须在D1-A实现完毕后重新固定。

## Python与依赖的实际静态检查

| 项目 | base候选 | H1 venv |
|---|---|---|
| CPython文件版本/架构 | 3.12.14 / AMD64 | 3.12.14 / AMD64 |
| cryptography | 50.0.2目录与METADATA存在，符合项目固定版本 | 常规包目录缺失 |
| cffi / pycparser | 2.1.1 / 3.11元数据存在，满足已读Requires-Dist/Python条件 | 本轮无需补齐该venv |
| SQLite | _sqlite3.pyd及sqlite3.dll存在，DLL版本3.53.1.0；R16同基础标准库曾执行3.53.1 | R16已执行内存SQL3.53.1 |
| 运行导入/服务 | 本轮未执行 | 不因H1通过推定服务可加载 |

cryptography wheel tag为cp311-abi3-win_amd64，cffi为cp312-cp312-win_amd64，与候选CPython/AMD64静态约束相容。实际DLL加载、环境路径/冲突和模块导入仍需后续受控验证，PYTHON_RUNTIME_VERIFIED=false。

本地许可证：Python LICENSE.txt提供PSF等许可说明；cryptography元数据为Apache-2.0 OR BSD-3-Clause，cffi为MIT-0，pycparser为BSD-3-Clause。LICENSE/WHEEL/METADATA/INSTALLER及关键二进制hash已记录。INSTALLER=pip只说明安装机制，缺direct_url和原下载wheel证据，安装来源的精确URL/SHA与供应链真实性未被补证。

首选base候选无需预设安装新依赖；没有发现其已读声明依赖缺口。若实际导入失败则停止，另给精确最小补齐申请。若坚持使用原H1 venv，至少需重新审定cryptography50.0.2及其依赖，当前不安装、不默认回退。

## 合成范围

推荐非秘密标签：管理身份h2_metadata_reader_001，业务caller h2_agent_001，account h2_account_001，task h2_task_001，audience h2_audience_001，generation h2_gen_001，request rid h2_issue_001。grant别名h2_grant_001，实际grant_id与handle未来新生成并建立映射。

目标是1个active grant，operations=[issue]、limit=1/reserved=1/spent=0，以及1个QUEUED请求，attempt/release/result均null。原请求digest按现有normalized_request和caller重算。初始化历史标为合成准备来源；disposals/windows为空；不制造typed O/o，QUEUED创建前沿和来源hold继续由原B1保守导出。

R10是专用明文合成S3-A合同，不能作为真实Authority文件库；R12/R14/R16只复用字段/拒绝/预算/摘要等模型结构。R16的最小casdoor材料/codec spy不是完整原生材料，不原样搬入真实服务。新seed使用现有validate_material可接受的全新synthetic字符串材料，数量与来源明示；无网站账户、无AS请求、无真实凭据复制或脱敏改名。

## 网络

当前真实serve依赖TCP TLS回环；没有已审生产进程内管理通道可省掉整个监听器。D1-B只申请一个Authority listener，外网监听、端口映射、防火墙开放、Controller/Provider/Agent和Casdoor均禁用。固定27443可以避免现有port=0 ready记录问题；占用状态未知，未来bind失败即退出并保留证据，不扫描/自动挑另端口。
