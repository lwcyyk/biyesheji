> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../frozen/crypto_fi_640_joint_correctness/CONDITIONAL_STRUCTURE.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# 640一次更新：共同环境、条件列独立与真实系数分布

2026-11-10，Asia/Shanghai。身份：`INFORMED_JOINT_PROBABILITY_DERIVATION`，知情联合概率推导。上一轮单坐标证明的独立审阅状态仍为pending；本轮没有新增独立、人工、跨模型或证明助手审阅。

## 1. 输入、对象与模型

四份指定640审计文件及其交付清单已读取/核验。交付清单29项原文件及清单自身共30条输入指纹在[evidence/INPUT_LOCK.json](../../frozen/crypto_fi_640_joint_correctness/evidence/INPUT_LOCK.json)固定。历史文件仅读。

对象为FI DOI10.46298/fi.14425、期刊/arXiv:2410.03948v4打印算法，PDF SHA256为`bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`。固定n=640、D=15、q=32768、m̄=n̄=8、B=2，均匀Setup，共用一个A，所有χ640坐标和调用独立，token诚实生成一次且未筛选。

Ord_n按n列、位平面顺序解释，H有9600列，并与Tensor_D满足gadget恒等式。Decode采用官方最近整数平局向上。χ640的零点及每个正/负点概率分子依次为

`[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]/65536`。

FI原图p12的KeyGen/Enc/Decode、p14的TG/Upd与官方2021规范p10舍入、p25质量/参数已定点核读；源TeX相应算法段也已核对。原始文件副本在sources，具体指纹及实读范围见SOURCE_AND_COMPUTATION_RECORD.json。

## 2. 残差、符号与维度

两代诚实钥匙为S_x,E_x←χ^(640×8)，B_x=A S_x+E_x。初始Enc采U₀,F₀←χ^(8×640)、G₀←χ^(8×8)：

C₁=U₀A+F₀，C₂=U₀B_old+G₀+Encode(M)。

TG采U₁,F₁∈χ^(9600×640)、G₁∈χ^(9600×8)，U₂,F₂∈χ^(640×640)、G₂∈χ^(640×8)，其四块为

\[
\begin{aligned}
P_1&=U_1A+F_1,&Q_1&=U_1B_{new}+G_1-\operatorname{Tensor}_D(S_{old}),\\
P_2&=U_2A+F_2,&Q_2&=U_2B_{new}+G_2.
\end{aligned}
\]

Upd新采R∈χ^(8×640)，返回C′₁=HP₁+RP₂、C′₂=C₂+HQ₁+RQ₂，H=Ord_n(C₁)。消去A和gadget项得

\[
C'_2-C'_1S_{new}-\operatorname{Encode}(M)
\equiv U_0E_{old}-F_0S_{old}+G_0
+(HU_1+RU_2)E_{new}-(HF_1+RF_2)S_{new}+HG_1+RG_2\pmod q.
\tag{1}
\]

固定第一行。u、f、r均为1×640，h为1×9600，w=|h|。令a=hU₁+rU₂、b=hF₁+rF₂，a、b均为1×640。对j=1,…,8：

\[
N_j=uE_{old}[:,j]-fS_{old}[:,j]+G_0[1,j]
+aE_{new}[:,j]-bS_{new}[:,j]+hG_1[:,j]+rG_2[:,j]\pmod q.
\tag{2}
\]

该式与候选一致。小量取整数[−12,12]代表，h取0/1；a、b可先作为整数和，再取模。它们通常超出χ的小支持，本文没有给a、b施加小量截断。(1)(2)是同余关系，所有回绕由模群特征函数处理。

## 3. 命题1：共同环境下独立同分布

定义两个嵌套σ域：

\[
\mathcal B=\sigma(A,U_0,F_0,R),\qquad
V=\sigma(\mathcal B,U_1,F_1,U_2,F_2).
\tag{3}
\]

V正是题设环境。它固定u、f、h、r、a、b，也固定P₂及其rank这一派生量。外层仍对P₂的全部诚实分布平均，未筛选可逆token。V没有固定父C₂、两代公钥/秘密输出或含剩余随机量的Q/G字段。

**命题1。** 对每个正概率的V值，N₁,…,N₈独立同分布。

**证明。** 给定V，剩余列包

