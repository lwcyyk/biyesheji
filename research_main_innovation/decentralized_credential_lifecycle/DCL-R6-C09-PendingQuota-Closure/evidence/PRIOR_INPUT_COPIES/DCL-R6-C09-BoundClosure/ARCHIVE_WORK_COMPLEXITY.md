# 处理工作量、压缩、内存和FD边界

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


|步骤|输入规模|最坏读取|最坏写入|工作内存|FD|裁决|
|---|---|---|---|---|---|---|
|C09 current PENDING classification loop|N unbounded in contract, systemctl/raw reads separately unbounded|UNRESOLVED|sum L_i, current N unbounded|Per-row encoding plus uncapped helper PIPE/copy buffers; AS ceiling may terminate, not prove completion|Event datafd1 + lifecycle lock1, plus helper/Root existing descriptors|UNRESOLVED|
|Proposed quota log encode/append/cursor|<=263 main slots, row<=1322; cursor<=956; emergency<=334; failed staging retained separately|<=266 cursor reads plus schema/context inputs not included in this sub-bound|<=345148 +266*956+334=599778|O(1322+956) validated scalar row buffers; serialization object overhead/native helper context separate|Log append1, existing lifecycle lock1; cursor temp/update descriptors sequential; no new persistent process/thread|WORK_BOUND_PROVED_FOR_PROPOSED_LOG_COMPONENT_UNDER_SCHEMA_ONLY|
|Quota complete observation|check_base, counter, ticket/marker, checked_receiver/unit_show, current source/instance proofs|G.trusted caps selected JSON4MiB; G._run PIPE and G.read/digest inputs lack uniform caps|Bounded log subgroup only|UNRESOLVED until all helper response/schema bounds fixed|Bounded source call nesting; baseline/runtime-specific FD count separate|PARTIAL|
|native build|R_raw unbounded, N<=4450 under old scope|One full hash pass R + one compression-read pass R+manifest; ZipFile library may add metadata reads|Z_native +M_native, unresolved until R and format bound fixed|sorted(rglob) O(N), manifest O(N), G.digest Path.read_bytes O(max file); no max raw file proof|One input data file at a time plus archive output and pre-existing/lock/dir FDs|UNRESOLVED|
|terminal independent native verification|Only admitted zip<=32MiB, total uncompressed<=32MiB, manifest<=4MiB, currently members<=257|<=32MiB member streams plus metadata/manifest; duplicate/canonical checks; failed input inspected to fail boundary|Read-only verification; optional separate result excluded from earlier preimage|ZipFile central directory+JSON rows O(N+manifest), chunk64KiB; Python allocation constants not a complete1GiB proof|Inside terminal reader: Root directories8 +boot1 +counter1 +phase-lock1 +ZIP open+dup2 =13 incremental source descriptors, plus baseline; transient operations separately reviewed|CONDITIONAL_PROVED_FOR_ACCEPTED_INPUT|
|post-exit native audit|native manifest and archive, host/native scope/hash bindings|Existing z.read(member) materializes full member; lacks matching full-set and uniform per-member prelimit in that helper|STARTUP_NATIVE_AUDIT outside ROOT|O(largest member +manifest/JSON), presently not bounded for all source outputs|Zip source/active member plus audit temporary query descriptors|PARTIAL|
|admin export/finalizer|R_raw + native manifest + Z_native <=32MiB required for export; host/source sidecars additional|Copy pass +host hash pass +ZIP creation pass +ZIP verify pass; each variable input must be counted|Admin snapshot copy +admin ZIP+fixed metadata|Native export64KiB streaming; host digest/read ZIP may allocate full files; O(N) rows/index|Sequential files plus ZIP output; environment baseline not a new approved NOFILE limit|UNRESOLVED_FOR_TOTAL|
|paired independent archive oracles|Whole manifest/member set, validated path/type/hash/size/binding|Two complete accepted archive streams plus original crosschecks, up to2*B+R under respective caps|Separate immutable verification receipt only|O(N+manifest+chunk), independent rule code shares zipfile/parser TCB in prior review components|Archive+one sequential member stream; actual wrappers/FD limits remain environmental|CONDITIONAL_PROVED|

拟议日志组件在严格schema/额度生效条件下可记**WORK_BOUND_PROVED**：主日志预留345148字节、cursor956、失败334，最多266次cursor写，总写入≤599778字节；包含文件/目录的持久化尝试≤798。它只覆盖日志编码/追加/cursor，不覆盖完整check_base/systemctl响应/stop/seal。当前原生循环的整个工作量仍UNRESOLVED。

现有native构建器hash为整文件read_bytes，ZipFile按N个条目构建索引，sorted(rglob)还需O(N log N)路径排序。独立终态checker使用64KiB块，但ZipFile/JSON对象占用O(N＋manifest)；其他host/native helper会用z.read一次物化成员。AS1GiB是硬拒绝边界，缺少完整对象分配常数/输入字节证明时，不能据此宣称工作内存足够且封存会完成。

ZIP不能假设压缩后更小。对固定ZIP32、空extra/comment、保守16字节descriptor及命名profile（最多6个路径分量、每分量255字节），F≤1535。H≤22＋N(92＋2F)，N=4451得H≤14074084字节。该粗界来自字段/源层级，不作为新容量许可；未来scope和ZIP64/扩展字段须重新审查。

若另证实际pinned默认zlib满足compressBound式D(s)≤s＋(s>>12)＋(s>>14)＋(s>>25)＋13，则U=32MiB下压缩数据和元数据条件上界47696620字节；ZIP_STORED条件界47628516。两者都高于现行压缩包32MiB，展示该双上限缺少“所有合法raw都能被容纳”的保证。此处是保守上界超出接受界，未声称实际输入必定达到该界。

文件描述符与TasksMax分别计量。终态reader路径可列13个增量源描述符（目录/boot/counter/phase/ZIP open+dup），再加进程已有基线；当前没有获批的新NOFILE上限。目录/库/子进程辅助资源仍需结合实际scope审查。

即使获得有限操作/读写量，存储fsync、调度、systemd和终止时延仍缺严格最坏完成时间；保持**WALL_TIME_BOUND_UNRESOLVED**。完整300秒、终态5秒、行政30秒均未通过新的原生实测或严格时延证明。

[ZIP参数/压缩假设](evidence/ZIP_BOUND_ALGEBRA.json) · [工作量全表](evidence/WORK_MEMORY_FD_MODEL.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
