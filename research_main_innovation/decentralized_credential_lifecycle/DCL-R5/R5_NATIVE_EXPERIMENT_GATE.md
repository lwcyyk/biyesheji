# R5四轨迹隔离原生实验准入合同

2026-11-10。状态PREPARED_FOR_AUTHORIZATION，NOT_AUTHORIZED_TO_EXECUTE。新增构建、测试、native请求、账户操作和hook代码均0。本文的命令/请求为未来审查材料；现有工程、18081实例/历史账户及研究归档保持冻结。

## 1. 权限、目标与写入范围

未来根目录拟为`D:/毕业设计/DCL-R5-isolated-native/<run-id>`，下设source-clean、source-barrier、toolchain、gomodcache、dist、config、fixture、runtime、scorer-private、method-view、evidence与budget。所有路径先解析为绝对路径并验证位于此run目录，禁止复用原`.runtime`、私钥、secrets.json、数据库或issuer硬编码harness。原源码只读作为比较对象，独立源从固定commit取得。

仅访问`http://127.0.0.1:28451`。启动前检查该端口空闲，冲突即停止，不自动改端口；httpaddr=127.0.0.1，issuer/discovery所有端点必须精确匹配此端口，禁止重定向/系统代理/外部回调。barrier控制使用带run-id的本地named pipe及私有ACL，不另开HTTP端口。原18081、18080和历史端口均在拒绝名单。构建取源/依赖若需公网，权限单列限官方仓库/Go模块服务，不提供项目秘密。

申请权限包括：取得并锁定Go1.26.10/依赖；创建验证harness/监督器与最小barrier diff；编译两个工件；启动/停止本批自己的服务；合成bootstrap管理员、组织、应用、四用户和新签名证书；114次HTTP总上限及下列逐端点子限；新实例同业务连接的只读PRAGMA/Stats、私有一致DB备份/快照、日志/加密证据写入。候选机制实现及真实跨域部署不在其中。

新bootstrap用户名为`built-in/r5-bootstrap-<run>`，只存在于新DB，用新生成私密密码；不使用冻结builtin/admin的秘密。startup init_data仅初始化合成bootstrap/自有证书及必要登录app字段，禁预置OAuth Token行，`initDataWatchInterval=0`。固定main.go在InitFromFile后才完成后续服务启动；fixture内容、对象Owner/Name/IsAdmin/证书范围须在执行批准前审阅。默认公开证书/默认管理凭据需在本隔离环境启动流程中替换或禁用；若未能按计划完成则停在setup，不触碰其他环境。

## 2. 未来命令清单

所有命令仅在上述新路径运行，`<…>`为执行批准时必须绑定的工件/哈希/参数，并非当前可运行脚本。

|目的|拟执行命令/操作|必要约束|
|---|---|---|
|环境检查|`Get-NetTCPConnection -LocalPort 28451 -State Listen`；`Get-FileHash <Go1.26.10工具包> -Algorithm SHA256`|无空闲端口或工具摘要未认证则停；Go1.20仅曾作元数据读取|
|固定源|在新source-clean取得固定commit；`git -C <source-clean> rev-parse HEAD`和`status --porcelain`|完整所需源/模块与编译目标静态审阅；不fetch到冻结稀疏源|
|依赖|`<Go1.26.10>/go.exe mod download`，其后`go mod verify`|GOMODCACHE/GOCACHE/GOPATH均新run目录；保存MVS/go.mod/go.sum前后哈希；网络范围需授权|
|干净源编译|`go.exe build -mod=readonly -buildvcs=true -ldflags "-s -w -X github.com/casdoor/casdoor/util.BuildType=release" -o <dist>/casdoor-clean.exe .`|不执行GoReleaser before hook/全套测试；版本变量保留源状态，单列与正式发行配方的差异|
|barrier编译|同构建命令，从source-barrier输出casdoor-barrier.exe|只有获审hook diff；禁止变更ID生成、验证、事务和业务分支；两工件哈希均锁定|
|启动|`Start-Process -FilePath <casdoor-barrier.exe> -ArgumentList '-config <run>/config/casdoor.conf' -WorkingDirectory <run>/runtime -WindowStyle Hidden -PassThru`|进程ID、exe摘要、命令行、监听地址均匹配计划；stdout/stderr仅私有run文件|
|四轨迹|`<reviewed-harness> --plan <locked-T1-T4-plan.json> --authorization <bound-receipt> --base http://127.0.0.1:28451`|harness尚未创建；请求逐次预算预留，超时/失败计数，无自动重试/redirect|
|关闭|停止harness后仅停止本次记录且exe/命令行匹配的PID；再备份本run的DB/证据|PID归属不匹配即人工处置；不按进程名批量终止；不递归删除工件|

