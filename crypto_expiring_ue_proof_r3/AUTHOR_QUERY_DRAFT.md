# 待审核作者/外部研究者技术核对草稿

状态：**DRAFT / NOT SENT**。本轮没有发送邮件、平台消息或私有工件。下文供研究者审核后决定是否及如何对外沟通。问题以出版版本为定位；作者原意和最新版结论保持开放。

## Draft technical note

Subject: Clarification of expiry-frontier and delegation notation in the TCC 2023 TIPE construction

We are checking the construction in *Revisiting Updatable Encryption: Controlled Forward Security, Constructions and a Puncturable Perspective*, DOI 10.1007/978-3-031-48618-0_8. Our reference is the 31-page published PDF, printed pages 220–250, SHA256 `afe4c0d4577feaa581aa5c7c15c699bafbf624cc7df5baedea593e9ca7038f0b`. We have not obtained the extended ePrint version or an erratum, and would appreciate a version-specific clarification before drawing any construction-security conclusion.

### 1. Exact meaning of the expiry frontier (pp.235–236,239)

For λ=4, the preorder encoding gives a(1)=ε, a(2)=1, a(3)=11, a(4)=111. The displayed frontier definition gives

    Γ1={1,2}, Γ11={11,12,2}, Γ111={111,112,12,2}.

Under ordinary set difference on labels, both Γ1\Γ11 and Γ1\Γ111 are {1}. The displayed Enc formula would therefore have identical bodies at epoch 2 for expiry 2 and expiry 3, at a fixed key, message, tag and random tape.

Is the difference intended to operate on node labels, on covered epoch ranges, or through an additional normalization/cropping operation? If range difference is intended, could you specify the actual stored nodes and available delegation coordinates for these two examples? In an all-nodes-as-epochs preorder tree, splitting a subtree root into its children removes the root's own epoch, so this distinction affects the encoding.

Does expiry enter any other part of the full encoding, sampling, authentication or validation that is omitted from the displayed Enc tuple?

### 2. A type-complete Gen→K2→K3 example (pp.238–239)

The printed root key tuple combines k1 and h1. With root label ε and the displayed first two decryption slots, our direct substitution leaves a factor E(g0,h1)^{-1}. Should the root tuple have a separate message slot and future coordinate h1, or does the construction use another root convention?

The displayed second child is indexed a(e+2). For λ=4, the root's right child is label 2 at epoch 9, while a(3)=11. The target K2 frontier is {1,2}. Is the intended child index a(e) concatenated with 2? The same question arises for label 1, whose right child 12 is at epoch 6.

### 3. Update domains and the shift pairing (pp.239–240)

For epoch 2 and expiry 3, the printed Enc input has node set {1}. The update declaration/output use full Γ sets, and the intermediate loop uses the previous filtered set. Could you give the intended input, delegated, retained, and returned node sets?

The printed Δ3 encodes a(3)=11. If the shift ratio uses the old node's message component g1, it leaves E(g2,h0); using the delegated node's component g1g2 cancels that factor. The correctness discussion appears to use the destination node. Which binding is intended in ExPunc?

### 4. Original game and Lemma 5 (pp.231,234,242–244)

Does incoming Δ_e encode a(e) or a(e−1)? The printed token formula and the non-prefix explanation in Lemma 5 use different indices. For a universal Δ2 and challenge node 1, the former gives a matching epoch prefix. We would appreciate the intended joint-distribution argument or corrected indexing.

The shortest window τ=e* leaves no e' satisfying e*<e'≤τ in Lemma 4's guessing range. Is there a separate no-window case? Also, Fig.2 starts at e=1, while Fig.3 shows e=0; please confirm the intended correspondence and any corrected token-reachability rule.

### 5. Conditional security implication to check

Our claim is conditional. If publicly changing expiry 2 to 3 maps an epoch-2 honest encryption to the expiry-3 honest distribution, and the latter correctly updates/decrypts with Δ3,K3, then a saved challenge expiring at 2 can be processed locally after an allowed epoch-3 key exposure.

A minimal query skeleton is ordinary Enc at epoch 1 with M1=1, rotation to 2, challenge with independent uniform M0 and expiry 2, rotation to 3, exposure of K3, followed by local expiry relabeling, update and decryption. With a fixed post-challenge schedule, the update branch is independent of M0. The success probability is at least

    1 − (ε_eq+ε_corr)/2 − 1/(2|G_T|),

where ε_eq must cover the full relabeled encoding jointly with the honest state. We do not currently assert that the full author construction satisfies these premises. A corrected frontier, coordinate layout, authentication field or original-game restriction may change the applicability.

Could you point us to the exact extended version, historical revision, supplementary material or erratum that resolves these definitions?

## 供审核者填写的最小回执

1. 版本文件/公开链接、日期、页码与哈希；
2. e2/τ2 与 e2/τ3 的实际节点和坐标是否相同；
3. 从真实 Gen 到 K3 的完整槽布局和孩子标签；
4. Δ3 的目标标签及 ExPunc 配对节点；
5. expiry 元数据的完整校验和原游戏资格；
6. 这些关系是否已有公开更正或分析。

收到新资料后应新增证据版本并重新裁定 P1–P7，保留本轮来源状态和条件结论。
