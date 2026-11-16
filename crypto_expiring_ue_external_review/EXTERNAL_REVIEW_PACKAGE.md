# EE-R 外部版本核对材料包

日期：2026-11-06。版本：EXT-REVIEW-1。状态：**DRAFT_FOR_RESEARCHER_REVIEW / NOT_SENT**。

本包只询问 Q1–Q3。正式收件人和最终正文尚待研究者明确授权；公开联系方式只作为候选记录，见 `SOURCE_AND_RESPONSE_REGISTER.json`。本轮没有发送邮件、平台消息或附件。

## 一页英文询问正文

以下标记之间为可独立复制的英文正文，共 288 词，按一页询问长度组织。三个问题对应原文页码，公式附件单独提供，便于正文独立审核。

<!-- EMAIL_BODY_BEGIN -->
Subject: Version and notation clarification for the TCC 2023 expiry-aware TIPE construction

Dear Dr Slamanig and Dr Striecks,

We are checking the expiry-aware construction in your TCC 2023 paper, “Revisiting Updatable Encryption: Controlled Forward Security, Constructions and a Puncturable Perspective” (DOI: 10.1007/978-3-031-48618-0_8). Our reference is the published chapter, pages 220–250. We also located the conference slides linked from your publication page.

Could you direct us to the complete version corresponding to this construction, its revision date, and any relevant erratum, and clarify three points?

1. **Expiry binding (pp.236,239).** For epoch 2 and expiry 2 versus 3, is the displayed frontier difference an ordinary difference of node labels or a range/cropping operation? What nodes and delegation coordinates are actually stored? Does expiry affect other metadata, sampling, authentication or validation in the full ciphertext?

2. **Complete correctness path (pp.238–240).** Could you provide a type-complete Gen→K2→K3 and ExPunc example, identifying the root message/future-coordinate slots, child labels, token encoding, and the delegated node used in the shift pairing? Our attachment identifies the precise printed indices and variable bindings we would like to check.

3. **Original game and proof (pp.231,234,242–244).** Which version specifies token reachability, challenge eligibility and Lemma 5's non-prefix condition? In particular, how are incoming tokens indexed and the shortest expiry window handled? We would like to assess the attached query skeleton in the intended original game.

The attached implication is conditional: if public expiry relabeling gives a valid later-expiry distribution and the corresponding update/decryption is correct, a permitted post-expiry key exposure yields the stated distinguishing bound. We currently retain this conditional statement; applicability to the complete construction awaits these specifications.

Any version-specific clarification, corrected formula, or reference to an existing explanation would be very helpful. Thank you for your time.
<!-- EMAIL_BODY_END -->

## 最小公式附件：版本固定

