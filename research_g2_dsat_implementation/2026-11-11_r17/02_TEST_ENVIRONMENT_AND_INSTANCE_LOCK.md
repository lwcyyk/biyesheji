# 专用测试环境与实例锁

## 当前选择及证据

已登记选择：全新、隔离、合成数据、真实Authority代码。**环境类型已选择，具体环境尚未锁定。** H2_TEST_ENVIRONMENT_LOCKED=false，H2_TEST_ENVIRONMENT_UNRESOLVED=true。

| 材料 | 可以复用的事实 | 不能承担的确认 |
|---|---|---|
| R16 A1 | 当前挂载代码、会话门、内存SQL和合成输入已验收 | 18个内存连接均为已结束单元夹具，缺持久Authority实例/进程/密钥 |
| H1隔离venv | 路径和R16 CPython3.12.14记录可固定，纯标准库侧已有证据 | 常规cryptography目录未发现；不是已经确认可启动真实服务的环境 |
| M1在线状态验收报告 | 曾运行真实Authority/TLS＋合成Provider，历史环境具cryptography50.0.2并已清理拥有进程 | 属旧版本和旧授权，无法证明当前环境、依赖或实例存在/可复用 |
| 旧L1原生文档 | 曾使用独立Keycloak/Casdoor实验环境 | 私有数据在.runtime，且用途为原生实验；本轮不读取、不复用或作为H2候选实际实例 |
| R16 JSON合成seed | 可作为数据结构参考，含正确的原请求绑定测试输入 | 其codec是spy；不能把JSON或spy blob直接当作真实AES-GCM数据库 |

因此，没有已获本轮授权、当前可确认运行的H2专用实例。新建是选定路线，实际创建尚未发生。

## 当前锁字段

environment_id、owner、deployment_root、Authority服务OS主体、实际Python、DB引用、当前服务/PID/创建时点、端口、实际合成账户/task/grant/rid均UNRESOLVED。H2_TEST_ENVIRONMENT_LOCK逐字段区分VERIFIED_STATIC、REQUIRES_RUNTIME_CHECK和UNRESOLVED。

代码锁采用R16最终六份源码＋storage/protocol/SQL等依赖的磁盘SHA。实际加载版本还需D1部署清单与P1a观察，源码文件当前存在不能证明进程加载同一版本。

历史文档中的base Python路径仅作候选线索，本轮未查询该目录或执行解释器。研究者指定Python后，需单独核cryptography、SQLite特性、源码加载和TLS支持；缺包时停止并另审，D1不自动安装。

## 新实例的最小隔离合同

拟议范围是一个受控Authority进程和一个回环TLS监听端点，使用全新专用根目录、新生成合成state key/TLS key/认证材料。首轮不启动Controller、Provider、AI Agent、Casdoor、Keycloak或连接外站。Controller连接关系登记为“待后续单独接线”，保持管理读取与普通Agent分离。

部署根必须由研究者指定并排他新建，不能位于旧.runtime或任何生产数据目录，不能通过复制旧DB/key/bootstrap配置来替代。ACL仅覆盖新拥有对象；当前负责人/OS主体/具体权限仍待提供，不从用户名猜测。

允许测试账户可以是Authority内部的合成account标签，不要求创建真实网站账户。用户需指定允许的名称范围，或明确批准工具在新实例内生成全部合成名称。新的grant/rid在获批准备阶段才生成，生成记录随后成为P2目标；当前不伪造为已存在对象。

端口需指定或明确批准一种选择策略；绑定失败即停止，禁止扫描其它端点。现有lab的free_port先bind/close再启动存在竞争窗口，不能把提前取得的空闲端口当作持续保留。选择动态端口时还要修正/适配ready metadata：当前serve按config.port写ready，port=0时会记录0而非实际端口。[C01:356–364；C06:71–75]

## 真实实例身份

未来应同时固定：批准environment_id、OS进程主体、PID＋创建时点、每启动新生成的epoch、部署hash、规范DB位置/文件身份、同一打开connection/Store绑定以及监听端点归属。epoch由受信启动器在该进程生成并登记，不能使用RPC正文或复用旧文件字符串。

当前A1只检查issuer.epoch_ref与ticket中的字符串相等；它没有从OS产生/认证真实epoch。进程重启清空命名空间；旧授权文件必须因PID/创建时点/新epoch不符而失效，禁止自动rearm。新epoch的重新审批须由外部管理授权流程提供，不由A1对象自行证明。

数据库持久genesis身份仍缺，authority_instance保持null。本次实例锁只能在声明的可信OS、无未经批准替换/回滚及唯一Store运行边界下识别一次部署，不能据路径、PID或hash单独声称持久实例连续性。

## 待补的最小信息

见H2_TARGET_SELECTION_REQUEST.md：负责人/新根目录/Python/合成数据与端口策略。该表是本轮已发询问的剩余信息清单；“1”已保留，不要求重新选择环境类型。具体值未取得前，D1、P1a、P1b命令均不形成可执行argv。
