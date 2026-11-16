# Binary Constrained q-Center with a Common Finite Relation

**Working note for mathematical and bibliographic review. Version ER-1, 6 November 2026.**

## Abstract

We present a deterministic exact search for Binary Constrained q-Center when every coordinate uses the same explicit binary relation R, of size L. The search maintains a set of input rows that distinguish relation patterns and a set of coordinates assigned exceptional patterns. A failed row yields a conflict on at most 2L(r+1) coordinates. Relative to a fixed feasible solution, this conflict supplies either a row that refines the current pattern classes or a previously unrecorded exceptional coordinate. Separate bounds on these two kinds of steps give the running times stated below. The proof includes relation processing, complete ordered-center output, and degenerate input conventions. Correctness and bibliographic priority are separate review questions; the latter remains unresolved.

<a id="contract"></a>
## 1. Problem and statements

Let m,n,q,L≥1 and r≥0 be integers. The input consists of an explicit matrix A∈{0,1}^{m×n} and an explicit set

\[
R=\{\rho^1,\ldots,\rho^L\}\subseteq\{0,1\}^q.
\]

The relation is common to all n coordinates. We seek an **ordered tuple** of q centers C₁,…,C_q∈{0,1}ⁿ such that

\[
(C_1[t],\ldots,C_q[t])\in R\quad(t\in[n]),\qquad
\forall i\in[m]\ \exists s_i\in[q]:\ d_H(A_i,C_{s_i})\le r. \tag{1}
\]

One center label s_i is used for the whole input row. Centers may coincide or be unused; patterns of R may be unused. Input rows may repeat. The output is either NO or **all q original ordered centers**; covering labels may also be returned.

Choose a pattern y_t∈[L] for each coordinate. Then (1) is equivalent to

\[
C_s[t]=\rho^{y_t}_s,\qquad
\forall i\ \exists s_i:\ \sum_t[A_{it}\ne\rho^{y_t}_{s_i}]\le r. \tag{2}
\]

Thus the problem is also approximation of A by a fixed template B[s,ℓ]=ρ^ℓ_s, with independently chosen row and column roles and a **separate budget r on each input row**. This description preserves the error vector, rather than replacing it by a total error budget.

**Theorem T1.** The problem admits a deterministic exact algorithm with complete output in time

\[
(q+1)^{O(L)}[L(r+1)+1]^{O(Lr)}(mn)^c. \tag{T1}
\]

**Theorem T2.** It also admits the bound

\[
2^{O(L^2+Lr\log(Lr+2))}(mn+qL)^c. \tag{T2}
\]

Here c and the hidden constants are absolute, independent of all parameters. The bounds may use different absolute constants. The input relation is explicitly charged. Binary encodings of the integers, index operations and complete output are charged as detailed in §6. The main statements use the positive domain above; §7 handles zero dimensions separately. No claim of parameter optimality or first publication is attached to these statements.

<a id="dedup"></a>
## 2. Equivalent covering labels

For a center label s define its signature across the relation patterns:

\[
d^s=(\rho^1_s,\ldots,\rho^L_s)\in\{0,1\}^L.
\]

Retain one original label per distinct signature. Let S₀ be these representatives and q₀=|S₀|≤min(q,2ᴸ). For any legal y, labels with equal signatures produce identical centers. Replacing a covering label by its representative therefore preserves every distance in (2).

Only the covering-choice list is shortened. The original L patterns and their complete q-bit contents are retained. On success, C_s[t]=ρ^{y_t}_s reconstructs every original ordered center. Pairwise signature comparison gives a deterministic O(q²L) preprocessing bound.

<a id="search"></a>
## 3. Search state and canonical candidate

A state is (W,(s_i)_{i∈W},E,ψ). Here W is an ordered list of distinct input rows, s_i∈S₀ are guessed covering labels, E⊆[n] is a set of distinct exceptional coordinates, and ψ:E→[L] fixes their patterns. Set

