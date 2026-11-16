# Research Point Schema

Version: 1.0  
Artifact type: Frozen research handoff  
Purpose: 将成熟科研点保存为长期可追溯的 project source

---

## 1. Identity

### Research Point ID

格式建议：

`RP-YYYY-NNN`

示例：

`RP-2026-003`

### Title

一句话描述核心研究问题。

### Revision

例如：

`r1`

### Status

允许：

- INBOX
- EXPLORE
- EVIDENCE_SCAN
- CHALLENGE
- VALIDATION_DESIGN
- CANDIDATE
- FROZEN
- PARKED
- REJECTED

### Created

YYYY-MM-DD

### Last Updated

YYYY-MM-DD

---

## 2. Observation

描述直接观察到的现象。

禁止混入尚未验证的原因。

---

## 3. Context

说明：

- 场景；
- 系统；
- workload；
- 数据；
- 研究背景；
- 为什么会注意到这个问题。

---

## 4. Core Research Question

写成真正未知、可通过研究改变认知的问题。

避免：

> 如何优化 X？

优先：

> 在条件 A 下，变量 B 如何影响 C，其主要机制是什么？

---

## 5. Why It Matters

分开写：

### Scientific Relevance

### Practical Relevance

### Generalizability

---

## 6. Existing Knowledge

当前可靠知道的内容。

每条尽量附 evidence label。

例如：

- `[PRIMARY] ...`
- `[DATA] ...`
- `[CODE] ...`

---

## 7. Candidate Gap

明确 gap 类型：

- Problem
- Method
- Evidence
- Mechanism
- Measurement
- Dataset
- Evaluation
- Domain
- Reproducibility
- Contradiction

### Gap Statement

### Gap Confidence

- CONFIRMED
- PROBABLE
- POSSIBLE
- UNKNOWN

### Evidence for Gap

### Evidence Against Gap

---

## 8. Candidate Novelty

分别检查：

### Problem Novelty

### Method Novelty

### Mechanism Novelty

### Architecture Novelty

### Dataset Novelty

### Measurement Novelty

### Evaluation Novelty

### Setting Novelty

### Combination Novelty

没有 novelty 的类别写：

`None identified`

不要为了填满模板制造 novelty。

---

## 9. Primary Hypothesis

格式：

> Under [conditions], [variable/intervention] will lead to [observable effect] because [mechanism].

### Falsification Condition

什么结果会削弱或否定它？

---

## 10. Competing Hypotheses

### H0

Null / trivial explanation.

### H1

Primary hypothesis.

### H2

Alternative explanation.

### H3

Optional additional hypothesis.

---

## 11. Supporting Evidence

列出支持当前科研点的证据。

每条标记：

- source；
- evidence type；
- strength；
- limitation。

---

## 12. Counter-evidence

必须保留。

包括：

- 与 hypothesis 不一致的数据；
- 已有 competing work；
- reviewer-style objection；
- negative result；
- conflicting literature。

---

## 13. Critical Unknowns

按重要性列出仍未知问题。

优先写：

> 哪个 unknown 最可能让整个科研点失效？

---

## 14. Validation Strategy

说明如何区分 competing hypotheses。

### Minimum Viable Experiment

### Key Baselines

### Key Metrics

### Required Data

### Required Infrastructure

---

## 15. Failure Conditions

明确以下问题：

### Scientific Failure

什么结果说明核心 hypothesis 不成立？

### Novelty Failure

发现什么 prior work 会让 novelty 消失？

### Practical Failure

什么结果说明效果没有实际意义？

### Feasibility Failure

什么资源限制会让研究无法继续？

---

## 16. Risks and Limitations

至少考虑：

- confounder；
- dataset bias；
- measurement artifact；
- implementation dependency；
- generalization；
- reproducibility；
- resource constraints。

---

## 17. Related Research Points

### Parent

### Children

### Overlap

### Competing

### Depends On

---

## 18. Key References

仅保留真正影响 Research Point 的核心来源。

格式：

- `[PRIMARY]`
- `[REVIEW]`
- `[PREPRINT]`
- `[CODE]`
- `[DATA]`

---

## 19. Decision Log

记录关键变化。

示例：

### r1

Initial formulation.

### r2

Prior work X weakened architecture novelty; research question narrowed to workload-specific mechanism.

---

## 20. Next Best Action

只写当前信息增益最高的下一步。

---

# Blank Research Point Card

```markdown
# RP-YYYY-NNN — <Title>

Revision:
Status:
Created:
Last Updated:

## Observation

## Context

## Core Research Question

## Why It Matters

### Scientific Relevance

### Practical Relevance

### Generalizability

## Existing Knowledge

## Candidate Gap

Type:

Gap Statement:

Gap Confidence:

Evidence for Gap:

Evidence Against Gap:

## Candidate Novelty

Problem Novelty:

Method Novelty:

Mechanism Novelty:

Architecture Novelty:

Dataset Novelty:

Measurement Novelty:

Evaluation Novelty:

Setting Novelty:

Combination Novelty:

## Primary Hypothesis

Falsification Condition:

## Competing Hypotheses

### H0

### H1

### H2

## Supporting Evidence

## Counter-evidence

## Critical Unknowns

## Validation Strategy

### Minimum Viable Experiment

### Key Baselines

### Key Metrics

### Required Data

### Required Infrastructure

## Failure Conditions

### Scientific Failure

### Novelty Failure

### Practical Failure

### Feasibility Failure

## Risks and Limitations

## Related Research Points

Parent:

Children:

Overlap:

Competing:

Depends On:

## Key References

## Decision Log

## Next Best Action
```