\[
\Xi_j=(E_{old}[:,j],S_{old}[:,j],G_0[1,j],
E_{new}[:,j],S_{new}[:,j],G_1[:,j],G_2[:,j])
\]

在j之间独立，且每包均为相同维度的独立χ坐标。原因是所有原始χ抽样与A及V中的原始χ变量独立，钥匙矩阵和G矩阵的不同列也独立。B_old/B_new是A与这些列的函数，并没有作为额外条件量。

式(2)对每列施加相同的固定系数线性函数，因此N_j条件独立同分布。一次TG的U/F矩阵在8个坐标之间共享，现已被V固定；这里没有为每个坐标重新生成token。□

## 4. 解码集合、消息与行事件

官方平局向上给正确残差集合

\[
\mathcal D=\{-4096,-4095,\ldots,4095\}\bmod32768,
\quad |\mathcal D|=8192.
\tag{4}
\]

每个2位标签k编码为8192k；平局规则具有相应平移性质，因此正确当且仅当N_j∈D，与k无关。虽然同一行的8个消息标签可以不同，8个残差和正确指示仍满足命题1。

置p(V)=Pr[N_j∈D|V]。精确地

\[
\boxed{p_{row}=\Pr[\text{第一行8个坐标均正确}]=E[p(V)^8].}
\tag{5}
\]

该事件是16位行消息正确。所有64个坐标正确蕴含该事件。本文对所有固定128位消息给相同结论，无需消息并集。改变舍入法需要重审共同p(V)或另计边界；本轮固定官方半向上规则。

## 5. 命题2：条件特征函数

令ψ(t)=E_{X←χ}[exp(2πitX/q)]。式(2)中全部剩余χ坐标独立，故

\[
\boxed{\Phi_V(t)=\psi(t)^{1+w}
\prod_{k=1}^{640}\psi(tu_k)\psi(-tf_k)\psi(ta_k)\psi(-tb_k)
\prod_{i=1}^{640}\psi(tr_i).}
\tag{6}
\]

| 因子 | 对应剩余随机量 |
|---|---|
| ψ(t) | G₀[1,j] |
| ψ(t)^w | h选中的G₁[:,j] |
| ψ(tu_k)、ψ(−tf_k) | E_old[k,j]、S_old[k,j] |
| ψ(ta_k)、ψ(−tb_k) | E_new[k,j]、S_new[k,j] |
| ψ(tr_i) | G₂[i,j] |

本轮把旧、新钥匙和G留作列随机量，和上一轮固定钥匙、平均TG行的条件环境不同。两种分解均由同一真实残差得到，不能混用各自的条件独立性。

## 6. 命题3：真实a、b系数的条件分布

给定较小的环境\(\mathcal B\)，h和r固定，但U₁/F₁/U₂/F₂仍为原独立χ矩阵。对每个k，a_k和b_k各具有模q的加权和分布

\[
T_{\mathcal B}=\sum_{\ell=1}^{w}X_\ell+\sum_{i=1}^{640}r_iY_i\pmod q,
\quad X_\ell,Y_i\text{独立}\chi.
\tag{7}
\]

不同k使用不同原始矩阵列；a族使用U，b族使用F。因此全部1280个系数在给定B后独立同分布。它们共享h、r、A的关系由条件保留，没有先把系数换成均匀或Gaussian。

该标量律的特征函数精确为

\[
\varphi_{\mathcal B}(s)=\psi(s)^w\prod_i\psi(sr_i).
\tag{8}
\]

给定B后对a、b积分就是对一次诚实TG的U/F币积分。若额外筛选P₂ rank，其对应U₂/F₂的积分律会改变，本文没有作该操作。

## 7. 使用范围及待复核点

命题1–3是本轮知情纸面推导，证明已列出，独立复核待进行。数值行界另依赖：B好事件概率；(8)控制E|ψ(tT)|²的全频率包络；弦线不等式对八阶混合矩的处理。完整链见[JOINT_PROBABILITY_BOUND.md](JOINT_PROBABILITY_BOUND.md)。

本轮不使用行间独立性。同一列在不同密文行共享钥匙列和G₁/G₂，进一步把行上界取8次幂需要新的联合证明。实际作者seed/程序对应也保持既有来源责任。