Go env/版本查询与依赖取得、编译均属于未来执行授权。clean build用于来源基线；本批四轨迹跑barrier build，不能据它宣称现存dirty发行物并发已复现。自然并发release试验需要新范围。

构建阶段拟申请总墙钟60分钟、进程树峰值4GiB；运行/四轨迹含setup/测量/cleanup另限30分钟、进程树峰值4GiB。任一超限INCONCLUSIVE，无自动扩容。环境/进程/端口检查不发HTTP，所有HTTP健康检查也必须占下表明确槽。

## 3. 逐端点请求与setup依赖闭包

新组织`r5-study-<run>`，应用Owner=admin、Name=`app-r5-<run>`，四非管理员用户T1–T4各一；新client_id/secret。应用JWT、rotation开启、password及refresh_token允许，AT/RT期限至少覆盖本次运行及裕量；无DPoP、第三方身份、邮件/SMS或外部webhook依赖。所有模板从新实例读取，副作用记录在新DB。

|阶段/目的|HTTP及受限参数|数量上限|依赖/证据|
|---|---|---:|---|
|setup discovery|GET /.well-known/openid-configuration|1|端点全部28451，失败停止|
|setup keys|GET /.well-known/jwks|1|匹配本run签名证书|
|setup admin|POST /api/login，合成bootstrap/app-built-in|1|新Cookie jar，禁用GetAccount来“探测登录”|
|setup组织模板|GET /api/get-organization?id=admin/built-in|1|只读新DB内模板|
|setup组织创建|POST /api/add-organization|1|合成新Name，无重试|
|setup应用模板|GET /api/get-application?id=admin/app-built-in|1|复制前删除/替换外部集成与秘密|
|setup应用创建/读取|POST /api/add-application；GET /api/get-application?id=admin/app-r5-…|各1|新org/证书、rotation/期限/GrantTypes静态比对|
|setup四用户|POST /api/add-user；GET /api/get-user?id=r5-study-…/r5-T…|各4|记录实际ID、Owner/Name、新密码来源|
|setup四父材料|POST /api/login/oauth/access_token，grant_type=password|4|每用户一次；保留原始AT/RT和ID指纹|
|setup基线|GET /api/get-tokens?owner=admin&organization=r5-study-…，不带分页|4|每轨迹前的完整合成范围；其他轨迹按不同用户隔离|
|method|见下一表的refresh/revoke|8实际操作槽，保留16阶段上限|没有另8次可自由使用的请求权限|
|measurement|每个本轨迹已知父/子GET /api/userinfo；POST /api/login/oauth/introspect hint=refresh_token；每轨迹一次同范围get-tokens|8份材料×2＋4列表=20；沿用阶段封顶28|AT真实fresh接受；RT只读内省；scorer范围/方法权限分离|
|cleanup|详见§5|40|覆盖材料、用户、app/org及验证|

setup依赖总数24，沿用阶段上限30，剩余6只作未消耗容量，不授权额外请求。一个模板/创建/认证失败立即停方法流程，保留已创建资源进入预算内cleanup；不通过更多登录/查询“修好”setup。此约束使setup依赖封闭且可复查。

## 4. T1–T4及barrier精确位置

|轨迹|预登记method顺序|请求数|必要测量/预期判据|
|---|---|---:|---|
|T1|revoke父RT并收ACK，再首次refresh读父|2|无该refresh子提交；请求拒绝；DB/接受结果各自留证|
|T2|refresh停在生成后/Insert前→revoke父RT并收ACK→放行原refresh|2|ACK严格早于子Insert提交；新子fresh AT接受另判|
|T3|两个refresh均生成后/Insert前停住→依次放行H1/H2至完成|2|两不同子提交；第二次父Delete 0行/返回行为如实记录|
|T4|首refresh完整返回，再用旧RT发第二次refresh|2|一子创建、第二次拒绝；检查rotation和父状态|

固定`object/token_oauth_util.go` hook位于705行生成完成之后、738行AddToken调用之前；不得在259行Engine.Insert的事务/写锁内部暂停。T2的因果握手为`ready(H1) → scorer发revoke → scorer收到ACK → release(H1) → Insert提交`。T3需收到两个ready，再按H1/H2顺序放行；随机ID保持原生成语义。每个barrier等待上限20秒，超限退出见下文。

