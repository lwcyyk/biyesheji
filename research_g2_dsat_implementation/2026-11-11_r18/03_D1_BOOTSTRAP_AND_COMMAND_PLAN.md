# D1-A/B任务与命令准备

## 修正启动顺序

候选流程按当前AES-GCM合同调整为：新root/权限检查 → Python/依赖/批准manifest → 新测试state/TLS材料 → 规范合成state → 加密并准备新Schema2 DB → 唯一AuthorityStore构造 → dormant来源绑定 → Handler/TLS → 非秘密runtime metadata → 后续另批P1。

key必须先于需要它的加密写入；当前Store在genesis时直接cipher读key，不能先启动Store再假定key之后可补。推荐**受审预置新Schema2＋加密seed**后再启动Store，避免直接把spy blob写入DB或隐含执行旧RPC解密/写入。

| 步骤 | 现有位置/缺项 | 副作用与权限 |
|---|---|---|
| root/manifest/依赖核验 | 新启动桥待实现 | 仅新路径/白名单；实际依赖导入属于后续受批验证 |
| 新合成state/TLS材料 | lab.py47–95有成熟参考，但会准备三角色并分配多个端口 | D1-A实现Authority-only版本，D1-B才生成文件；不读取旧secret |
| 规范seed与加密新DB | R16只有结构/spy；专用准备器待实现 | 使用新key/真实AES-GCM、现有AAD；仅新库DDL/INSERT，不解密已有state |
| Store初始化 | storage.py47–91 | 预置Schema2/状态行时约7次execute，无genesis key读；marker/config/日志仍写 |
| dormant源绑定 | services.py293–297已有hook；dormant与真实Admission待补 | 捕获同一Store/lock/connection，注册0 SQL/key，P2默认关闭 |
| Handler与TLS | services.py299–365已存在 | 单回环端口、TLS private key加载；无Controller/Provider |
| metadata/停止 | 当前ready不足，runtime桥待补 | PID/创建时点/新epoch/实际端口/版本与source引用；只关闭拥有进程 |
| P1a/P1b/P2 | 入口/真实身份与许可后续固定 | 与D1-B分别审批 |

如果改走空库ctor，约12次execute、genesis新state key读1次；它仍无目标rid。推荐预置方案需要额外的seed准备SQL和一次加密，但避免把普通grant/admit RPC的read_state费用藏进准备。两者总费用都要由实现后的操作清单冻结，不能只比较7与12。

新state推荐符合两步grant/admit合同的初始化快照，标明“合成准备”。grant实际ID和handle未来生成；请求QUEUED，无Native dispatch。初始a/合成历史及grant_ops/digest须一致，并在D1-A校验。legacy O可能为空，但保守source/queued hold仍存在，typed O/o不填默认完整值。

## D1-A：最小代码实施范围提案

本轮不写工程代码。下一轮拟仅修改services.py一个既有文件，新增以下五个Python文件及一个fixture子树，共七个逻辑目标：

1. 修改services.py：可选类型化runtime context、唯一Store构造后的dormant绑定、实际listener/metadata回调、拥有资源finally关闭；原默认路径和A1 ticket路径保持。
2. 新src/auth_lifecycle/online_state/dsat_authority_runtime.py：配置解析/批准边界、路径与合成seed构造、新库准备、dormant descriptor、每启动epoch/单活、白名单metadata和拥有进程清理。
3. 新scripts/run_h2_authority_service.py：严格启动manifest、Authority-only、P2关闭、无现有root回退/自动重试。
4. 新scripts/inspect_h2_authority_metadata.py：P1a单实例白名单、无secret/env/DB读取。
5. 新tests/test_dsat_authority_runtime.py：配置、seed/codec/SQL、dormant、metadata/生命周期的离线验证。
6. 新scripts/run_dsat_authority_runtime_tests.py：限定新验证及必要回归，输出新run；不修改旧runner/锁。
7. 新tests/fixtures/dsat_authority_runtime/：纯合成输入与公开测试key/codec向量。

runtime模块和脚本仅在D1-B获批后允许创建真实测试根/key/DB/进程，离线测试不触及候选根。P1b专用脚本暂缓，避免尚未证明必要就扩大实现。

D1-A验证至少覆盖：七项路径/版本边界、真实Schema2有界加密往返的合成向量、规范grant/request/digest、未批准manifest拒绝、唯一Store、dormant0读/P2不arm、每启动epoch、白名单metadata、拥有资源关闭及停止、端口失败不回退。新测试分母在实施任务中单列，不伪造已执行数。

原44项A1/H1回归保持断言。其A17要求无services/storage/materials/cryptography导入，故不能与D1-A密码学/服务定义验证混用同一模块域。未来runner应受控分开离线进程/环境域并保存独立分母；必要的拥有子进程次数要在实施执行范围中明确批准，禁止删模块/改旧断言制造通过。

## D1-B：实际准备/启动

D1-A通过不触发D1-B。D1-B还需确认候选五项、实际OS主体/目录权限、固定源快照和依赖、加密seed/key/TLS/SQL预算、27443绑定、拥有进程启动/停止、输出限制及独立授权。仅写新root，存在则停止，不自动迁移/修复/复用旧数据。后台进程隐藏窗口启动，保留失败证据，禁止全局kill或自动删除。

当前代码位置和来源快照候选已经给定；实际部署SHA必须包含D1-A新增/修改文件后重新固定。部署前不假设当前源码digest已经覆盖尚未实现的桥。

## 三份命令锁

D1/P1a/P1b的actual_argv均为null，command_executable=false。root/Python/数据/端口提案已具体化，主要阻塞转为**参数待批准＋入口未实现/参数不受现CLI支持**，不再要求研究者重填空白方案。

D1_COMMAND_LOCK列出未来proposed_argv与具体候选输入路径，但明确未创建新脚本、未声明该参数已获当前CLI支持。旧online_state.py的init/serve存在，却不能传runtime/dormant context，故不当作D1-B命令。read_dsat_authority_once.py当前仅offline，同样不能承担真实P2。

P1a先实现单PID检查脚本，再根据已启动进程填入PID/创建时点与已批文件；P1b仅必要时另批ro连接和各一次PRAGMA user_version/journal_mode。P1不读取新/旧key或state，P2另批一次真实读和整行解码。

所有环境、依赖、初始化、DB、key、logging、activation、network、P1/P2性能均NOT_MEASURED。已知静态次数、候选上限和实际数值分别保存，不把准备器/服务构造或验证查询当作免费。
