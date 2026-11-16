# 读取、取证工具与执行范围

本轮用户附件全文已读。R01九份主报告在当前对话已完整编写/核读；本轮复用前核对其既有QA登记的33项输出，全部一致，QA文件另锚定。R01原输入/证据限制沿用；没有把先前部分核读资料改记为全文。

Refresh相关Python正文、固定Go路由/handler/RefreshToken/Token/JWT、失效/内省/UserInfo过滤及所列helper按SOURCE_LOCK实际范围核读。PythonAST和Go符号正则只用于位置索引，符号被列出不表示对应文件所有函数已完成语义证明。其他生命周期、论文与原生批次以R01的已读范围复用。

## 新增取证

- Git HEAD只读定位为528a0213f01caf70b9f41009cbf7b2f67bdd67ec。11份实际核读Go文件与该commit对象比较，规范化CRLF后全部相同；原字节SHA单列。
- M3/M4/M6各三份Go核心归档与当前源、MODEL声明SHA均匹配，共9项。各批Python适配器不同版本保留，未用当前代码回填历史。
- sparse工作树没有util目录；从同一现存本地Git对象读取util/time.go，保存为txt证据，IsTokenExpired位于原blob第61行。没有checkout、补丁、网络或新增Go源码实现。
- 历史PYTHON_TRANSPORT_SOURCE保存了urllib.do_open与HTTPConnection.request片段；本轮核读其单次调用/异常语义。它不绑定实际依赖全部模块；A05/A06的运行部署责任显式保留。

## 辅助工具用途

PowerShell/rg用于文件定位/文本/符号读取；Python仅用pathlib/json/hashlib/ast/subprocess等做文本、哈希、Git对象取证和文档QA；apply_patch只写本轮报告与证据。没有导入/执行auth_lifecycle或research_v12。

新增候选/参考实现、求解器、数学穷尽、测试重跑、原生HTTP、账号操作、真实数据修改、外发、新代理均0。标准工具读取源码或Git对象不属于运行该源码。没有解密或读取实际秘密与评分响应。

## 工具异常与阅读限制

首次若干定位采用了不存在的.runtime、顶层MODEL.json、a/_plant.py、controllers/user_oauth.go、routers/authn_filter.go及稀疏util路径。均为只读定位失败；随后使用rg清单/实际路径，MODEL位于历史batch，plant为plant.py/_plant_reference.py，UserInfo为account.go/AutoSigninFilter，util来自本地Git对象。长输出部分截断，关键Refresh与后继/依赖函数均用定点窗口补读。

一次报告补丁使用AddFile无效标题，apply_patch校验拒绝且未写入任何文件；修正标题后成功。错误限文档写入，不影响历史源或证明输入。

结构性哈希检查只固定字节；人工语义审查与条件性证明按正文范围解释。当前研究属于知情模型辅助；外部系统/数学读者未新增。COL2026主动检索暂停，FS23延期，VPass废弃。
