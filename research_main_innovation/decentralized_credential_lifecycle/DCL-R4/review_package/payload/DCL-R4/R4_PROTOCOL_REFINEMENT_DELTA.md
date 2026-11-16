# D1-PBFT-SEAL/1.1：R4规范精化增量

2026-11-10，Asia/Shanghai。以冻结的DCL-R3为基线；原21业务转换与八步重配置继续使用。本文件精化部署接口和组合证明，未编写协议/模型检查程序，未部署/实验。I1/I2/I3归档和实现门关闭继续有效。

## 1. 状态就绪与秘密使用就绪

R3的Ready同时提到状态对象和材料可用性，实际分布式部署需分成两个角色证明。

`ReadyState_j=(StopDigest,CfgNewDigest,state_root,rho_root,data_manifest_root,code_schema,j)`。正确新副本仅在取得完整逻辑状态、密文/引用对象、验证规范编码及确定性F后签署；它不取得原生秘密明文。q_new个同body签名构成CertReadyState，支撑NEW_MEMBERSHIP_ACTIVATE。

`ReadyUse_V=(profile,StopDigest,GenesisDigest,mid,target_E2_boot,gate_code,secret_namespace_versions,allowed_scope,preconditions,nonce,validity,V_role_signature)`。V/Gt在自身受保护边界内检查解密/受限使用准备度，返回条件性部署证据，不把分片/密码/AT/RT交给BFT副本。未来执行仍需当前Q批准、预算、当前owner与一次性发送权。

ReadyUse不证明未来永远可用。V故障/权限/对象版本变化后暂停相关资格并重验。缺ReadyUse不阻止新委员会RECOVERING以处理Revoke/Record，但阻止相关native业务Release。ReadyState、ReadyUse和执行资格是三种对象。

原生查询若用于预检，必须已有明确善后/管理授权，逐请求计费；成员加入预检本身不自动允许原生调用。收到ReadyState后要求新BFT副本解密全部密码会改变故障与暴露模型，应拒绝这种部署映射。

## 2. 当前资格与恢复

Cfg成员身份、公钥均规范去重，角色/部署/epoch/消息类型域分隔。沿完整Stop/genesis链验证当前anchor，业务资格采用当前有序授权及新challenge，不使用显示缓存、旧QC或未同步副本的无序本地读。

崩溃恢复同时验证应用状态与PBFT自身view/sequence/投票约束。恢复到Seal之前的旧备份不能重新进入ACTIVE；无法确认当前head时停发。已有SQLite恢复证据仅支持其原单活/缓存恢复范围。

RHO继续携带原i/o/generation、reserved/charged、send_rights、UNKNOWN、Hist、CreatorCaps、native观察水位、cost_envelope和旧claim条件。移交完整应用状态的证明不承担隐藏原生行为全集完整性。

## 3. 成本与进展保持

组合安全定理沿用R3的前向模拟；费用与活性补充以下义务。

- 每个真实native尝试起点必须映射到一个带相同ΔC_N的抽象步骤/环境步骤。预算预留不等于实际HTTP已发生；二者分别记录。不能把反复查询当成零费用stutter。
- 抽象stutter若不改变C_N，只允许不引入新native尝试的内部步骤；通信/CPU/存储时间仍报告自己的费用。
- 进展需每个已选择动作实现段在声明公平/可达/超时条件下最终返回合法观察，或有相应有限内部rank；所有允许的timeout/UNKNOWN须已在Post中。安全模拟本身不排除无限stutter。
- 目标h只限决策段数；墙钟完成期限、UNKNOWN持有时间和无限次重试需要额外界。缺这些前提时仅承诺安全/持久责任。

## 4. B支持与承诺范围

S1允许Seal暂停B、保持其批准/预算/义务并条件恢复。S2继续要求每个规定前缀有当前、真实可用的合法支持，包含Q、Gate、原生材料、网络及费用条件。双Gate同依主Q仍会被同一Seal切断。具体S2配置和不可行证书见R4_TASK_B_CONTINUITY。

允许所有路径/Provider同时失联的故障模型不能保证S2；有限有效期和有限维护预算不能自动支撑无限持续区间。增加独立路径、预算、原生根及可信域均同等给G并完整计费。

## 5. 状态

版本1.1是纸面接口精化，未执行运行中代码/schema升级。各epoch之间仍要求同一已验证代码/schema及确定性迁移；实际安装的状态服务、密钥/存储、V/Gt与原生profile需逐项满足部署条件。

保留CONDITIONAL_PROTOCOL_COMPLETE于纸面实例；真实部署/全部原强目标和REVIEW_READY保持待证。修订采用成熟角色分离、资源标注模拟及可用路径方法，强G覆盖裁决继续。
