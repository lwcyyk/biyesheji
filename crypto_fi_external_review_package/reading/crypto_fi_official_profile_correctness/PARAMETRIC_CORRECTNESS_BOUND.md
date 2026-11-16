> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../frozen/crypto_fi_official_profile_correctness/PARAMETRIC_CORRECTNESS_BOUND.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# 参数化可靠性判据与官方976／1344配置认证

2026-11-11，Asia/Shanghai。身份：`INFORMED_PARAMETRIC_PROBABILITY_RESEARCH_AND_DETERMINISTIC_FINITE_CERTIFICATE_CHECK`，即知情参数化概率研究与确定性有限证书核对。640作者证明、复核与v2.2研究稿均已可见。本轮新增独立、人工、盲审、跨模型、子代理及证明助手审阅均为0。

**结论。** 下述参数化条件命题成立。其在官方976、1344精确分布上的新证书，对每个预先固定的公共矩阵A分别给出一次更新后完整消息错误率至少92.1979375%、79.3884688%；额外条件于初始完整消息已正确，同一显示端点成立。数值、逐项分布、全部频率及有向比较见[OFFICIAL_PROFILE_CERTIFICATES.json](../../frozen/crypto_fi_official_profile_correctness/OFFICIAL_PROFILE_CERTIFICATES.json)，适用范围与论文影响见[PROFILE_RESULTS_AND_SCOPE.md](PROFILE_RESULTS_AND_SCOPE.md)。

## 1. 参数范围与冻结合同

取整数D≥1、q=2^D、n≥1、m̄≥1、k=n̄≥1，0≤B≤D。数学分解适用于这些尺寸；称为FI打印参数实例时另携带其8∣n要求。χ为整数上有限支撑的对称概率分布。χ的整数提升用于PGF与范数，模q像用于环特征函数。若不同整数支撑点模q合并，涉及模原子时应先合并质量。

固定以下实验合同：

1. A∈(Z/qZ)^(n×n)在全部相关原始χ币之前固定，两代共用；消息M及被分析的行、坐标亦在这些币之前固定。
2. 给定A后，两代KeyGen、Enc、TG、Upd全部原始χ坐标和调用具有声明的精确独立乘积律。概率平均这些后续币。
3. 执行FI期刊／arXiv v4打印KeyGen、Enc、TG、Upd公式一次。Ord按C₁的实际n列作D位0/1分解，位平面顺序与Tensor_D配对，满足H·Tensor_D(S)=C₁S modq。
4. TG、Upd采用一次诚实未筛选抽样，全部P₂秩均计入。公钥、token输出、成功或秩事件保持原实验的自然分布。
5. Encode(k)=kq/2^B，Decode(c)=floor(c2^B/q+1/2) mod2^B，使用半向上舍入。每个标签的正确残差集合相同。

官方两组的χ支撑分别为[−10,10]、[−6,6]，均在模群中逐点嵌入。矩阵A允许为零、奇异、低秩，或来自任意前置公共seed展开。具体程序的适用性另由采样与算术映射证据决定。

## 2. 从原始算法到残差

两代S_x、E_x尺寸均为n×k，公钥B_x=AS_x+E_x。Enc的U₀、F₀为m̄×n，G₀为m̄×k：

\[
C_1=U_0A+F_0,\qquad C_2=U_0B_{old}+G_0+\operatorname{Encode}(M).
\]

TG的U₁、F₁为nD×n，G₁为nD×k；U₂、F₂为n×n，G₂为n×k：

\[
P_1=U_1A+F_1,\quad Q_1=U_1B_{new}+G_1-\operatorname{Tensor}_D(S_{old}),
\]
\[
P_2=U_2A+F_2,\quad Q_2=U_2B_{new}+G_2.
\]

Upd采R∼χ^(m̄×n)，置H=Ord_n(C₁)，输出C′₁=HP₁+RP₂、C′₂=C₂+HQ₁+RQ₂。代入并逐样本抵消A及gadget项，得到

\[
N=U_0E_{old}-F_0S_{old}+G_0
 +(HU_1+RU_2)E_{new}-(HF_1+RF_2)S_{new}+HG_1+RG_2\pmod q.
\tag{1}
\]

