# RootIPC与C09真实结果

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

RootIPC56全部获原生独立oracle接受：48 PASS＋8 MUTATION_DETECTED，访问505。UID999读取共享对象、Root私有对象保护、原子发布、停止/等待夹具和8项变异已按冻结范围验证。该套件通过与后续完整生命周期出现的新失败分别保留。

C09H34全部获原生独立oracle接受：28 PASS＋6 MUTATION_DETECTED；含Root原始复核共访问273。

真实C09成功链已取得：当前意图、Receiver4318确认、持久ACK、Launcher4314实际exit23、Root4259直接waitpid raw5888、当前状态fresh-read、HANDOFF_VERIFIED及classification_count=1。ACK/见证/结果的窗口、锁、授权SHA、boot、T0和R=38,729一致，原件摘要吻合。

|实际时间书签（BOOTTIME）|值|
|---|---|
|ACK文件自带时间书签|{"boot_id": "55ac71b2-e2c9-4e7b-9c94-e49d7082d8f4", "boottime": 1406.091102362, "utc_ns": 1794457720454857633}|
|退出见证采样|1406.287321124|
|C09 PASS|1406.344237780，T0+48.592009253秒|
|同父内部恢复|entry已验证；准入在manager检查处失败，resume_count=0|

交接成功收据证明真实C09这一阶段；完整恢复及后续C10资格仍未取得。失败后发现等待态coordinator身份被清空、普通非零退出缺关闭收敛；本轮通过冻结stop_tree/seal补充关闭，原R及T0保持。

独立原始复核的完成范围是READY64/RootIPC56/BC40/C09H34；host仅核对Root结果、原件摘要及账格式，没有在关闭后重跑目标oracle。S34/门18与完整资源门原始复核保持UNRUN。

[真实交接证据](evidence/C09_ACTUAL_HANDOFF.json) · [完成套件原始摘要](evidence/COMPLETED_NATIVE_AUDITS.json) · [失败与收敛缺口](evidence/FIRST_FAILURE_AND_CLOSURE_GAP.json)。

ACK书签在冻结写入调用前采样；持久完成由原生返回控制流和Receiver回复见证，精确fsync返回点未单独打点。
