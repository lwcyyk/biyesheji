# batch04资格门负向结果

Material Passport：17项负向检查实际执行0、实际检出0；状态UNRUN_RESOURCE_GATE。

C09在C阶段关闭，root原始S重算、正向控制与17项负向投影均未到达。GATE_NEGATIVE_AUDIT和RESOURCE_QUALIFICATION没有生成，RESOURCE_GATE_PASS=NOT_OBTAINED。

|冻结责任|实际结果|
|---|---|
|UNRUN / FAIL / INCONCLUSIVE等7项状态拒绝|UNRUN_RESOURCE_GATE|
|缺job / 缺原始集合 / raw hash不符|UNRUN_RESOURCE_GATE|
|boot / 源码 / 输入 / 执行锁 / T0五项绑定|UNRUN_RESOURCE_GATE|
|checker hash不符|UNRUN_RESOURCE_GATE|
|伪造PASS且去掉原件|UNRUN_RESOURCE_GATE|

C09后恢复准入因真实CLOSED而拒绝，属于本次运维恢复检查；它没有被计入上述冻结17项负向测试。没有人为写PASS或root资格标志。后续需要先修复监督器竞态并取得新版本许可，随后重新执行整个必要集合。