指定行的u、f、r长度为n，h长度为nD，w=|h|，a=hU₁+rU₂、b=hF₁+rF₂。其第j坐标满足

\[
N_j=uE_{old}[:,j]-fS_{old}[:,j]+G_0[i,j]
 +aE_{new}[:,j]-bS_{new}[:,j]+hG_1[:,j]+rG_2[:,j].
\tag{2}
\]

式(1)与(2)对每个A、每个原始币取值成立。消息仅贡献已抵消的编码平移，故逐个预先固定合法消息适用。

## 3. 两层条件环境、真实系数律与绝对Fourier矩

令

\[
\mathcal B_{env}=\sigma(A,U_0,F_0,R),\qquad
V=\sigma(\mathcal B_{env},U_1,F_1,U_2,F_2).
\tag{3}
\]

### 3.1 同行条件列包

给定每个正概率V值，以下原始列包跨j=1,…,k独立同分布，并独立于V的原始币：

\[
\Xi_j=(E_{old}[:,j],S_{old}[:,j],G_0[i,j],
 E_{new}[:,j],S_{new}[:,j],G_1[:,j],G_2[:,j]).
\]

式(2)对每包施加同一确定系数函数；正确残差集合𝓓对所有标签相同。置p(V)=Pr(N_j∈𝓓∣V)，J为指定行全部正确，则

\[
\boxed{\Pr(J\mid A)=E[p(V)^k\mid A].}
\tag{4}
\]

该等式保留行内共享钥匙、共享token及共同父密文的依赖。条件环境采用原始币。初始已正确事件I留到§6用事件比率处理。

### 3.2 较小环境内的2n个真实系数

给定𝓑_env后，h与r固定。不同矩阵列及U/F两类原始币彼此独立，故2n个a_l、b_l独立同律，各具真实加权和模q律

\[
T_{\mathcal B}=\sum_{\ell=1}^{w}X_\ell+\sum_{i=1}^{n}r_iY_i\pmod q,
\qquad
\varphi_{\mathcal B}(s)=\psi(s)^w\prod_i\psi(sr_i),
\tag{5}
\]

其中X、Y均为新的辅助χ变量，ψ(t)=Eχ exp(2πitX/q)。辅助变量描述原实验中系数的分布。实际实验仍采一次TG。

给定V，(2)中χ币独立，故

\[
\Phi_V(t)=\psi(t)^{1+w}
 \prod_{l=1}^{n}\psi(tu_l)\psi(-tf_l)\psi(ta_l)\psi(-tb_l)
 \prod_i\psi(tr_i).
\tag{6}
\]

定义m_t=E_T|ψ(tT)|、D_t=E_T|ψ(tT)|²∈[0,1]。其余模至多1的因子可丢弃，独立性和Cauchy–Schwarz给出

\[
\boxed{E[|\Phi_V(t)|\mid\mathcal B_{env}]
 \le m_t^{2n}\le D_t^n.}
\tag{7}
\]

若ν_d=Pr(X−X′=d)，有限展开直接给

\[
\boxed{D_t=\sum_d\nu_d\varphi_{\mathcal B}(td).}
\tag{8}
\]

χ对称使φ为实数；D_t的非负性来自其原定义。逐项用|φ|上界时保留全部ν质量，符号或回绕均有合法上包络。P₂在V层已确定，其所有秩仍在较小环境及外层积分中按诚实质量遍历。

## 4. 参数化判据

设𝓓⊆Z_q，π₀=|𝓓|/q。设好事件𝓖为𝓑_env可测，Pr(𝓖ᶜ∣A)≤δ，0≤δ≤1；对每个好环境的正概率取值，或一般条件律的几乎处处取值，已认证

\[
E[|p(V)-\pi_0|\mid\mathcal B_{env}]\le Z,\qquad Z\ge0.
\tag{9}
\]

定义

\[
C_k(\pi_0)=\sum_{j=0}^{k-1}\pi_0^j
 =\frac{1-\pi_0^k}{1-\pi_0}\quad(0\le\pi_0<1),
\]
\[
F=\pi_0^k+C_k(\pi_0)Z.
\tag{10}
\]