\[
p_\ell=(\rho^\ell_{s_i})_{i\in W},\qquad
\kappa=|\{p_\ell:\ell\in[L]\}|,
\quad a=L-1,\quad b=r(L-1).
\]

The initial state has W=E=∅ and κ=1. Admit only |W|≤a and |E|≤b. Every row step must strictly increase κ; every exception step adds one new coordinate. The following describes a finite mathematical search. Indices and all tie-breaking use fixed orders.

1. If some t∉E has input projection A[W,t] different from every p_ℓ, choose the smallest such t. If the exception budget allows, branch over the L assignments ψ(t)=ℓ and add t to E. Otherwise close this state.
2. When every t∉E has a matching code, set y_t=ψ(t) on E and choose the least matching pattern on its complement. This is the canonical complete candidate y.
3. Check every input row against every representative label. For a row i, after counting N_{ℓ,z}=|{t:y_t=ℓ,A_it=z}|, its exact distance is

   \[
   \min_{s\in S_0}\sum_{\ell=1}^L N_{\ell,1-\rho^\ell_s}. \tag{3}
   \]

   If all rows pass, output y, actual valid covering labels, and the q centers. Otherwise choose the smallest failed row i.
4. If i∈W, close this state. Otherwise form the conflict X of §4.1.
5. Row children: for each s∈S₀, add i with label s only if this strictly increases κ and the row budget allows.
6. Exception children: for each t∈X\E and ℓ∈[L], add t with ψ(t)=ℓ if the exception budget allows.

Visit the children in a fixed order. Return NO if every state closes. A failed row, an unmatched coordinate, the representatives and X are all computed from the input and current state. A feasible solution will be fixed only in the completeness proof.

<a id="c1"></a>
## 4. Conflict lemmas and correctness

### 4.1. Lemma C1: bounded conflict

For a complete candidate y and failed row i, partition coordinates by (y_t,A_it)∈[L]×{0,1}. From each class retain its first min(N_{ℓ,z},r+1) members. Their union X has size at most 2L(r+1).

For every fixed covering label s, let

\[
M(s)=\sum_\ell N_{\ell,1-\rho^\ell_s},\qquad
M_X(s)=\sum_\ell\min\{N_{\ell,1-\rho^\ell_s},r+1\}.
\]

Then M(s)≤r iff M_X(s)≤r. Indeed, when M(s)≤r each contributing count is at most r, so truncation preserves all contributing counts. When M(s)>r, a contributing count at least r+1 already witnesses failure after truncation; if every contributing count is at most r, all are preserved. This proves the equivalence for each allowed label separately. Consequently X fails for every allowed label exactly when the complete row fails.

The same label set and all L patterns are kept on X, including patterns currently assigned no coordinate. The lemma preserves the threshold at the specified r; it makes no assertion about preserving the exact optimum.

<a id="invariant"></a>
### 4.2. Fixed solution and consistent states

Suppose the instance is feasible. Fix a pattern assignment y* and one valid representative covering label s_i*∈S₀ for each row. Define

\[
U_W^*=\{t:\exists i\in W,\ A_{it}\ne\rho^{y_t^*}_{s_i^*}\}.
\]

A state is consistent with these choices when s_i=s_i* for i∈W, ψ=y*|E, and E⊆U_W*. Each true selected row has at most r errors, so

\[
|U_W^*|\le r|W|. \tag{4}
\]

If t∉E has no matching code, then t∈U_W*: otherwise its true pattern would supply the matching code. The exception child assigning y_t* is therefore consistent.

<a id="c2"></a>
### 4.3. Lemma C2: separation or a new exception

Consider a consistent state in which the canonical candidate is defined, and a failed row i with its conflict X. At least one of the following holds:

(A) The true label s_i* distinguishes two patterns having the same current code.

(B) There exists **t∈X\E** with A[W,t]≠p_{y_t*}.

**Proof.** Suppose both alternatives fail. For t∈X∩E, the canonical and true patterns are equal by the fixed assignment ψ. For t∈X\E, canonical matching gives p_{y_t}=A[W,t], while failure of (B) gives p_{y_t*}=A[W,t]. Failure of (A) says that ρ^ℓ_{s_i*} is constant on each code class. Hence in both cases

