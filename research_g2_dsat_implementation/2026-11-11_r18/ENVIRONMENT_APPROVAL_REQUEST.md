# 一次性确认：H2候选参数

新建隔离方案1已确认，只需确认或修改下列整组候选。

| 项目 | 推荐值 |
|---|---|
| 责任分工 | 研究者本人任研究/批准/日志数据保管；Codex仅在单独授权后执行；Authority为本人控制的专用测试进程，实际OS身份/SID在部署前核验 |
| 环境ID/新目录 | h2-authority-synth-001；D:\毕业设计\h2_test_runtime\h2-authority-synth-001（未创建） |
| Python | C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe（3.12.14 AMD64；已有crypto50.0.2元数据） |
| 合成范围 | 新管理身份h2_metadata_reader_001；caller/account/task/audience/generation采用h2_*_001；1 grant别名h2_grant_001＋1 rid=h2_issue_001的QUEUED issue；handle、材料、state/TLS key仅在另批准备阶段新生成 |
| 网络 | 单Authority，127.0.0.1:27443 TLS；不扫描/自动换端口、不外网、不启动Controller/Provider/Agent/Casdoor |

当前各项approved_value为空，可回复“确认推荐五项参数”，或只列修改项。无需发送口令、Token、key、真实用户信息或完整生产配置。

此确认仅锁定候选参数。D1-A代码实施、D1-B创建/密钥/DB/启动、P1a、可选P1b及P2分别另批；本轮没有执行这些操作。
