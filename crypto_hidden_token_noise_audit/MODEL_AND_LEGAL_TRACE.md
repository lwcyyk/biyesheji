# 隐藏有效随机性后的解密残差均值攻击：模型与合法轨迹

2026-11-07。身份：**INFORMED_DERIVATION_AND_SOURCE_AUDIT**。本会话继承此前推导、审阅结论和本轮工作摘要，并参与本轮命题整理；本轮独立审阅次数为0。历史ROUND-007的独立／知情范围按其原记录保留。本轮数学结论待下一次独立复核。

固定输入清单为 [input_record.json](sources/input_record.json)，SHA-256：737ccb554ebf36737b4a1eff02b9fec1289bf735a71eaf5cc81ef25346f197c9。原文版本、阅读范围和先例见 [来源记录](sources/SOURCE_AND_READING_RECORD.json)。历史目录仅读。

## 1. 具名对象

冻结 **MATRIX-SELECT-OUT-CF2**：FI-v4 §5.1／§6的矩阵算法，配项目SELECT-CONSOLIDATED-2 §3的查询、登记和最终闭包规则，只取普通响应的密文输出。完整普通带版本中，攻击忽略这些带。这是具名算法与游戏规则的组合；SELECT原文件§2的GP群算法和其安全定理各有自身对象。

另冻结 **MATRIX-SELECT-PRP-INPUT-CF2**：矩阵更新先将独立均匀原始输入池ρ映成固定秘密置换的有效池ω，再运行同一CDF采样器。普通接口可给ρ，隐藏ω、r和σ。输出／未来钥匙投影精确耦合，证明见参数账本。

安全目标为fresh/update不可区分性。M₀、M₁在第一行指定消息位上不同。攻击学习目标边界解密作用，隐藏的完整token、源秘密和挑战随机输入均无需恢复。

| 对象 | 本轮结论 |
|---|---|
| FI-v4矩阵算法＋MATRIX-SELECT实际可见C | 合法输出攻击，CF2上有无困难性假设的常数gap |
| FI-v4原rand-ind-eu-cpa游戏 | 此轨迹触发公平评分；此前其它原游戏攻击有独立作用域 |
| CANS2024／IEICE2026接口 | 同父重复、未来完整Key和实际可见C轨迹成立；RISE算法作为群正面对照 |
| 冻结GP23/CTX1 SELECT及其包装 | 所需小整数矩阵残差表示缺失，保留此前安全与成熟组合覆盖裁决 |
| Nishimaki RtR | 档案文本提示近邻矩阵结构；完整原图、参数、游戏映射仍待核准 |

## 2. 维度、字段和原算法

环R=Z/qZ，q=2^D，g=nD，d=n̄；CF2取m̄=n̄=8。密文C=(C₁,C₂)形状m̄×n、m̄×d。第一行记u、c，H=Ordₙ(u)。

| 字段 | 形状 |
|---|---|
| A | n×n |
| Sₑ、Eₑ、Bₑ=ASₑ+Eₑ | n×d |
| u、c、H | 1×n、1×d、1×g |
| U₁、F₁、G₁ | g×n、g×n、g×d |
| U₂、F₂、G₂ | n×n、n×n、n×d |
| token₃=(K_P,K_Q,N_P,N_Q) | g×n、g×d、n×n、n×d |
| r，AΔ，BΔ | 1×n，g×d，n×d |

原文Ord定义用n̄作列数占位，Upd实际输入C₁有n列。这里按输入列数参数化Ord，保留位平面顺序及Tensor_D(S)=[S;2S;…;2^(D−1)S]，使Ordₙ(u)Tensor_D(S)=uS modq。这是Remark6.1要求的类型／记号规范化，采样和算法输出保持原式。

同一边界3生成并复用固定token：

\[
K_P=U_1A+F_1,\quad K_Q=U_1B_3+G_1-\mathrm{Tensor}_D(S_2),
\]
\[
N_P=U_2A+F_2,\quad N_Q=U_2B_3+G_2.
\]

更新逐行输出

\[
u'=HK_P+rN_P,\qquad c'=c+HK_Q+rN_Q.
\]