\[
\rho^{y_t}_{s_i^*}=\rho^{y_t^*}_{s_i^*}\quad(t\in X).
\]

The canonical candidate therefore has, under the valid label s_i*, at most the true row's r errors on X. This contradicts Lemma C1. ∎

If (A) holds, adding i with its true label strictly refines the code classes. If (B) holds, its coordinate belongs to U_W* and has not entered E; the exception child assigning its true pattern is consistent. The argument permits repeated codes, unused patterns, and splitting equal input columns among different true patterns.

<a id="completion"></a>
### 4.4. Progress, old rows, and completeness

Codes only acquire coordinates, so distinct codes stay distinct. Each row step increases the number of classes from an initial 1 toward at most L. Thus every path has at most a=L−1 row steps. Along a consistent path, exception steps add distinct coordinates in U_W*, giving at most b=r(L−1) such steps.

A selected row i∈W passes at a consistent state: outside E its guessed true label matches the input by construction; inside E the candidate uses true patterns. Its errors are therefore a subset of its true row errors. This justifies the old-row pruning. More generally, if an old row fails, even its stored label has more than r errors, all on fixed E; that set of guesses has no consistent extension. Actual feasible candidates are accepted before applying this pruning.

The global caps preserve a consistent child. At |W|=L−1 all code classes are already singletons, so (A) is unavailable. At |E|=r(L−1), a new true exception would contradict (4). The same argument handles an unmatched coordinate at the exception cap. Lemma C2 therefore supplies an admitted consistent child at every unsuccessful consistent state.

The initial state is consistent, and every path has length at most a+b. Thus a feasible instance has a successful search path. Every successful output satisfies the original relation and the complete distance checks; this proves soundness as well as completeness.

<a id="count"></a>
## 5. Counting all search nodes

A row edge has at most P=q₀ choices. A conflict exception edge has at most Q=2L²(r+1) choices. The L choices of an unmatched-coordinate step also fit under Q. A node reached by u row steps and v exception steps is described by a type word and the local choice number at each step. All other choices are deterministic. This description counts every prefix, including states that later close, and yields

\[
\mathcal N\le
\sum_{u=0}^{a}\sum_{v=0}^{b}\binom{u+v}{u}P^uQ^v
\le(a+1)(b+1)\binom{a+b}{a}P^aQ^b. \tag{5}
\]

The last bound uses P,Q≥1. It also applies when a=0 or b=0. In particular L=1 gives one state, while r=0 permits only row steps. There is no additional choice of an arbitrary input row or coordinate: the failed row and conflict have already fixed the candidate locations.

For r≥1, taking logarithms in (5), with binom(a+b,a)≤2^{a+b}, gives

\[
\log_2\mathcal N
=O\bigl(L\log(q_0+1)+Lr\log(Lr+2)\bigr). \tag{6}
\]

When r=0, use (5) directly to obtain at most Lq₀^{L−1} states. Separate counting of the two kinds of steps keeps the q₀ factor raised only to O(L).

<a id="cost"></a>
## 6. Complete costs and center recovery

Let H_enc be the integer-encoding length. Pairwise signature preprocessing costs O(q²L). At a search node, direct projection matching costs O(nL²); counting and testing all rows costs O(m(n+q₀L)). Extracting X uses one coordinate scan. Codes, refinement tests, and copying W,E,ψ have parameter-polynomial size plus index bits. Enumerating rejected row options and all attempted children is charged explicitly. A conservative bound is

\[
\begin{aligned}
T\le{}&O(mn+q^2L+nq)+O(H_{\rm enc})\\
&+\mathcal N(q_0+Q+1)\operatorname{poly}(L,r+1)
\,[m(n+q_0L)+nL^2+1]
\operatorname{polylog}(mn+qL+2).
\end{aligned} \tag{7}
\]