**命题P。** 在§1—3合同及(9)下，候选通式

\[
\boxed{\Pr(J\mid A)\le U_{row}^{raw}:=(1-\delta)F+\delta}
\tag{11}
\]

成立。更便于处理平凡端点的版本为

\[
U_J=(1-\delta)\min\{1,F,\pi_0+Z\}+\delta,
\quad L_J=(1-\delta)(\pi_0-Z)_+^k,
\tag{12}
\]
\[
L_S=(1-\delta)(\pi_0-Z)_+,
\quad U_S=(1-\delta)\min\{1,\pi_0+Z\}+\delta.
\tag{13}
\]

这里S为指定坐标正确事件。相应区间为L_J≤Pr(J∣A)≤U_J、L_S≤Pr(S∣A)≤U_S。

**证明。** 对0≤x≤1，x≤π₀时有x^k≤π₀^k；x>π₀时

\[
\frac{x^k-\pi_0^k}{x-\pi_0}
 =\sum_{j=0}^{k-1}x^{k-1-j}\pi_0^j\le C_k(\pi_0).
\]

因此x^k≤π₀^k+C_k(π₀)(x−π₀)_+。由(9)得到每个好环境内的行上界F；另有p^k≤p及p≤1，可同时取min{1,F,π₀+Z}=:f≤1。设真实坏概率b_A≤δ，则

\[
\Pr(J\mid A)\le(1-b_A)f+b_A\le(1-\delta)f+\delta.
\]

当F≤1时(11)由同一单调性得到；F>1时其右侧≥1，概率的平凡上界即足够。对好环境先用E[p∣𝓑]≥(π₀−Z)_+，再用Jensen得到E[p^k∣𝓑]≥(π₀−Z)_+^k，解除好环境即为(12)下界。坐标界由(9)同理得到。证毕。

**端点。** π₀=0时𝓓为空、全部非空正确事件概率为0，C_k=1；π₀=1时𝓓为全群、相应概率为1，C_k按连续延拓取k。k=1时C₁=1。δ=1时(12)—(13)退化为[0,1]。Z≥π₀时下界可为0；F≥1时上界按(12)截为1。空行k=0可另定义J为必然事件、C₀=0；本命题实际算法参数取k≥1。n=0或D=0的空尺寸由各自算法单列，本命题取n,D≥1。

### 4.1 如何从全频率包络取得Z

用有限群Fourier反演及|𝓓̂(t)|≤|𝓓|，

\[
|p(V)-\pi_0|\le\pi_0\sum_{t=1}^{q-1}|\Phi_V(t)|.
\]

若对每个好环境认证D_t≤R_t，则(7)给

\[
Z\le\pi_0\sum_{t=1}^{q-1}R_t^n.
\tag{14}
\]

q为偶数、正负频率共轭时，本轮采用保守形式

