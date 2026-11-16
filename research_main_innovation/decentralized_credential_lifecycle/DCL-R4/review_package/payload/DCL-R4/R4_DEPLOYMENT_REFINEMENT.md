# DCL-R4：PBFT与原生执行的部署精化

日期：2026-11-10。规范基线为[D1八步协议](../D1/BFT_RECONFIGURATION_PROTOCOL.md)、[R3证明依赖](../D1/PROOF_OBLIGATIONS_R3.md)及[R4的1.1增量](R4_PROTOCOL_REFINEMENT_DELTA.md)。本轮形成部署蓝图和逐边证明责任；实际PBFT安装数量为0。Gate R4-B = PARTIAL。

## 1. 三种部署与实际所在位置

|维度|Profile A：同机多进程|Profile B：多机同管理域|Profile C：独立管理域|
|---|---|---|---|
|Q节点|每epoch四进程可测f=1协议流程|每epoch四主机可研究主机故障|每epoch四个独立控制域，按实际控制能力约束f≤1；新旧可无交集|
|共同失陷|OS/root/调试器可取全部钥与状态|云根、AD、KMS、镜像发布权可同时控制多机|管理帐号、KMS、恢复帐号、CI更新权限、备份解密权逐项隔离并审计|
|可信组件|单管理员及OS、Q实现、Controller/V/Gate、P|共同管理员及供应链、Q实现、V/Gate、P|正确Q的软件/稳定存储、用户批准根、V/Gate保护边界、P；失陷Q仍受f界限制|
|密钥位置|本机隔离目录仅有功能意义|各主机钥；共管KMS须计相关域|各域独立节点钥，域分隔；旧钥残留按证书生命周期故障界累计|
|节点认证|固定Cfg公钥白名单|同左，TLS身份与签名身份逐项绑定|同左，加独立治理、禁止同一公钥重复计票，更新经当前治理/RSM|
|当前状态|当前有序challenge；本地缓存只供显示|同左；分区节点拒绝凭缓存放行|同左；可信近期anchor、完整Stop链与最高head持久pin|
|网络|同机调度/环回仍可能丢响应|主机隔离、乱序、分区进入模型|跨域认证、重放防护；安全允许分区；进展另需足够quorum及时可达|
|持久存储|共同磁盘回滚会击穿多进程证明前提|独立盘抗单主机故障；共管备份仍有关联|各域保存共识view/seq/投票约束和应用状态，恢复验证可信head；共管回滚权应归入故障集合|
|材料|当前单机整包AES-GCM及Controller持钥|移植整包会增加各主机明文持有者|Q只复制元数据/密文引用；V/Gate受限使用，E仅句柄；保密性需要独立接口证据|
|恢复|验证本机状态；失去权威状态则停发|可信日志/检查点恢复；保留UNKNOWN|校验共识状态、Seal/child、对象、RHO及近期锚；ReadyState与ReadyUse分别验收|
|适用结论|功能测试、既有单机profile|特定主机故障的恢复研究|满足全部条件后才可检验跨管理域目标|

现状落在A的单AuthorityStore/Controller子域；尚无四副本PBFT。现有M6轨迹仅支持其受信创建者、范围和有限调用合同。B/C属于待验证设计。共同管理员可控制超过f个投票身份时，按进程数声明拜占庭容错会错误缩小攻击模型。

## 2. 抽象—源码—部署映射

状态链：`D1逻辑状态 → Q确定性复制/持久提交 → 当前Gate发送权 → Casdoor微步骤 → 有来源证据 → Q Record/Close`。状态、密文及原生事实的完整性分别验收。

