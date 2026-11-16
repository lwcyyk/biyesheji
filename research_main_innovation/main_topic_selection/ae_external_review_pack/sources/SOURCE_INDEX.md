# External-review source index

Version ER-1, 6 November 2026. This index preserves exact source identities, local locations and prior reading scopes. The mathematical note can be read on its own; these records support follow-up checks.

## C19 — version actually used

Fedor V. Fomin, Petr A. Golovach, Fahad Panolan, Kirill Simonov. *Low-rank binary matrix approximation in column-sum norm*. arXiv1904.06141v1, 12 April 2019, 18 pages.

- Public version: https://arxiv.org/pdf/1904.06141v1 .
- Local [PDF](D:/毕业设计/research_main_innovation/main_topic_selection/ae_col2026_check/sources/column_norm2019.pdf).
- SHA256: `d208e61764cfdff2165e5acd80ecdd738bfd0fc38273dabc89dd497fe8d1eba3`.
- Structural preflight: PASS. Definition1 is on physical p4, problem and Theorem2 on p5. This round reread these definitions and the PTAS statement from the existing extraction; it did not independently reprove the entire PTAS.
- Source notation has dimension m and number of points n. The note exchanges those names to use m input rows of length n. Relations may vary by coordinate in C19; the common-relation subcase is explicit by setting them equal.

## P20 — final journal offprint acquired

Fomin, Golovach, Panolan. *Parameterized low-rank binary matrix approximation*. Data Mining and Knowledge Discovery34:478–532 (2020), DOI10.1007/s10618-019-00669-5.

- Public author-hosted source: https://fedorvf.github.io/articles/2020/2020f.pdf .
- Local [PDF](D:/毕业设计/research_main_innovation/main_topic_selection/ae_pm2020_check/sources/PM2020_author_public_offprint.pdf), 57 physical pages, of which the first two are covers. Printed article page=physical page+475 thereafter.
- SHA256: `0139e81f066a11fc4c17870cfa1f8596612b42334025efacfa0be36377d56c91`.
- Structural preflight UNAVAILABLE: wrong-pointing objects114 and132. Prior audit used two extractors and rendered critical pages; original warnings remain recorded.
- Used locations: printed p483 fixed template/nonempty roles/total K; pp518–527, Observation4/5, Lemmas10–12, Proposition2, Theorem7 and Algorithm5. The full relevant proof audit was completed in ae_pm2020_check. This round consolidates that audit and checks its implications, without claiming a new full-PDF reading.
- Current source-specific conclusion: PARTIAL_OVERLAP, with total-budget and role/parameter bridge responsibilities kept explicit.

## K12-A — complete author version acquired

Christian Komusiewicz, Johannes Uhlmann. *Cluster Editing with Locally Bounded Modifications*. Author manuscript dated23May2012, 28 pages, with a submission footer naming Discrete Applied Mathematics.

- Public author-group copy: https://fpt.akt.tu-berlin.de/publications/ce-bounded-degree.pdf .
- Journal identity: Discrete Applied Mathematics160:2259–2270 (2012), DOI10.1016/j.dam.2012.05.019.
- Local [PDF](D:/毕业设计/research_main_innovation/main_topic_selection/ae_local_edit_priority/sources/KU2012_author.pdf).
- SHA256: `ce554912f39a778d490f9c44d2a43b3620d50734d43c496596cce666c4c8683b`.
- Structural preflight PASS. Definition1 p3; constrained input p19; Rules3–8 and Lemmas5–7 pp21–25; Theorems6/7 pp23–25. The prior local-edit audit read the complete relevant kernel proofs; this round uses that completed audit.
- Exact equivalence to the final 12-page journal typesetting remains a small version check. The author-manuscript theorem numbers are used throughout the note.

## D13-P — two-page formal preview

Peter Damaschke. *Cluster Editing with Locally Bounded Modifications Revisited*. IWOCA2013, LNCS8288:433–437, DOI10.1007/978-3-642-45278-9_38.

- Publisher preview: https://page-one.springer.com/pdf/preview/10.1007/978-3-642-45278-9_38 .
- Institution record: https://research.chalmers.se/publication/187873 .
- Local [PDF](D:/毕业设计/research_main_innovation/main_topic_selection/ae_local_edit_priority/sources/DAM2013_preview.pdf), **2 pages=printed433–434**.
- SHA256: `e4ac89a7cfbeb8da7069871fdbdd700d87823c990b697896587f20406f375b12`.
- Structural preflight UNAVAILABLE: object866 outside the active xref chain. Both pages were extracted by two readers and visually checked in the prior audit; Poppler font warnings remain recorded.
- Acquired scope: model and size/time announcements on433; definitions and the beginning of Lemma1 on434. **Printed435–437 remain missing.** The note attributes visible statements only.

The public 9-page 2016 *Sufficient Conditions for Edit-Optimal Clusters* at https://www.cse.chalmers.se/~ptr/edopt.pdf is a separate source whose first-page note limits the overlap to one section of D13. The local-edit audit holds its full reading record. It does not supply the missing kernelization pages.

## C26 — requested source, no bound full text

Fomin, Golovach, Panolan, Simonov. *Low-rank binary matrix approximation in column-sum norm*. Theoretical Computer Science, 2026. DOI10.1016/j.tcs.2026.116240; PII S030439752600469X.

- Publisher: https://www.sciencedirect.com/science/article/pii/S030439752600469X .
- Obtained scope: bibliographic record and abstract only. Volume1086/article116240/Open Access label are researcher-reported metadata, recorded in the inherited COL2026_RESEARCHER_UPDATE.json.
- No full-article page count, full-PDF SHA256, theorem number or proof claim is supplied for this unacquired version. C19's identity and hash remain separate.
- Formal version or reliably associated accepted manuscript requested in SOURCE_REQUESTS.md.

## Process records

- INPUT_MANIFEST.json fixes the exact inherited theorem, review, source-audit and provenance documents. Frozen copies retain their old version identities.
- LOCAL_SOURCE_RECHECK.json records this round's directory scope and PDF identities; it did not locate a new matching complete source.
- SEAL_RECHECK.json checks already recorded proof/review commitments against current bytes; it cannot establish intellectual independence.
- DELIVERY_CHECK.json checks local links, anchors, JSON and input integrity, with no mathematical algorithm execution.

This round added no external mathematical opinion, network acquisition, source theorem coverage or implementation evidence. External reviewers can answer using the supplied public versions and exact locators, and can identify a stronger version or missing source explicitly.
