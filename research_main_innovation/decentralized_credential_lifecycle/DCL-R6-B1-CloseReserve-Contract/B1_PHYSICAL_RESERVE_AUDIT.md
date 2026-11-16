# B1物理空间与持久化审查

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

**PHYSICAL_STORAGE_RESERVED=NOT_OBTAINED。** 当前close相关五模块未找到fallocate/posix_fallocate/ftruncate、statvfs/disk_usage调用；冻结B1材料缺少物理保留provider或凭据。该审查根据当前代码和已取得材料记录结论，Linux活动存储状态未查询。[PHYSICAL_STORAGE_AUDIT.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/PHYSICAL_STORAGE_AUDIT.json)

RootIPC保证private/out的st_dev一致，按目标策略编码后创建新的随机.publish文件，写入、file fsync、rename及目录fsync。BC.Store在boot目录为替换创建.bc随机临时对象，并执行文件/目录barrier。当前代码未为这些新对象建立独立可消费的关闭空间底线。[src/root_ipc.py:71](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/root_ipc.py:71) [src/boot_continuity.py:86](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/boot_continuity.py:86)

物理合同至少需要绑定每个target/staging的真实device/filesystem/目录generation、data extents、inode、目录项/rename、journal/COW metadata，以及old/new版本重叠和允许其他writer的排除规则。空mr_close.lock即便数据字节0也需要inode与目录metadata。内存page_size=4096并未提供磁盘allocation unit。当前这些参数保持null。

\[P_{close}\ge\sum_i\lceil s_i/a\rceil a+P_{inode}+P_{directory}+P_{FSjournal/COW}+P_{temporary}.\]

式中a和各metadata费用必须来自实际受信backend。仅做namespace权限和相同st_dev检查无法得到其他日志不占用关闭底线的结论；fsync或rename还可能在数据写入之后需要metadata空间。外部host路径也需独立绑定故障域与保留责任。

最小反例选择健康介质上的容量分配压力，最后raw和cursor已提交，逻辑close余额仍正，新的STOP/CLOSED staging却返回ENOSPC。它没有违反已配置的应用路径权限，也无需任意新DCL调用。当前无保护底线的组合不能保证必要持久停止记录。[MINIMAL_STORAGE_COUNTEREXAMPLE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/MINIMAL_STORAGE_COUNTEREXAMPLE.json)

标准可选方向为真实预分配/受信存储保留服务及排除普通writer的等价保障。若方案变更RootIPC的同文件系统rename关系、目标policy或helper，需要在后续单独申请准确范围。当前只记录合同义务，没有实际配置、分配或源码变更。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
