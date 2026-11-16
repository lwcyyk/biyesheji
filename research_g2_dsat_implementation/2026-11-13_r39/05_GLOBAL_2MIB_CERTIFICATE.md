# 全局整数证书

本轮对R38重新验证存储不变量，没有直接把旧2000167或96985挪作新增内容可用量。

路径A从实际AST提取13个EVIDENCE_CAPS数值，核对新调用图的所有写入仍经原checkpoint/write/io_write；新增逐项记录占用F08原份额。路径B独立读取逐文件整数证书，以PowerShell Int64再次求和。二者结果相同：2000167，预算2097152，存储安全裕量96985。

在fresh只读approval<=8192、其他目标空、受信不可变源码/运行时、独占写入、FileIO extent<=请求长度的条件下，逐项有：

`0<=visible_f<=charged_f<=cap_f`。

每次write前全长扣费，短写/flush/fsync未知仍留全费，failed流不复用。新readonly句柄不增加payload；没有删除/退款/重开、磁盘temp/rename副本。部分目标与failed receipt也计入同13项。

因此所有受控存储前缀和逻辑发布共存峰值<=2000167。cap预留是未来占用上界，visible/confirmed/uncertain是同一已扣分配的不同观察，不能再次加一遍。用户态buffer=0仅指FileIO待刷payload；RAM、内核cache、物理簇与进程最终回收各有独立前提。

这个结论证明P1，与P2完整内容和P3失败准确性独立。完整必需wire需求没有因为文件guard存在而变小；NORMAL/WORST_FAILURE完整总量仍UNKNOWN。原96985仅是条件存储包络裕量，不能当作当前完整需求的实际剩余。

C1清单PROVED；C2正常UNPROVEN；C3异常UNPROVEN；C4已存原子共存峰值CONDITIONAL；C5原完整全局容量UNPROVEN；C6截止准入CONDITIONAL；C7采用已批准表示范围CONDITIONAL。静态执行准入保持BLOCKED，未形成有条件动态运行建议。

G3仍16获批/12限定/9需修改，G4仍7变更/5缺失。原来源锁与R35禁用命令保持，完整容量即使将来取得也不能独自接纳新运行时或启动68项。