The work radius can be clipped to min(r,n) after its binary encoding is read; (7) with the original r is a valid upper bound. State and counter bit lengths then fit a fixed input polynomial and the parameter factors. A depth-first traversal stores a single state stack. No prediction, random hashing, or solution oracle is used.

For T1, use q₀≤q in (5)–(7). Fixed polynomial powers of q and L are absorbed into (q+1)^{O(L)}. For r≥1 the remaining parameter factors fit [L(r+1)+1]^{O(Lr)}; for r=0 use the row-only bound and absorb fixed powers of L into the first factor. Reading qL and outputting nq bits are therefore charged in T1 as well.

For T2, use q₀≤2ᴸ. Both q₀^{L−1} and the fixed per-node powers of q₀ fit 2^{O(L²)}. The exception contribution is 2^{O(Lr log(Lr+2))}. All remaining occurrences of the original q are in preprocessing and output. In the positive domain,

\[
nq\le(mn+qL)^2,\qquad q^2L\le(mn+qL)^2.
\]

Thus they fit a fixed polynomial, proving T2. On success each original center bit is read from the retained original tuple ρ^{y_t}; equal covering signatures are expanded to every original index. The actual labels from the complete check certify coverage. Search guesses need not coincide with these final labels.

<a id="boundary"></a>
## 7. Boundary conventions

Within the main domain, L=1 fixes all coordinate tuples, q=1 implies L≤2, and r=0 has no exception steps. For q=1 and R={0,1}, the center content remains unknown; this is the binary Closest String special case.

For an extension admitting zeros, use explicit input length N_enc and output length q(n+1), including empty-string separators. If n=0 and q≥1, return q empty centers. If n>0 and R=∅, return NO. If m=0, q≥1, n>0 and R is nonempty, repeat any one pattern at all coordinates and output all centers. If q=0 and m>0, coverage fails; if q=m=0, coverage is vacuous and a positive number of coordinates still requires the empty tuple to belong to R. These direct cases cost O(N_enc+q(n+1)+1). For instance m=0, q=L=1 and R={0} requires Ω(n) output, motivating the separate empty-domain accounting.

<a id="prior-art"></a>
## 8. Directly relevant prior work and coverage questions

The problem model already has direct precedent. The comparison below concerns the stated algorithmic guarantees and exact contracts. The available evidence has not yet supplied a complete implication from these sources to T2. This is a status of the present audit, rather than a claim that every possible reduction has been excluded.

**[C19] Common-relation subcase of Binary Constrained k-Center.** Definition1 and the problem on pp4–5 allow coordinate-dependent relations R_t; setting all of them equal gives the present model. Theorem2 gives a randomized (1+ε)-approximation in time n^{O(1)}m^{O((q/ε)⁴)} in this note's length/point notation, with success probability at least 1−2m⁻². The tuple formulation imposes neither distinct centers nor a positive usage count for each center. Relations and full output require their explicit polynomial processing costs.

For an integer threshold, ε=1/[2(r+1)] and exact validation give a one-sided randomized decision procedure: successful approximation on a YES instance has radius below r+1 and hence at most r; an accepted output is an actual certificate. After equivalent-label reduction, its guarantee still has m^{O((q₀(r+1))⁴)}. Small point counts can be treated directly. This neither gives the displayed fixed input exponent nor supplies determinism. The upper-bound comparison supplies no runtime lower bound. The 2019 version does not certify the contents of the 2026 journal version [C26].

**[P20] Fixed templates with a total editing budget.** The P-matrix definition (printed p483) uses nonempty row and column roles and total matrix error K. Writing its template size as p×b, Proposition2 (p520) gives

\[
2^{O(K\log[(K+p)(K+b)]+p\log p+b\log b)}mn,
\]

and Theorem7 (pp523–527) gives

\[
2^{O((p+b)\sqrt{K\log(p+K)}+p\log p+b\log b+b\log(b+K))}mn. \tag{8}
\]

