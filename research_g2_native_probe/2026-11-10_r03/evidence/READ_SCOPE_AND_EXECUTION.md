# G2-R03：核读与工具范围

## 连续任务说明

本轮附件已全文核读。G2-R02十稿/静态模型/费用/准入卡以及G1-R01/R02/R03、G2-R01的同对话已读内容复用原范围，不重新声明为盲审。此前的知情状态、论文部分阅读、历史失败与UNKNOWN保留。PRIOR_G2_R02_BINDING来自本任务最初阶段，接续写稿时原样保留。

SOURCE_INDEX列出本轮重点27项短ID。C01—C10、G01—G04/G06—G10按范围读源码；G05主要复用前轮已读发行/JWT段；G11—G12补读继承的UserInfo入口与Bearer检查。后两文件在原218项内，此次没有另做Git blob比较。本轮补查角色继承IsolationLab、checkSigninErrorTimes、password发行链、RecordUserSignin/UpdateUser、两类对账helper、NativeHTTP reservation/发送之间的位置。H01、H02及相关历史报告按已记录范围核读；锁入文件不等同每个文件本轮全文重新阅读。

evidence/SOURCE_EXCERPTS.md是所选范围的逐行摘录；包含少量相邻源码作为上下文，不扩张为完整依赖审计。全部原文仍在源路径。

## 只读身份取证

当前重点10份Go文件通过本地git show与指定提交比较：原字节受换行影响，LF统一后10/10相符。264项输入固定，继承218项全部匹配。源到运行二进制可复现对应仍UNPROVED。

工具用途：PowerShell/rg文件与符号定位；Python标准库Path、json、hashlib、ast等仅取证、文本/JSON生成与文档质量核查；本地git show只读blob。没有import或执行auth_lifecycle/research_v12，没有运行旧README中的复现命令。

少量路径定位曾失败：isolation_lab.py、controller.py、reconciliation_lab.py、native_unidentified.py、controllers/userinfo.go、object/user_signin.go、object/user_update.go。随后通过rg找到真实文件/符号；不存在路径未作为证据。GenerateId的初次定位未形成UUID版本依据，本轮只保留G1的freshness/非碰撞前提，不声称核得UUIDv4。

## 执行零项

新机制实现、参考实现、求解器、状态枚举/数学穷尽、项目模块执行、测试重跑、真实原生HTTP/账号变更、真实秘密读取导出、外部消息与新代理均0。文档处理脚本只写本轮研究资料，没有生成或执行候选机制。

手工反例/费用是纸面证据。没有将它们登记为实测、外部验证或程序穷尽结论。

## 本轮文字修订

1. 首次成稿明确补入Issue共享账户写、失败计数/冻结及可能密码格式升级，限制F0的非干扰/支配范围。
2. 区分基础lab与M6继承角色；明确两者user均无call，管理委托和专用可信管理进程分开。
3. 未知Issue、双未知、第三grant保留现有helper缺口，不以原生GET存在代替完整接线。
4. 费用增加前台/内部RPC和审批交互，7/10/5/8均为条件策略上界；Controller已ready前提显式补入。
5. 全平台支配与CPU/延迟必要下界保持待证，关闭范围限定为固定profile旧来源诊断候选。

上述均为本轮后继文档的精化，历史稿原字节未改；没有修改T3或旧数学证明。