Insert提交、Delete影响行数和ACK记录来自被动私有scorer观测；新增探针不能再执行SQL或包住原调用为新事务。观察hook在原语句返回后记录结果、可能丢观测的崩溃标UNKNOWN，不能把“完成日志行”无条件当作DB提交。DB一致快照/因果事件交叉检查。runtime版本/PRAGMA观测使用实际业务连接的只读hook，查询也登记额外SQL I/O及可能影响；若无法证明观测不改变所检原子边界，缩小结论或停试。

初始四父材料各属不同用户/意图；拟议固定顺序为T1→T4→T2→T3，串行控制先行，各自handler全静止后才清理该用户。按T1/T2/T3/T4编号的最大已知材料数分别1、2、3、2，共8；未收到子响应但scorer识别的子只供评分/清理，不传给方法。未知额外创建、身份不符或槽溢出触发停止，禁止用额外枚举冲淡边界。

## 5. cleanup分配与114上限核算

R4每轨迹cleanup≤10的均分无法覆盖NC2的三份材料完整验证。本轮在全局40内重分配，T3为12，其余6/9/9，另4用于共享app/org；总上限114保持。

|清理对象|操作与次数|总计|
|---|---|---:|
|每条已知材料（含已删除父）|POST revoke RT、GET fresh UserInfo、POST RT introspect，各一次；已缺失材料也如实留拒绝/无效证据|8×3=24|
|四轨迹用户|各一次GET合成范围get-tokens、POST /api/delete-user、GET /api/get-user确认缺失|4×3=12|
|共享测试app/org|POST /api/delete-application、POST /api/delete-organization，各一次；GET对应app/org各一次验证缺失|4|
|合计|T1=6、T2=9、T3=12、T4=9，共享=4|40|

保留新bootstrap/默认启动对象与整个隔离DB作为封存证据；不把删除测试app/org说成数据库已经物理擦除。用户删除前确认所有method handler已结束；存在在途UNKNOWN时不宣布原生全集关闭。清理后拒绝仅适用于该profile的fresh AT/RT接受，异步效果另需合同。

阶段封顶`30+16+28+40=114`；按本次材料上界1/2/3/2完整展开，预登记happy path最大`24+8+20+40=92`。未用22为容量，不许可新增端点/请求/重跑；失败/超时照样消耗已分配槽。测量只查本轨迹的已知父/子，列表中其他轨迹对象不重复探测；不足三材料时跳过空槽，绝不创建材料填满测量数。HTTP尝试和服务内部SQL/备份I/O分账；构建/版本/工具取得另计资源。

## 6. 失败、UNKNOWN与证据保护

- 达到任一全局/阶段/操作槽或时间/内存界、错误issuer/端口、非合成数据、权限范围越界、hook改变原子性即停止新方法/测量请求；cleanup只使用原40配额及既定端点，不自动增额。
- barrier超时或handler未静止：停止新业务，私有监督器限时等待已发操作；仍不静止时只停止本run自有进程，封存DB/队列/未决权。不能在冻结实例补查，也不能把未知清理强行结案。原始失败、残留及未用预算全部记录。
- 原始HTTP响应、cookie、密码、AT/RT、私钥与DB仅在scorer-private受保护目录，加密封存并分离密钥；method-view只给合同允许的结果。脱敏表用run内映射/指纹保持因果关联，不把真值字段泄露给候选/G。双方同能力/计费，当前没有实现任何候选方法。
- 一致DB证据用授权备份/同一事务快照，记录watermark；WAL存在时不裸拷main文件。停止自有服务后可备份整个新run数据库及旁文件，明确快照时点；不连接原DB。
- 外部分享只准备脱敏投影，未获相应授权时不上传/联系。方法输出UNKNOWN、阴性/阻塞与构建差异保留。单次阴性结果不否定所有调度；barrier构建命中只证对应工件/条件。

## 7. 执行前绑定与裁决

尚需绑定：授权收据、run绝对路径、Go/依赖/源与两个exe摘要、hook/监督器/harness代码审阅哈希、bootstrap/证书/配置清单、端口空闲、实际driver连接观测方案、加密/ACL及cleanup责任人。技术材料已列明权限、命令、文件、端点、次数、相位、停止/残留策略；这些字段未绑定和代码未创建符合当前只做准入准备的范围。

申请材料CONDITIONAL_PASS；执行NOT_AUTHORIZED，原生新请求0。拟议plan固定为T1→T4→T2→T3；串行控制未通过时停止并发轨迹。未来若调整须先修订并重新锁定授权plan，禁止运行中临时换序或重跑。