The better orientation under simultaneous transposition is retained. Lemmas10–12 and Algorithm5 include type reductions, representative columns and an extension procedure; Algorithm5 considers candidates from Y∪Z. Lemma11 enumerates up to ℓᵇ representative choices when there are ℓ input column types. Its budget and representative arguments still use total K.

The template substitution p=q₀,b=L preserves the whole row-error vector, but replacing its local constraints by K=r or K=mr changes feasibility. For R={0}, A=I_h,r=1 is locally feasible and has total error h; rows00 and11 with r=1 have total error2=mr while one row violates the radius. Unused-role handling is an additional responsibility for this source. The read results have therefore been classified as partial overlap. A local-budget bridge, including its parameter bound and recovery, remains to be supplied.

**[K12-A] Locally bounded cluster editing.** The complete 23 May 2012 author manuscript defines a graph editing problem with at most d nonempty clique components, total K edits, and constraints deg_F(v)≤τ(v)≤t on **all** vertices (p19). Theorem6 gives a 4dt-vertex kernel in O(N³) time; Theorem7 gives 2dt vertices for deletion only. Standard d-label enumeration on the editing kernel yields O(N³)+d^{4dt}poly(N,d,t), with logged reconstruction. The graph target is a union of cliques, rather than an arbitrary fixed binary template. Direct bipartite encoding also bounds the coordinate-side accumulated error; making that side unrestricted can require t≥m. In particular the one-column all-one matrix with R={0},r=1 is feasible, while its star K₁,₄ admits no locally 1-bounded clique-editing solution. A target-preserving parameter reduction is still needed. The public manuscript's exact equivalence to the final journal typesetting remains a minor version check.

**[D13-P] Formal preview of the 2013 chapter.** The acquired pp433–434 explicitly state the same (d,t)-constrained graph model, a deterministic kernel of at most 5dt+d vertices in O((M+dt²)log N) time, and a randomized improvement arbitrarily close to 4dt with expected time O(M+dt²log N). These are visible kernelization statements; explicit vertex/budget-list reading and complete solution output carry their own costs. The remaining pp435–437, complete kernel proof and randomization details remain unavailable. The 2016 edit-optimal-cluster paper expands one section and does not replace this missing kernel material. A proof-level coverage verdict for the complete 2013 chapter remains pending.

<a id="application"></a>
## 9. A conditional root-binding corollary

For g≥2 let D_g={0,1}ᵍ\{0ᵍ,1ᵍ}. Given a task matrix A, seek f:[n]→[g] such that every demand row admits δ_i∈D_g with at most r mismatches A_it≠δ_i(f(t)). Empty roots are allowed and counted. Set q=|D_g|=2ᵍ−2 and use the g relation patterns ρʲ=(δ_j)_{δ∈D_g}. Equation(2) is exactly this distance problem. T1 yields

\[
2^{O(g^2+gr\log(gr+2))}\operatorname{poly}(mn),
\]

including relation construction and recovery of f and valid δ_i. This mathematical specialization assumes no multiplicity bound on equal task columns. An operational interpretation as dynamic rebinding additionally needs unit independent tasks, full migration eligibility, sufficient capacity, counted empty roots, a common initial state for separate demands, atomic migration before retirement, and the appropriate distance-equivalence lemma. Those operational premises are outside the generic proof.

<a id="references"></a>
## References and exact versions used