完整Key₃给(S₃,B₃)，实际秘密S₃可读。全部输出为原始环坐标，原文算法无有损压缩。定义AΔ=K_Q−K_PS₃、BΔ=N_Q−N_PS₃。

## 3. 完整固定攻击轨迹

Q、R和消息在查询前固定；epoch从1开始。FI原文从0开始的编号平移与Next登记差异分别处理。

| 顺序 | 操作 | 用途／登记 |
|---:|---|---|
| 1 | Enc₁(M₁)，保存父p₁ | 诚实普通登记 |
| 2 | Next₂ | 产生K₂、token₂ |
| 3 | Q次Enc₂(M₀)，保存p₂,₁,…,p₂,Q | 固定数量独立训练父，无数值筛选 |
| 4 | Challenge₂(M₀,p₁) | b=0返回Enc₂(M₀)，b=1返回Upd₂(p₁)；保存代次2的C*，C={2} |
| 5 | Next₃ | 私有更新官方缓存；跳过GetChallenge₃ |
| 6 | CorruptKey(3) | 完整获得S₃、B₃；K={3} |
| 7 | 每个p₂,j作R次Upd₃(p₂,j) | 每次提交同一epoch2父id，独立新币；追加子记录，父记录保留 |
| 8 | 本地均值、模生成学习、分类保存的C* | 无额外oracle |

训练父均满足前代普通记录检查。挑战谱系没有重新登记。保存的C*在Next以后仍可使用。先Key₃再训练可流式计算残差，权限与时间条件均成立。

SELECT闭包为：j∈K*且j∈T*推出j−1∈K*；相邻两Key推出token；j−1∈C*且j∈T*推出j∈C*。最终

\[
K^*=\{3\},\quad T^*=\varnothing,\quad C^*=\{2\},
\quad K^*\cap C^*=\varnothing.
\]

无token或相邻Key启动新增传播。部分作用的本地学习按冻结SELECT §3保留为攻击能力，闭包没有“计算成功即非法”的追加规则。一条固定合法骨架足以形成自适应安全反例。

## 4. 原文游戏逐项限定

**FI-v4原图p.10，O.Next第4—7行：** 挑战后的Next还执行C←C∪{e}。故Challenge₂→Next₃后3∈C，Key₃触发交集，按p.11终局返回独立公平位。本轨迹在原实验的gap为0。将C改为实际返回版本会改变这行程序，应另立MATRIX-SELECT对象。

**CANS2024印刷p.53 Fig.1、p.54闭包、p.55 Fig.2／Def.3.1：** Next只增加内部挑战登记；直接C由Challenge／读取挑战版本增加。普通Upd保留父并追加子；Key／token返回完整对象；普通接口返回随机输入。T为空时，其双向闭包同样保持K*={3}、C*={2}。原图已核读。

**IEICE2026印刷pp.235–237 Figs.1–2／§3：** 保留上述接口及实际可见C。RISE及其Theorem1见pp.237–238。接口轨迹核准与将FI算法放入该接口的安全判定分别登记。

**GP23印刷pp.419–420／Fig.5：** 新加密pad及新钥匙坐标参与更新。冻结CTX1是其群实例的明确规格。中心化群编码不会产生本轮AΔ、BΔ和小整数零均值残差。

## 5. 实际读取与失败

攻击读取q、D、普通父的u/c、返回u′/c′、父id和Key₃中的S₃。忽略普通Enc/Upd带、ρ、ω、r、σ、token、B₃及内部缓存。Enc Q+1、Upd QR、Next 2、Challenge 1、Key 1；Token、GetChallenge、Dec、挑战带请求均为0。总调用Q(R+1)+5。

理想CF2的χ₆₄₀为固定16-bit CDF采样，无拒绝／耗尽／⊥。有限采样变体遵循其原子提交及C0/FAIR终局，首个FAIL后停止，攻击者无法覆盖终局。均值错误通常不可见，按两个实验分别计费。

本轮协议实现、攻击原型、大参数密码实验、作者联系、邮件和原生AS/RP请求均为0；有限标量核算只登记为有限数学证据。
