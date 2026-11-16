# R07阶段D：依赖来源审定

2026-11-10（Asia/Shanghai）。当前仅完成公开元数据、许可证、接口和本地工具链审查。Wheel下载、安装与执行待研究者批准；工程源码及R06结果保持。

## 唯一提请候选

| 项目 | 核读结果 |
|---|---|
| 包/版本 | networkx 3.7，PyPI标记稳定，未撤回 |
| 官方仓库 | https://github.com/networkx/networkx |
| 官方记录 | https://pypi.org/project/networkx/3.7/ 及对应JSON API |
| 文件 | networkx-3.7-py3-none-any.whl |
| 大小 | 2,142,205 bytes |
| SHA-256（官方预期值） | `e3fd2c13a7814cee3746340d8d7f8598a67f16a58bf47fb7f8793fab6efca1b0` |
| 发布时间 | 2026-09-21 16:45:14 UTC |
| Python约束 | `!=3.14.1,>=3.12`；CPython3.12.14满足 |
| Wheel标签 | py3-none-any；无平台ABI绑定 |
| 许可证 | BSD-3-Clause |
| 必需外部依赖 | 未申请extras时为0；39条Requires-Dist均由extra标记约束 |

基础包已覆盖整数网络单纯形、最大流/最小割和Bellman–Ford，本轮不申请numpy/scipy/pytest等extras。原pyproject维持原样。

## 来源交叉核对

实际取得PyPI3.7 JSON、PEP658核心元数据和PyPI公开发布provenance；均只取文本/JSON。核心元数据SHA为`ffcf42a343af6ffc54ff9cc4c09cf9638cd73b131370f395abd11b630186c90c`，与PyPI公布值匹配，Name/Version/Python/依赖字段一致。

发布provenance的publisher为GitHub仓库networkx/networkx、release.yml、release环境；statement的Wheel subject及SHA与上述值一致。记录来自PyPI的发布者核验服务，本轮未执行本地Sigstore密码验证器。对应发布commit的BSD许可证文本已取得，版权/许可条件需在分发时保留。

**远端元数据已核对，本地Wheel字节尚未取得和校验。** 获准下载后必须先核大小/SHA，再检查Wheel内METADATA、许可证、文件清单和导入位置，之后才允许安装/依赖执行。PyPI的vulnerabilities字段当前为空，该字段不承担完整代码安全审计。

## 正常入口限制

直接读取PyPI release HTML得到Client Challenge，本页保留作获取记录、不用作发布正文依据；版本事实采用官方JSON及其哈希绑定的核心元数据。GitHub release API返回匿名限流403，没有重试或索取凭据。官方API文档当前标题均为NetworkX3.7，stable链接可能将来移动，已保存实际正文哈希和获取时间。

## 本地与安装提案

R06的流库仍缺；本轮没有取得NetworkX本地Wheel。现有CPython3.12.14有标准venv和pip26.2.2元数据，目标环境尚不存在。

提议环境：`D:/毕业设计/auth-lifecycle/.venv-dsat-r07-networkx-3.7`。采用`venv --without-pip`，再由既有pip的`--python`选项仅管理目标环境，避免安装/更新共享运行时及额外pip包。现有pip官方说明自22.3支持管理未安装pip的venv；当前pip的本地选项源码也有该参数。

安装关闭在线索引、依赖解析、版本联网检查及缓存，固定本地Wheel、完整哈希和单一版本。命令/位置/边界见APPROVAL_REQUEST.md和DEPENDENCY_LOCK.json。审批前全部PENDING。
