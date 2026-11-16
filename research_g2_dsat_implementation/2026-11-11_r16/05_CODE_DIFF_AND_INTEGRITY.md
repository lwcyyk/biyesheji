# 获准差异与历史保护

研究者R16附件独立批准七目标离线实施。APPROVAL_RECEIPT固定原请求路径/SHA、命令、内存SQLite范围和P1/P2/B2/S5关闭状态。

## 两项受控修改

| 文件 | 修改前SHA-256 | 最终SHA-256 |
|---|---|---|
| services.py | d8ea05120fc8559a95050e4c71a094eefb73e29d22e1de66494d8c8e1975993a | 7cc2321e2623c06848e13d106680887a01bd5635bf417127942a5bac1647be41 |
| dsat_authority_read_host.py | c19d81ff9cb69508a3c1a818366645d4ab5cb9a3616fdc58f096d04f55e1ea11 | 8edcbb1aef62482a6bb3e1f7f993e33824bd6b060b7ddef479567645fdcdb9ad |

修改前完整字节保存在sources/original/*.txt，与旧hash一致。services只修改serve的可选挂载、新读取路由及该路由的日志故障处理；Controller/FakeProvider/SingleActive和旧非读取分派保持原逻辑。H1 host只增加注册来源接口、会话claim/rid/计量及finally清理，默认合成行为通过原24项验证。

另有4个新Python文件与新夹具子树的3份JSON。源码、输入和执行hash逐件在CODE_DIFF/SOURCE_LOCK中登记。sources/CODE.diff提供两项整文件统一替换diff及四项完整新增代码；原字节与当前源码均可独立比对。合成秘密输入只列hash，公开diff不展开canary值。

## 保护结果的准确口径

实施前1320次比较全部匹配。实施后1311项引用仍等于历史hash；9项引用指向两个获准修改的当前源码路径，按明确的新旧版本映射处理，并验证旧字节快照。

这9项不被记成“当前文件仍等于旧版本”。新runner验证所有其它路径原字节，并在每run前后冻结6份执行源码hash。原R13/R14/R15的SOURCE_LOCK、批准、测试/运行日志及本轮修改前快照都保持原字节。

storage.py、protocol.py、R12、R07 S1/S2、R10 S3-A、原H1测试/runner/夹具、migration及其余指定研究记录没有获准变更，均在剩余保护范围内。无全仓回归、旧115/46/33或原生测试；本轮只执行20新项与24必要回归。

## 失效与修复责任

新模块的首次Registration-local gate未覆盖重建issuer/来源显示别名。A09反例实际发生第二次内存SELECT；修复加入进程级来源命名空间，源/客户端/旧H1数学语义没有因此升级。其后三个完整44项批次通过，末轮记录计量与CLI边界。

run_005还补充结束观测失败的保护：读取total_changes失败时保持unknown，数据不出域，费用和槽保留，inflight正常释放。该路径经A14实际验证；未把它记为旧版本已执行的失败证据。修订定位见sources/REPAIR_LOG.json。

本轮不改T3等数学结果、A/B/AB创新资格或缺失文献状态。成熟同步、字段净化、SQL和接线按工程建设管理。全部新版文件、失败轮次、静态定位和最终交付QA均可审查。
