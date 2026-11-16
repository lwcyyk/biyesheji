# R07依赖审定与实际安装

2026-11-10（Asia/Shanghai）。研究者已明确批准固定Wheel下载、隔离安装及S2离线验收。原阶段D稿件/锁/QA逐字节保存在stage_d_frozen；批准与命令另存收据。

| 项目 | 实际结果 |
|---|---|
| 包/版本 | 官方networkx3.7，稳定、未撤回 |
| 仓库 | https://github.com/networkx/networkx |
| 官方元数据 | https://pypi.org/pypi/networkx/3.7/json |
| Wheel | networkx-3.7-py3-none-any.whl，2,142,205bytes |
| SHA-256 | `e3fd2c13a7814cee3746340d8d7f8598a67f16a58bf47fb7f8793fab6efca1b0` |
| Python | `!=3.14.1,>=3.12`，已实际运行CPython3.12.14 |
| 标签/许可 | py3-none-any，BSD-3-Clause |
| 外部依赖 | 未申请extras；39条Requires-Dist均由extra标记约束，核心必需外部依赖0 |

PyPI JSON、PEP658核心元数据和发布provenance交叉核读。核心元数据SHA `ffcf42a343af6ffc54ff9cc4c09cf9638cd73b131370f395abd11b630186c90c` 与官方值/实际Wheel内METADATA一致；发布subject指向同一Wheel哈希，publisher为networkx/networkx的release.yml。许可证与发布commit文本一致，Wheel没有pyd/dll/exe/so成员。服务端发布核验记录与本地文件哈希核验分别登记，本轮未运行本地Sigstore验证器或完整代码漏洞审计。

从已批准唯一官方URL下载一个软件包，先核大小/哈希/元数据/许可再安装。实际环境：`D:/毕业设计/auth-lifecycle/.venv-dsat-r07-networkx-3.7`。使用venv --without-pip及既有pip26.2.2 --python，只从本地Wheel安装；--no-index/--no-deps/--require-hashes/--no-cache-dir等约束见INSTALL_RUNS.json。未向共享环境安装包，也未向venv安装pip或extras。

实际导入路径位于批准环境，核心5份源码与Wheel字节相符，target仅networkx-3.7.dist-info。共享解释器/pip源码哈希与全局仍无NetworkX的状态已核对。申请文本保留原身份，APPROVAL_RECEIPT及DEPENDENCY_LOCK记录当前APPROVED/INSTALLED。

直接PyPI HTML遇Client Challenge，版本事实采用官方JSON/哈希绑定元数据；GitHub release API限流403未重试。官方stable文档当时标题为3.7，正文/时间/哈希已保存；实际安装API签名再次核对。requirements锁保留审批前固定字节，授权由批准收据承担。
