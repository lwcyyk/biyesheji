# Casdoor源码—构建—本地发行物—历史运行证据链

2026-11-10。仅做文件/元数据静态读取。使用系统Go工具的version -m读取目标文件，未启动casdoor.exe；未构建、运行测试、连接native DB或发新原生请求。

## 1. 新确认的链条

|层|实际证据|能支持的结论|
|---|---|---|
|固定源码|HEAD=528a0213f01caf70b9f41009cbf7b2f67bdd67ec；继承26源副本及额外9文件锁|审计引用版本固定；源码工作树与运行镜像对应继续单列|
|源码工具链|go.mod声明go1.26.0、toolchain go1.26.10；固定commit官方build.yml也指定1.26.10|编译器声明与二进制元数据相符；本机元数据读取器为Go1.20，它未用于重构建|
|发行构建配方|.goreleaser.yaml：CGO_ENABLED=0、windows/amd64、-s -w及util.BuildType=release；before hook含go mod tidy；官方CI取frontend产物再Run GoReleaser|配方与所见flags一致；配方本身不证明具体运行日志/生成文件内容|
|二进制|SHA256=ddbab07cbe0a913e3bf3b3fbb09b0a1fa3b4abc5127c6b3156930aa77a37ad5c|现存文件与M6旧哈希一致|
|本地ZIP|SHA256=24457f4383e33639d851514ddbb49fcaac85fca630f4736901c14d13a1114b32；235项；内部casdoor.exe同哈希，大小129363968|现存exe与本地保存ZIP字节一致。GitHub API本轮403限流，官方asset digest独立核验仍缺|
|历史执行|M2/M3/M4/M6记录的版本、二进制摘要、配置/调用/接受结果|支持已记录轨迹及profile，未在本轮重跑或重新认证当前进程|

元数据全文保存在evidence/CASDOOR_GO_BUILDINFO.txt（依赖名称/版本与构建参数），ZIP流式哈希在BINARY_ARCHIVE_PROVENANCE.json。固定工作流引用：[build.yml](https://raw.githubusercontent.com/casdoor/casdoor/528a0213f01caf70b9f41009cbf7b2f67bdd67ec/.github/workflows/build.yml)。

## 2. dirty标记与证明边界

二进制声明：Go1.26.10、vcs.revision等于固定commit、vcs.time=2026-10-29T17:14:49Z、vcs.modified=true；主模块标记v1.1000.1-0.20261029171449-528a0213f01c+dirty。产品发行版本与Go主模块版本各自记录。

modified=true表示构建时工作树有修改，差异内容尚未取得。可能涉及生成物、模块整理或其他文件；当前证据无法判定哪些被编译文件改变。固定提交/依赖/flags和ZIP一致性均提供交叉支持，可复现构建对应仍为UNPROVED。嵌入元数据也不充任密码学源代码认证。

因此U=1、NC1/NC2等是固定源码的语义；把它们用于该实际二进制的全称保证仍需忠实部署/构建前提。历史CLOSED继续附原source-faithful profile，有限已观察效果不升级为每次调用的普遍上界。

## 3. 依赖、DB与隔离

二进制声明XORM v1.1.6、Beego v2.3.8、golang-jwt/jwt/v5 v5.3.0、modernc.org/sqlite v1.18.2、modernc.org/libc v1.18.0；关键依赖与固定go.mod相符。完整MVS模块列表已保存，未下载/升级依赖。

读取现存casdoor-l1.db头100字节：SQLite format 3，读写格式字节均1，最后写入者版本号3039003（3.39.3）。它只描述main-file头的最后写入者指示；并发/WAL/其他写入者可影响解释，活跃引擎版本与具体PRAGMA未获新认证。历史环境中的SQLite3.53.1属于Python/AuthorityStore环境，不能直接赋给Go Casdoor。

SQLite官方规则与XORM固定版本支持源码级逐语句事务分析；当前原生AS的实效隔离、连接/代理条件仍需完整运行配置/未来实验。AuthorityStore的WAL与BEGIN IMMEDIATE也不能代替native AS的事务设置。

## 4. 后续最小对应核验（未执行）

优先取得官方asset checksum/构建日志、dirty差异和生成物清单。若只能重构建：在新隔离目录锁定commit、Go1.26.10、完整go.sum/MVS、工具和环境、frontend/配置/ldflags，记录before/after tidy及所有生成差异；分别保存干净源构建与已还原发行配方构建的哈希。不得为追平哈希隐去差异。

这些构建/版本查询/运行均在后续明确授权及适用门槛满足后实施；本轮只形成计划。当前证据链状态为版本/本地工件一致性增强、源二进制语义对应未闭合。
