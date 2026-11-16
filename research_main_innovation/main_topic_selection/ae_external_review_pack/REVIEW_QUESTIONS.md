# Three focused questions for an external reader

Version ER-1, 6 November 2026. Please read [THEOREM_NOTE.md](THEOREM_NOTE.md) as the self-contained mathematical submission. The questions below can be answered independently. A response may identify the exact range examined and leave the remaining questions open.

## Q1. Correctness and complete resource bound

**Question.** Does the stated deterministic search establish T1 and T2 for its complete contract, or does a particular quantifier, pruning step, unavailable choice, counting argument, or recovery cost fail?

**Shortest necessary statement.** The input is m≥1 binary rows of length n≥1 and one explicit common relation R⊆{0,1}ᑫ of size L≥1. Every output coordinate chooses a pattern of R. Each row chooses one covering label for its whole length and has at most r errors. Repeated and unused centers and unused patterns are allowed. The algorithm must output all original q ordered centers and have a fixed input-polynomial exponent.

**Proof locations and questions to check.**

|Location in the note|Specific responsibility|
|---|---|
|[§§2–3: labels and search](THEOREM_NOTE.md#dedup)|Does equivalent-label reduction preserve every original tuple and complete ordered output? Are failed rows, unmatched coordinates and canonical patterns computed from the current state?|
|[§4.1: C1](THEOREM_NOTE.md#c1)|Does capping each (current pattern,input bit) class at r+1 preserve the radius test for every allowed covering label?|
|[§4.2: consistency](THEOREM_NOTE.md#invariant)|Can a single fixed feasible y* and one fixed covering label per input row support the whole path? Does E⊆U_W* persist?|
|[§4.3: C2](THEOREM_NOTE.md#c2)|If the true label splits no code class, must X\E contain a coordinate with incorrect true projection? The proof uses fixed ψ on X∩E and matching codes only on X\E.|
|[§4.4: completion](THEOREM_NOTE.md#completion)|Can old-row pruning or a cap remove every consistent path? Are at most L−1 row steps and r(L−1) distinct exception steps sufficient?|
|[§5: node count](THEOREM_NOTE.md#count)|Does the type-word encoding count all prefixes and both forms of exception step, without a hidden m^{L} or n^{Lr} choice?|
|[§§6–7: costs and recovery](THEOREM_NOTE.md#cost)|Are rejected options, state copying, integer encodings, relation processing, all nq output bits and zero-dimensional cases fully charged? Does q₀≤2ᴸ yield the exact T2 exponent?|

**Useful answer format.** Either give a valid counterexample or the first unsupported inference, with section/equation and assumptions; or report that no defect was found in the checked range. For a repair, specify whether it changes the admissible instances, theorem conclusion or parameter bound. A checked range and confidence boundary are more useful than a general endorsement.

## Q2. Exact prior-art coverage

**Question.** Is there an identifiable theorem that, directly or by a short complete reduction, gives

\[
2^{O(L^2+Lr\log(Lr+2))}\operatorname{poly}(mn+qL)
\]

or a stronger deterministic exact guarantee under the contract of Q1?

**Shortest necessary comparison.** The relation is common and explicit, with L=|R|; the budget is a maximum over input rows, each row using one center label throughout; center and pattern usage is optional. The requested exponent of the input size is independent of L,r,q. The output includes every original ordered center. General FPT with an unspecified parameter function, an approximation algorithm, or total-edit FPT should be identified at that separate strength.

**Locations and current nearest references.** [§1, T2](THEOREM_NOTE.md#contract) gives the target; [§8](THEOREM_NOTE.md#prior-art) compares C19 Theorem2, P20 Proposition2/Theorem7 and Lemmas10–12, K12-A Theorem6, and the acquired D13 preview. The candidate proof's possible new bridge is [C2](THEOREM_NOTE.md#c2) together with [the Lr accounting and separate count](THEOREM_NOTE.md#completion).

**Useful answer format.** Please supply title/authors, exact version, theorem/lemma number, page and accessible source or reliable full-text locator. For an indirect implication, specify the variable map, both feasibility directions, parameters, deterministic/randomized status, running time after substitution, and complete output recovery. If only a special case or a weaker parameter function is covered, identify that precise range. If coverage is currently unknown to the reader, that answer can be reported without an absence claim.

**Most consequential source question.** Does COL2026, DOI10.1016/j.tcs.2026.116240, contain a result beyond the read 2019 preprint that changes this comparison? Its complete bound text is still requested. Damaschke2013 pp435–437 and KU's final-version correspondence are separate outstanding checks.

## Q3. Contribution after accounting for prior work

**Question.** Given the answer to Q2, which precise technical statement, if any, remains as a substantive contribution of this construction, and which immediate source check would most decisively change that assessment?

**Shortest necessary evidence.** The common-relation submodel and fixed-template formulation already have precedent. The candidate contribution under examination is the explicit deterministic construction and its fine parameter dependence, rather than the model name. The working proof has model-assisted support; first publication, optimality, and a strict efficiency separation from the strongest applicable public method remain unestablished.

**Locations.** [§8](THEOREM_NOTE.md#prior-art) states the exact nearest-model differences; [§9](THEOREM_NOTE.md#application) gives the conditional root-binding specialization; [C2 through §6](THEOREM_NOTE.md#c2) contains the proof that could carry an algorithmic statement. The source requests are in [SOURCE_REQUESTS.md](SOURCE_REQUESTS.md).

**Useful answer format.**

- If T2 is covered, identify whether a distinct strengthened statement, constructive recovery result or meaningful application theorem survives, with its assumptions and nearest source; presentation alone should be described at its actual value.
- If only part is covered, write the remaining result as an explicit proposition and identify the additional argument required.
- If a same-level theorem has not been located in the sources examined, identify one or two specific direct references or version checks that should be completed before assigning a provisional algorithmic contribution.

## Compact reply form

|Question|Answer|Exact location or source|Checked scope / remaining uncertainty|
|---|---|---|---|
|Q1 correctness|Defect / repair / no defect found in checked range|Section, lemma, equation; counterexample if applicable|Reader's actual scope|
|Q2 priority|Full / partial / special-case coverage / unknown|Exact theorem and version; reduction if needed|Model and parameter limitations|
|Q3 contribution|Precise residual proposition / application only / insufficient basis|Nearest result and difference|Most decisive next source or proof step|

中文交接说明：建议连同英文短稿转交以上三问。请保留读者的实际阅读范围和原回复，逐条记录错误位置、覆盖定理或明确未决项。研究者决定转交和发送；本轮只准备材料，没有联系外部读者。