\[
\boxed{Z=2\pi_0\sum_g\#g\,Q_g,\qquad Q_g\ge R_g^n,}
\tag{15}
\]

分组完整覆盖1,…,q/2。Nyquist项按一对计费。有限求和可以与条件期望交换。采用精确𝓓̂还能收紧(14)，本轮(15)已经足够作出两项裁决。

### 4.2 官方Decode导出π₀

对1≤B<D，令h_dec=q/2^(B+1)。半向上规则在编码平移后等价于−1/2≤e2^B/q<1/2，故

\[
\mathcal D=\{-h_{dec},\ldots,h_{dec}-1\}\bmod q,
\quad |\mathcal D|=q/2^B,\quad\pi_0=2^{-B}.
\tag{16}
\]

负半宽端点正确，正半宽端点错误。B=D时𝓓={0}，π₀=1/q；B=0时唯一标签总被正确解码、𝓓=Z_q、π₀=1。976的半宽4096，1344的半宽2048；本轮穷尽两组的全部标签及全部65536个残差代表，分别核准524288、1048576个组合。

## 5. 完整消息与已正确条件化

令K为更新后完整m̄×k消息正确事件，I为初始完整消息正确。点态K⊆J⊆S给出

\[
\Pr(K\mid A)\le U_J,\qquad\Pr(K^c\mid A)\ge1-U_J.
\tag{17}
\]

若已有每坐标失败上界，也可对Kᶜ用并集得到完整正确率下界；当前高错误率结果使用(17)。同行下界L_J的对象是J。

若Pr(Iᶜ∣A)≤α<1，对E=S或J及其原实验区间[L_E,U_E]，事件交集和分母界给

\[
\max\{0,(L_E-\alpha)/(1-\alpha)\}
 \le\Pr(E\mid I,A)\le\min\{1,U_E/(1-\alpha)\}.
\tag{18}
\]

同理Pr(K∣I,A)≤min{1,U_J/(1−α)}，错误率取补。推导可先置ρ=Pr(Iᶜ∣A)，使用(L_E−ρ)/(1−ρ)与U_E/(1−ρ)，再利用前者递减、后者递增代入α。α=1时I可能为零概率，须另有正分母证据。I条件下的列包分布由原实验诱导，式(18)以事件关系承担条件化。

## 6. 初始残差PGF与有理tilt

初始单坐标η₀=uE_old[:,j]−fS_old[:,j]+G₀[i,j]，A逐样本消去。该坐标涉及的原始变量互不相交。χ及XY对称，故对任意有理z>1，完整有限Laurent PGF为

\[
A_\chi(z)=\sum_x\chi(x)z^x,\quad
B_\chi(z)=\sum_{x,y}\chi(x)\chi(y)z^{xy},
\]
\[
\boxed{E[z^{\eta_0}\mid A]=A_\chi(z)B_\chi(z)^{2n}.}
\tag{19}
\]

如果χ缺少对称性，一般形式应保留Bχ(z)^nBχ(z^−1)^n；本轮两组均精确对称。对正整数半宽h_dec，双侧Markov给

\[
\Pr(\text{初始坐标错误}\mid A)
 \le\Pr(|\eta_0|\ge h_{dec}\mid A)
 \le 2z^{-h_{dec}}A_\chi(z)B_\chi(z)^{2n}=:a_{coord}.
\tag{20}
\]

回绕后的额外正确质量及负半宽端点被保守留在尾中。完整消息用并集α≤min{1,m̄k a_coord}，允许原始坐标间共享币。B=D时可取整数阈值1，|η₀|<1足够保证正确；B=0直接采用正确概率1的端点。

| 配置 | h_dec | 有理z | PGF乘积幂 | 坐标失败上界 | 完整消息失败上界 |
|---|---:|---:|---:|---:|---:|
| 976 | 4096 | 107/100 | 1952 | 2^-199 | 2^-193 |
| 1344 | 2048 | 59/50 | 2688 | 2^-252 | 2^-246 |

证书逐项求和完整21点／441对、13点／169对，并直接比较大整数。`next_exponent_fails`只描述所选Chernoff包络的下一个二进制指数；实际失败概率的紧值另有责任。

## 7. 从官方CDF重新导出两组分布

官方规则：16位均匀字r的低位给符号、t=r>>1，绝对值e=Σ_(j=0)^(s−1)1[t>T(j)]。完整CDF末项T(s)=32767确定末端合同；采样循环访问前s项。分母65536下

\[
w_0=2(T(0)+1),\quad w_{+j}=w_{-j}=T(j)-T(j-1),\quad1\le j\le s.
\tag{21}
\]

| 配置 | 完整CDF | 0及每个±j的质量分子 |
|---|---|---|
| 976 | 5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767 | 11278,10277,7774,4882,2545,1101,396,118,29,6,1 |
| 1344 | 9142,23462,30338,32361,32725,32765,32767 | 18286,14320,6876,2023,364,40,2 |

976沿用v2.1已更正行。1344应用[官方issue35回复](https://github.com/microsoft/PQCrypto-LWEKE/issues/35#issuecomment-2504969837)：T(5)=32765、T(6)=32767。2023原PDF的缺项保留为历史来源差异。

| 配置 | 支持／总分子 | 偶／奇分子 | 最大原子a₀（唯一在0） | EχX² | EχX⁴ | ν₁ |
|---|---|---|---|---|---|---|
| 976 | [−10,10]／65536 | 32768／32768 | 5639/32768 | 44009/8192 | 173/2 | 249463133/2147483648 |
| 1344 | [−6,6]／65536 | 32770／32766 | 9143/32768 | 66927/32768 | 408975/32768 | 46872625/268435456 |

两组全部65536个采样输入字均作确定性穷举，并逐点匹配(21)。完整差值律分别有41、25点，ν_d分子由Σ_x w_xw_(x−d)重建、总分子65536²且对称；全部原子保存在JSON的`difference_law.mass`。本轮所用二阶矩均来自精确CDF质量，规范中的σ是分布设计参数。

## 8. 逐固定A环境：全平移位重量PGF

### 8.1 通用非零坐标界与本轮改进

给定A,u后，C₁[l]=(uA)[l]+f_l modq跨l独立。若a₀=max_x Pr(χ modq=x)，L为非零父坐标个数，则w≥L，且对0<z<1有E[z^L∣A,u]≤[a₀+(1−a₀)z]^n。这是640使用的通用入口。

本轮保留一个父坐标的完整D位重量，令

\[
g_H(z)=\max_{a\in\mathbb Z_q}\sum_x\chi(x)z^{\operatorname{wt}_D(a+x\bmod q)}.
\tag{22}
\]

由于每个平移的PGF≤g_H，独立父坐标给

\[
E[z^w\mid A,u]\le g_H(z)^n,
\quad\boxed{\Pr(w\le h_0\mid A)\le z^{-h_0}g_H(z)^n.}
\tag{23}
\]

该证明对所有固定平移逐点成立，随后依次对f、u平均；A的秩与分布均保持任意。0或1端点按PGF连续值解释，Markov步骤取0<z<1。

本轮逐组穷尽65536个平移，以整数共同分母认证最大值。976有1484种重量质量向量，1344有1000种；采用的z下最大平移分别唯一为4、2。若w_j是重量j的质量分子，最大平移的非零w_j为：

| 配置 | w₀,w₁,w₂,w₃ | w₁₄,w₁₅,w₁₆ | z_H | h₀ | 认证Pr(w≤h₀∣A) |
|---|---|---|---:|---:|---:|
| 976 | 2545,26479,29854,5007 | 30,520,1101 | 33/40 | 1477 | ≤2^-40 |
| 1344 | 6876,39484,16707,40 | 2,404,2023 | 9/10 | 1644 | ≤2^-40 |

其余重量质量为0，g_H(z)=Σ_jw_jz^j/65536。两组g_H均严格小于同z下的a₀+(1−a₀)z。新阈值均超过n，单靠w≥L、L≤n无法认证这些阈值。这是本轮超出640常规常数代入的具体技术增量；其工具仍为有限最大化、条件独立和指数Markov。

### 8.2 R平方范数下尾

令R₂=Σ_i r_i²。对0<z_R<1，

\[
g_R(z_R)=\sum_x\chi(x)z_R^{x^2},\quad
\Pr(R_2\le r_0\mid A)\le z_R^{-r_0}g_R(z_R)^n.
\tag{24}
\]

| 配置 | z_R | r₀ | 认证下尾 | 好环境w+R₂下界 |
|---|---:|---:|---:|---:|
| 976 | 123/128 | 3669 | ≤2^-40 | 5146 |
| 1344 | 59/64 | 2030 | ≤2^-40 | 3674 |

取𝓖={w≥h₀,R₂≥r₀}。坏事件w<h₀、R₂<r₀均包含于表中含等号的尾事件，故逐固定A有δ=2^-39。各式完整有理PGF和整数比较指纹在JSON的`environment`。

## 9. ψ包络、模子群与全频率

### 9.1 小参数正性与衰减

记v=EχX²、m₄=EχX⁴。对称性给ψ(x)=E cos(2πxX/q)。由全实轴cos二次下界与四次上界、157/50<π<22/7，对|x|≤q/j有

\[
\psi(x)\ge1-2(22/7)^2v/j^2>0,
\]
\[
\psi(x)\le1-K_jx^2/q^2,\qquad
K_j\le2(157/50)^2v-\tfrac23(22/7)^4m_4/j^2.
\tag{25}
\]

本轮逐一认证右侧正性和下列整数K_j：

| 配置 | j=128，域512 | j=64，域1024 | j=32，域2048 | j=16，域4096 |
|---|---:|---:|---:|---:|
| 976 | 105 | 104 | 100 | 83 |
| 1344 | 40 | 40 | 39 | 37 |

因此这些域内|ψ(x)|≤exp(−K_jx²/q²)。若|td|和全部|tdr_i|均在相应域，则每个好环境内

\[
|\varphi_{\mathcal B}(td)|
 \le\exp[-K_j(h_0+r_0)t^2d^2/q^2].
\tag{26}
\]

本轮通过hi·d_max·sχ≤q/j逐组检查未回绕域。系数T本身可任意回绕，其真实律由(5)保持。

### 9.2 高频与1344奇偶偏差

保留χ的0、±1原子配对，

\[
|\psi(t)|^2\le1-8p_0p_1\sin^2(\pi t/q).
\tag{27}
\]

对q/32≤t≤q/2，sin(πt/q)≥2t/q，故|ψ(t)|≤exp(−p₀p₁/64)。对128≤t≤q/32用(25)的j=32。于是全部128≤t≤q/2统一有

\[
|\varphi_{\mathcal B}(t)|\le\rho,
\quad\rho\ge e^{-x_H},\quad
x_H=\min\{K_{32}h_0\,128^2/q^2,\ h_0p_0p_1/64\}.
\tag{28}
\]

这里只用H部分，r部分模≤1。代入(8)的d=±1并对其余差值质量保留上界1，

\[
D_t\le1-2\nu_1(1-\rho).
\tag{29}
\]

两组χ的0与1均有正质量，(27)保证所有非零频率|ψ(t)|<1。即使某些d在频率t处落入模子群的消失点，d=±1仍为非平凡字符，(29)保持。

特别地θ:=ψ(q/2)=Pr(X偶)−Pr(X奇)。976的θ=0；1344的θ=1/16384。若o(r)是r_i中奇数个数，

\[
\varphi_{\mathcal B}(q/2)=\theta^{w+o(r)},
\quad\Pr(T\text{偶}\mid\mathcal B)=\tfrac12(1+\theta^{w+o(r)}).
\tag{30}
\]

指数为0时按乘积定义取1，含θ=0的0次幂亦如此；本轮好环境w>0。差值的偶／奇质量为(P_even²+P_odd²)、2P_evenP_odd。1344的Nyquist D_t可写为(1+θ²)/2+(1−θ²)θ^(w+o(r))/2；本轮保守高频包络已覆盖它，实际有偏概率同时完整登记。

### 9.3 所有非零频率的分组

下表中“全”表示d_max=2sχ，单频率分别认证R_t；中频组用其最小频率lo及指定d_max，未保留的ν质量按1计费。

| 配置 | t范围 | j／K_j | d_max | 最大未回绕参数hi·d_max·sχ |
|---|---|---|---:|---:|
| 976 | 1–2 | 128／105 | 全20 | 400≤512 |
| 976 | 3–5 | 64／104 | 全20 | 1000≤1024 |
| 976 | 6–10 | 32／100 | 全20 | 2000≤2048 |
| 976 | 11–20 | 16／83 | 全20 | 4000≤4096 |
| 976 | 21–31 | 32／100 | 6 | 1860≤2048 |
| 976 | 32–63 | 32／100 | 3 | 1890≤2048 |
| 976 | 64–127 | 32／100 | 1 | 1270≤2048 |
| 976 | 128–32768 | 高频(28)—(29) | ±1，其余按1 | H部分无需r无回绕 |
| 1344 | 1–7 | 128／40 | 全12 | 504≤512 |
| 1344 | 8–14 | 64／40 | 全12 | 1008≤1024 |
| 1344 | 15–28 | 32／39 | 全12 | 2016≤2048 |
| 1344 | 29–56 | 16／37 | 全12 | 4032≤4096 |
| 1344 | 57–63 | 32／39 | 5 | 1890≤2048 |
| 1344 | 64–127 | 32／39 | 2 | 1524≤2048 |
| 1344 | 128–32768 | 高频(28)—(29) | ±1，其余按1 | H部分无需r无回绕 |

两个配置分别有24、59个实际证书组，计数均恰为32768。负频率配对，Nyquist保守多收一次。对于中频与低频，

\[
R_g=1-2\sum_{d=1}^{d_{max}}\nu_d(1-E_{g,d}),
\quad E_{g,d}\ge e^{-K_j(h_0+r_0)lo^2d^2/q^2}.
\tag{31}
\]

## 10. 有向有理证书与数值

对x≥0，S₂₄(x)=Σ_(j=0)^24 x^j/j!≤e^x，故e^−x≤1/S₂₄(x)。每个E_(g,d)、ρ取该倒数的64位dyadic向上包络；精确ν加权后，对R_g^n取80位dyadic向上包络Q_g。所有正而极小的幂均向上保留。

每个指数上包的dyadic额外误差<2^-64；R_g加权误差≤2^-64，x↦x^n在[0,1]的Lipschitz常数为n。因此(15)中这类额外松弛至多

\[
q\pi_0(n2^{-64}+2^{-80})<2^{-41}
\tag{32}
\]

对两组均以精确分数认证。这一损失已经进入Z。Taylor倒数的解析松弛也已进入E、R、Q；未计费的频率尾、差值截尾及概率截尾均为0。

| 配置／A量词 | h₀ | r₀ | δ | Z（仅展示近似） | 行及完整消息正确率共同显示上界 |
|---|---:|---:|---:|---:|---:|
| 976／每个固定A | 1477 | 3669 | 2^-39 | 0.06826799845358313 | 0.078020625 |
| 1344／每个固定A | 1644 | 2030 | 2^-39 | 0.19323310441065097 | 0.206115312 |
| 976／均匀全矩阵Setup平均 | 7339 | 3669 | 2^-38 | 0.014995375541432857 | 0.017137631 |
| 1344／均匀全矩阵Setup平均 | 10205 | 2030 | 2^-38 | 0.07763760183393992 | 0.082813443 |

C₈(1/8)=2396745/2097152，C₈(1/16)=286331153/268435456。所有显示上界已覆盖(18)的初始已正确条件化。精确证书原实验上界更小，显示端点由有理交叉比较向外取整。

## 11. 均匀Setup的独立量词与公共seed

额外假设A为均匀全矩阵，独立于所有χ币。u在Z_(2^D)含单位坐标，当且仅当至少一个u_i为奇数；给定这样的u及任意f，uA+f是n个独立均匀环元素，故其nD位公平独立。

令p_even=Prχ(X偶)，则坏单位事件的准确概率为p_even^n。976为2^-976；1344为(16385/32768)^1344≤2^-1343，保留其真实偏差。对z_U=9/10，H尾采用z_U^−h[(1+z_U)/2]^(nD)。h=7339、10205时均≤2^-40，连同R₂尾及单位坏事件可取δ_U=2^-38。

由此取得§10的额外平均界，量词为“均匀全矩阵A与全部诚实币共同平均”。逐固定A结果则可对任意前置A分布积分。若A=g(Z_pub)，且给定每个相关公共seed后，全部后续χ仍有冻结的乘积律、算法及消息量词均满足合同，则逐seed应用固定A界再积分即可。更紧的均匀Setup数字继续携带其额外分布依据。

## 12. 直接推论、先例与适用边界

1. 取k=8、π₀=1/4、Z与δ为640旧证书值，(11)精确复现其C和U。本轮核对这一有理特化，未修改640历史文件。
2. 两组官方配置取得CERTIFIED_HIGH_ERROR。有限判据在模型内足以排除“一次更新具有接近1的完整消息成功率”这一配置性判断。任意渐近族的结论仍需给出该族的全部前提与统一常数。
3. 定理的条件承担实质作用。χ=δ₀时初始与更新残差恒为0、正确率为1；此时K_j>0及小Z高混合证书无法建立。支持包含于真模子群的χ可能保留未衰减字符。参数化命题本身仅在已认证(9)后输出数值，独立采样与同A合同单独不足以强制高错误。
4. 初始PGF、指数Markov／Chernoff、有限群Fourier、Cauchy–Schwarz、Jensen及凸弦线属于成熟工具。参数化式(11)是640论证的直接抽象，全球新方法或优先权保持未认证。本轮具体增量为：全平移位重量PGF、两组精确分布的完整频率认证，以及1344真实奇偶偏差下的Setup与Nyquist处理。
5. 公开定向检索使用6条查询，原始回执见[evidence/PUBLIC_PRECEDENT_SEARCH_RECEIPT.json](../../frozen/crypto_fi_official_profile_correctness/evidence/PUBLIC_PRECEDENT_SEARCH_RECEIPT.json)。检索定位到FI原文及经典工具来源；所得已核材料未建立与本轮同合同、同官方配置数值结论的直接覆盖。该范围加上历史截至2026-11-10的有界审计，支持限定的先例比较；全球优先权继续留项。

经典工具参考：Chernoff，*A Measure of Asymptotic Efficiency for Tests of a Hypothesis Based on the Sum of Observations*，Annals of Mathematical Statistics23(4),493–507,1952，[DOI](https://doi.org/10.1214/aoms/1177729330)，本轮题录由[Stanford原始技术报告目录](https://statistics.stanford.edu/technical-reports/measure-asymptotic-efficiency-tests-hypothesis-based-sum-observations)交叉核对，DOI页面打开失败单列于回执；Diaconis，*Group Representations in Probability and Statistics*，IMS1988，[出版社记录](https://doi.org/10.1214/lnms/1215467407)，用于有限群Fourier工具归属，当前读取级别为题录。本文(7)—(32)提供自含推导，引用的题录读取范围与数学证明分别登记。

## 13. 原始来源与复核入口

- FI期刊/v4：[原论文](https://doi.org/10.46298/fi.14425)，本地冻结PDF SHA256 `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`；PDF12、14、15及源TeX L491—706用于算法、Decode与Theorem6.3。本轮源PDF结构预检PASS，23页。
- 官方2021规范：`crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf`，SHA256 `5c3440b311c7ee4fba8b9a12e0ff567eb75c29fef66843f3eecc16f137164f7d`；PDF10舍入、15–16采样/Decode、25质量与参数。结构预检PASS，59页。
- 官方2023提案：`crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf`，SHA256 `4688192bf5f5ac29e622ef359860890d2e97c224216baea2216dc42ef8d1547f`；物理PDF8、15、16，即印刷4、11、12。结构预检PASS，21页。2021／2023的seed接口差异保留；本研究冻结其标量χ、参数与舍入，后续原始币采用§1理想联合律。
- 1344勘误：官方issue35的Patrick Longa回复，本轮经只读GitHub工具取得并保存[原始回执](../../frozen/crypto_fi_official_profile_correctness/evidence/OFFICIAL_1344_ERRATUM_TOOL_RECEIPT.json)。
- v2.1 INC976及分布审计、v2.2稿、640固定A证明与复核为只读历史输入；[输入快照](../../frozen/crypto_fi_official_profile_correctness/evidence/INPUT_SNAPSHOT.json)登记61个历史文件。PDF源字节、页码及图像哈希另见[evidence/SOURCE_PAGES.json](../../frozen/crypto_fi_official_profile_correctness/evidence/SOURCE_PAGES.json)。
- [生成器](../../frozen/crypto_fi_official_profile_correctness/evidence/compute_profile_certificates.py)仅做确定性标量运算；[核对器](../../frozen/crypto_fi_official_profile_correctness/evidence/verify_profile_certificates.py)只读证书与历史输入，写出[evidence/CERTIFICATE_CHECK.json](../../frozen/crypto_fi_official_profile_correctness/evidence/CERTIFICATE_CHECK.json)。3194项有限比较通过；其中包含分布、所有平移、全频率有向链、条件化端点及640特化。计数描述核对范围，新增独立数学审阅为0。

本轮候选机制实现、钥匙／密文／token抽样、Monte Carlo、LWE求解、作者联系及外部服务实验均为0。浮点对数仅在[evidence/PARAMETER_SELECTION_NONCERTIFYING.json](../../frozen/crypto_fi_official_profile_correctness/evidence/PARAMETER_SELECTION_NONCERTIFYING.json)对应的确定性选参阶段出现，证书生成与核对均使用整数／有理数。