- **[C19]** Fedor V. Fomin, Petr A. Golovach, Fahad Panolan, Kirill Simonov. *Low-rank binary matrix approximation in column-sum norm*. arXiv:1904.06141v1, 12 April 2019, 18 pp. [Exact preprint](https://arxiv.org/pdf/1904.06141v1). Definition 1, p. 4; Theorem 2, p. 5.
- **[P20]** Fedor V. Fomin, Petr A. Golovach, Fahad Panolan. *Parameterized low-rank binary matrix approximation*. Data Mining and Knowledge Discovery 34:478–532 (2020). [DOI 10.1007/s10618-019-00669-5](https://doi.org/10.1007/s10618-019-00669-5); [public author-hosted journal offprint](https://fedorvf.github.io/articles/2020/2020f.pdf). Printed page locators above; the acquired PDF has two cover pages.
- **[K12-A]** Christian Komusiewicz, Johannes Uhlmann. *Cluster Editing with Locally Bounded Modifications*. Complete author manuscript dated 23 May 2012, 28 pp. [Author-group copy](https://fpt.akt.tu-berlin.de/publications/ce-bounded-degree.pdf). Journal identity: Discrete Applied Mathematics 160:2259–2270 (2012), [DOI 10.1016/j.dam.2012.05.019](https://doi.org/10.1016/j.dam.2012.05.019). Numbering in this note refers to the manuscript.
- **[D13-P]** Peter Damaschke. *Cluster Editing with Locally Bounded Modifications Revisited*. IWOCA 2013, LNCS 8288:433–437, [DOI 10.1007/978-3-642-45278-9_38](https://doi.org/10.1007/978-3-642-45278-9_38). [Acquired formal preview](https://page-one.springer.com/pdf/preview/10.1007/978-3-642-45278-9_38), pp. 433–434 only.
- **[C26]** Fomin, Golovach, Panolan, Simonov. *Low-rank binary matrix approximation in column-sum norm*. Theoretical Computer Science (2026), [DOI 10.1016/j.tcs.2026.116240](https://doi.org/10.1016/j.tcs.2026.116240), PII S030439752600469X. Complete journal text or an accepted manuscript reliably linked to this version is still requested; no mathematical result from that unacquired version is attributed here.

## Review disclosure

The starting branch proposal came from the researcher; model-assisted work completed and generalized the proof. A separate model session attempted a proof from the statement before receiving the existing proof, then performed an informed comparison. This supplies procedural separation of inputs, with the limits of a shared model family and filesystem. External human mathematical review and proof-assistant validation remain pending. The present working note is an informed exposition of that material. Its priorities, optimality and strict efficiency separation remain separate questions.

---

<a id="chinese-summary"></a>
## 中文核对摘要（一页提要）

**合同。** 输入m条长n二元串，共同显式R⊆{0,1}ᑫ、L=|R|，主体m,n,q,L≥1。每坐标选一个模式，每行在全串固定一个覆盖中心，误差≤r。允许中心重复、中心及模式闲置，输出全部原有序q中心。

**构造。** W记录带猜测覆盖标签的输入行，p_ℓ是模式在W上的码；E记录固定模式的例外坐标。E外使用匹配输入投影的最小模式。无法匹配时固定该坐标；完整检查失败时取一行，按“当前模式×输入位”各保留r+1个，得到|X|≤2L(r+1)。

**关键证明。** C1对每个允许标签分别保持半径阈值。固定一份可行解，C2保证：真实行标签细分当前同码类，或存在t∈X\E，其真实模式码与输入投影不同。E内固定真实模式、E外同码预测相同，给出反向矛盾。真实解只用于证明，失败行和冲突由状态确定。

**预算与计数。** 行步≤L−1；正确路径E包含于W的真实错配并集，例外步≤r(L−1)。全部前缀按两类步骤交错求和，q₀只取至多L−1次幂。覆盖列签名去重给q₀≤2ᴸ，得到

\[
T_1=(q+1)^{O(L)}[L(r+1)+1]^{O(Lr)}\operatorname{poly}(mn),\qquad
T_2=2^{O(L^2+Lr\log(Lr+2))}\operatorname{poly}(mn+qL).
\]

**费用与边界。** 关系读取、去重、拒绝分支枚举、状态复制、完整距离验收及nq输出均计费。空域单列真实编码和输出长度。M_r只是附条件的数学特化。

**审查重点。** 请检查§4的量词与旧行剪枝、§5全部前缀计数、§6恢复费用，并提供可能同合同覆盖T2的准确原文定理。PM2020和KU已读版本为部分重叠；D2013缺435–437页，COL2026全文待取。当前证据支持模型辅助数学复核，优先权与最优性保持待审。