**Reference A — published chapter.** Daniel Slamanig and Christoph Striecks, TCC 2023, printed pp.220–250, 31 physical PDF pages. [Publisher DOI](https://doi.org/10.1007/978-3-031-48618-0_8)；[publisher PDF](https://link.springer.com/content/pdf/10.1007/978-3-031-48618-0_8.pdf)。

SHA256:

```text
afe4c0d4577feaa581aa5c7c15c699bafbf624cc7df5baedea593e9ca7038f0b
```

**Reference B — newly obtained conference slides.** Same paper title and authors; title page names Roman Langrehr as presenter, TCC, November 30, 2023. 42 physical PDF pages including overlays; the TIPE summary is physical page 34, printed slide 7. [IACR-hosted slides](https://iacr.org/submit/files/slides/2023/tcc/tcc2023/30/slides.pdf)。

SHA256:

```text
d3b8183e76206215d33a202345cc17d181bbf3bd922a302a236a34937619f618
```

Reference B gives interfaces and intended expiry-sensitive correctness, without the complete DSG algorithms, tree-frontier encoding or formal game needed below. It is supplementary conference material, not an author response or a corrected complete construction. ePrint's currently retrieved record reports the last of four revisions as 2023-10-03; the corresponding PDF and historical-version page remain inaccessible in this retrieval round.

### Q1 — Encoding, ranges and complete ciphertext (P1–P3)

Reference A pp.235–236 defines the epoch encoding; p239 supplies Enc (physical PDF pages 16–17,20). Write a(e) for the paper's t(e), reserving t for the ciphertext tag. At λ=4:

```text
a(1)=ε, a(2)=1, a(3)=11, a(4)=111.
Γw={w} ∪ {v2 : v1 is a prefix of w}.
Γ1={1,2}; Γ11={11,12,2}; Γ111={111,112,12,2}.
I(e,τ)=Γa(e) \ Γa(τ+1).
I(2,2)=I(2,3)={1}                 [ordinary label-set difference].
```

For the retained node 1, the displayed body has the form

```text
(Sg0, g1, g2,…,gλ, gλ+1^t),   Z=μ2^s M,   μe=m(ke).
```

At fixed key, tag, message and tape, this displayed body is identical for the two expiry values. This observation concerns the printed body. It leaves the full metadata/validation format open.

An alternative range reading gives different time-point sets: the coverage of Γ1 starts at epoch 2, that of Γ11 at 3, and that of Γ111 at 4. Their range differences are {2} and {2,3}. Converting those ranges to stored nodes and usable delegation coordinates needs an explicit rule. With internal nodes themselves representing epochs, replacing a subtree root by its children removes the root epoch.

**Requested answer:** For both cases, list all actual ciphertext fields and stored coordinates; specify whether expiry changes sampling, binding, normalization, validation or authentication. Please identify the complete version and relevant pages. This determines P1 (public relabeling), P2 (body equality) and P3 (valid full relabeled distribution).

### Q2 — Gen→K2→K3 and ExPunc (P4–P5)

Reference A pp.238–240 (physical PDF pages 19–21). The following are checks of literal printed formulas, subject to confirmation of their intended slots and indices. Pairings E are written in the normalized order E(G,H); this is a notational reordering of the displayed pairing expressions, subject to confirmation of the intended pairing convention.

1. **Root slots.** For a(1)=ε, the first two printed key slots are h0 and k1h1. Substituting the displayed root ciphertext into the displayed decryption ratio gives

   ```text
   μ1^s M / E(Sg0,k1h1) = M / E(g0,h1).
   ```

   This uses the stated orthogonality and projectiveness. A separate root-message slot would change the calculation; please specify the intended root layout.

2. **Child labels.** For the stated preorder encoding,

   ```text
   epoch(u1)=epoch(u)+1;
   epoch(u2)=epoch(u)+2^(λ−|u|−1).
   ```

   At λ=4 the root's children are labels 1 and 2, epochs 2 and 9. The printed second-child index a(e+2) instead names label 11 at e=1, while the target K2 frontier requires {1,2}. The same notation appears in ciphertext delegation. Please confirm the intended indices.

3. **Update domains and pairing.** At epoch 2, expiry 3, the displayed Enc node set is {1}. The ExPunc input/output use full Γ sets while an intermediate loop uses the old filtered set. For

   ```text
   X0=Sg0, Xmsg=g1, Xfuture,2=g2,
   Δ3=(h0,δ3 h1 h2,μ3),
   ```

   the pairing ratio with the old message coordinate leaves

   ```text
   E(Sg0,δ3h1h2)/E(g1,h0)=m(δ3)^s E(g2,h0).
   ```

   Using the delegated node 11 gives denominator E(g1g2,h0), yielding m(δ3)^s. The correctness discussion appears to use this destination node. Please specify the actual binding, all retained/returned nodes and their parent sources.

**Requested answer:** Give the total key/ciphertext types and an honest trace from Gen through K3, including the two expiry cases. State the correctness theorem and any relevant failure bound. These details determine P4 (legal update) and P5 (decryption).

### Q3 — Original eligibility, reachability and Lemma 5 (P6–P7)

Reference A pp.231,234,242–244 (physical PDF pages 12,15,23–25). The printed Δe formula uses a(e); Lemma 5's explanation uses the preceding epoch for incoming Δe*. With e*=2, a universal incoming Δ2 and initial challenge node 1 share the same epoch prefix under the displayed formula. Please identify the intended indexing and the joint parameter-hiding argument.

The shortest window τ=e* leaves no e' satisfying e*<e'≤τ in the displayed Lemma 4 guess. Fig.2 starts at e=1, whereas Fig.3 shows e=0. Please confirm the complete-version correspondence and the token-reachable challenge closure used for validity.

**Requested answer:** Assess the following skeleton in the intended original game, rather than only the printed validity predicates. Our EE-R-PA1 research game fixes a single chain, hides challenge-chain tapes, permits only one key corruption strictly after expiry, and keeps all tokens public. It admits this skeleton. The corresponding Fig.2 skeleton can replace EncLeak with Enc' and retrieve the required tokens explicitly; applicability to the calibrated author game remains open.

## Conditional implication and probability bound

Assume all of the following for a complete, version-fixed construction:

- P1–P3: an efficient public relabeling R maps expiry 2 to a valid expiry-3 ciphertext distribution at epoch 2. The distribution error ε_eq covers the ciphertext **jointly with the honest state, relevant history, Δ3 and K3**; pointwise equality at each fixed state is sufficient.
- P4–P5: this valid expiry-3 ciphertext updates and decrypts under Δ3,K3 with failure probability at most ε_corr.
- P6/P7: the query sequence meets the relevant game's eligibility rules. The group message space admits uniform sampling with equal-length encoding; the post-challenge schedule and local update coins are independent of M0.

The minimal sequence is:

```text
1. At epoch 1: EncLeak(M1=1,expiry=2), obtaining an ordinary parent.
2. Next to epoch 2; choose M0 uniformly in GT.
3. Challenge(M0,parent), save C* (recorded expiry stays 2).
4. Next to epoch 3; expose K3 under the post-expiry rule.
5. Locally compute D=Upd(Δ3,R(C*)), W=Dec(K3,D).
6. Guess 0 iff W=M0, otherwise guess 1.
```

In the fresh branch, Pr[W=M0]≥1−ε_eq−ε_corr. In the updated-parent branch, W is independent of uniform M0, so Pr[W=M0]≤1/|GT|. Consequently:

```text
Pr[correct guess] ≥ 1−(ε_eq+ε_corr)/2−1/(2|GT|).
Adv := |Pr[correct guess]−1/2|
    ≥ max(0, 1/2−(ε_eq+ε_corr)/2−1/(2|GT|)).
```

This implication uses no exposed ordinary tapes. Body equality alone leaves ε_eq for the full actual encoding unassigned; uncalibrated correctness leaves ε_corr unassigned. The conclusion continues to be conditional. A literal notation inconsistency, a simulator failure, and a concrete construction attack have separate proof obligations.

## 内部审核与回应登记

当前 P6 为 CONFIRMED；P2 仅在出版正文的标签差解释下为 CONFIRMED；完整作者构造的 P1–P5/P7 继续 SOURCE_UNRESOLVED。新增幻灯片支持预期功能的来源说明，未补齐这些前提。

外部回应最小格式：版本文件/链接、日期和页码；Q1 两个完整密文；Q2 类型完整轨迹及正确性；Q3 原游戏和 Lemma 5 的索引/闭包。作者解释、独立研究者意见和研究者自行修订须分别标注。沟通草稿在研究者批准收件人及最终正文后才可发送。