|抽象环节|现有具体对象/接口|需要的精化关系|当前证据/状态|
|---|---|---|---|
|批准、预算、attempt/UNKNOWN|单机AuthorityStore与Controller持久状态|Release同提交登记责任；全局opid跨epoch去重|原单机历史证据；分布式提交和全局去重待实现，PARTIAL|
|Q当前资格|目前单活权威、OS controller.lock|每epoch完整PBFT；新challenge绑定caller/body/anchor；Seal后无新Release|纸面闭合；OS锁的证明范围限本机，部署PROOF_GAP|
|Release到发送|Controller/native_provider发送流程；未来可信Gate|先持久消费发送权，再启动IO；崩溃于任意点保留可能已发；相同创建UNKNOWN保持原责任|受信Gate、防回滚和全部出口仍CONDITIONAL|
|网络晚到|请求可在Release后、Seal/Revoke后才到P|已放行请求始终在RHO；NativeCreationCut计入其最大潜在创建|NC1/NC2静态相位与EnvClosure已覆盖；新运行0|
|Seal与退休|当前工程尚无分布式Seal|Seal固定唯一child、阻止旧Q新授权；退休不抹去旧状态/钥/原生能力|纸面引理成立；native handler继续执行|
|状态/对象接续|当前整包密文存储；拟议manifest与state_root|Q验完整逻辑对象/密文引用；V核秘密版本及受限使用；缺对象拒ReadyState，缺使用能力阻相关Release|Ready拆分补齐纸面角色，实际元数据/V分离边缺失|
|父读取到子插入|Casdoor固定commit的refresh、AddToken及XORM调用|handler缓存、Insert、父Delete、ACK分别建模；并发调度和每次尝试费用保持|固定源码SOURCE_FEASIBLE；dirty二进制对应待证|
|撤销与材料接受|revoke、GetToken、UserInfo等|row/cohort/子行/session/历史密码及接受端各有footprint；fresh读拒绝与已缓存接受分别处理|静态合同＋历史有限验收；任意RP/效果边界待证|
|其他创建入口|GetAccount→GetAccessTokenByUser→GetTokenByUserWithAuth→AddToken|空session-token且前置身份满足时的条件创建纳入CreatorCaps；UserInfo单列只读|R3入口审计；当前部署过滤/凭据来源待核|
|证据与关闭|点读、枚举、内省、异步审计|证据绑定原r/a/o、范围、因果水位、完整性/稳定性；证据缺失保持UNKNOWN|审计异步落盘不能独自充任原子全集来源；C_effect继续条件化|
|恢复与连续重配|历史单活缓存恢复；拟议PBFT日志|共识投票/应用Seal同步恢复；唯一已激活child发起下一次重配|反例CE1明确防回滚义务；实际恢复证明待做|

## 3. 受控发送间隙与A截止点

Release的线性化点定义C_local：该点后的新资格遵循当前撤销状态。已经提交并可能发送的旧权利能在Seal后形成原生事件，因此其责任、费用和CreatorCaps进入EnvClosure。P接收/检查/缓存/插入与Q提交各有事件顺序。C_native另取可证的原生创建/接受截止点，C_effect进一步检查已接受载体。

Gate崩溃于“已消费、未发送”会损失可用机会；崩溃于“已发送、未记录”会留下UNKNOWN。选择安全地保留这两种可能性。对缺原生幂等/终态合同的创建请求，恢复不重发。任何跨Gate切换都共享原intent的责任登记；复制一份凭据或启用备用Gate本身无法证明重试安全。

## 4. 真实攻击面及恢复验收

1. Q管理员失陷须计入真实FD；控制镜像或KMS的同一管理员能影响多身份。C中还需核谁能恢复备份、替换可执行文件和签发新节点身份。
2. 旧节点私钥/旧备份持续存在，要求证书生命周期累计失陷≤f、可信近期anchor；目前尚无前向安全/主动刷新部署。恶意恢复回旧ACTIVE的节点应算失陷，正确节点采用防回滚恢复。
3. V/Gate可见完整秘密或其可复用子材料时，需列入可信托管边界。普通软件Q共识无法额外给V管理员保密性。HSM/TEE/MPC名称须附操作、输出、回滚、更新和认证合同。
4. E1历史bearer、password RT、密码、Cookie及直连P均进入旁路图。仅更换owner/Q成员无法改变P验收。防火墙收口依赖可验证出口边界，公共P加历史bearer应继续保留旁路。
5. 恢复先验证应用/共识日志、根/完整对象、旧UNKNOWN、预算、Hist、发送权及可信head。无法获得证据时停发相关权限；合法Revoke/Record可在新RECOVERING执行。V尚未ReadyUse时继续处理这些元数据事务。

## 5. 源与运行证据的剩余边

[来源链](R4_SOURCE_BINARY_PROVENANCE.md)确认固定commit、依赖/工具链声明、现存exe与本地ZIP字节一致。`vcs.modified=true`使精确编译输入持续待证；dirty内容不能凭猜测归因。静态DB头指向最后写入者3.39.3，当前引擎/连接/PRAGMA、隔离、代理或whole-handler锁仍待运行配置证据。

部署验收须分别提供：Q稳定日志与恢复、节点/管理员控制矩阵、V/Gate接口及秘密流、Casdoor构建/实效配置、所有出口、观察/费用映射和B持续路径。当前映射足供审查；满足这些边之后才可提升真实部署保证。
