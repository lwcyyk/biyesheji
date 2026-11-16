# 新运行时磁盘与实际加载身份

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**RA-D1=PASS_DYNAMIC，范围为本批已观察检查点。RUNTIME_PROVENANCE_CONDITIONAL继续保留。**

|组件|SHA-256|Build-ID|
|---|---|---|
|ld-linux-x86-64.so.2|5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f|231ab65dd867a89dce29cb958fd5ca50abb1aa34|
|libc.so.6|755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a|8cebda42d140fc2b09639f8b13a5d5f2e617ef09|
|libm.so.6|5dcc4d25466e29ca390ed6fabb371c69b65dff6fa4e91c34561057a020d6994a|f772fc0c42a75e38f138f8b66f1ebc8aad060525|

原生static_A runtime_identity保存Root449的full bytes/build-id/packages/maps结果，三项每个5个映射段均与磁盘inode/device一致。C00启动/探针结果保存Payload实际pid的包和自身映射检查；观察位置、pid/boot、inode/device与scope原字段保留在下方JSON。

GNU libc上游2.39、Ubuntu精确2.39-0ubuntu8.12。libc6/libc-bin状态install ok installed/amd64及已安装目录匹配；Python3.12.3执行文件身份和原锁一致。基础环境和完整原生runtime预检实际通过，旧TR-A失配记录不追溯修改。

full观察中SHA/Build-ID重新读取；服务内full=False路径输出的SHA为已绑定合同值、字节由先行原Guard manifest循环核验，再校自身映射。报告区分这两种verification_scope，未把合同值伪装成重复独立计算。

点位检查不提供path→exec原子性、永久身份或Root特权更新阻断；缺新.deb独立payload再现和信任Root/dpkg/keyring条件保持。

[所有实际运行时回执](evidence/RUNTIME_IDENTITY_RECEIPTS.json) · [实际预检stdout](evidence/windows_entry.stdout.raw) · [绑定合同](evidence/FROZEN_SOURCE_REFERENCE/inputs/runtime_identity_contract.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
