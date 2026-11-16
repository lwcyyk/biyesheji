# Phase-1 target and review questions

The target is security of the fixed concrete profile in ALGORITHM_AND_GAME.md against polynomially many adaptive ordinary full-tape queries and all full-key/token queries allowed by its final closure validity. Derive an explicit polynomial DDH reduction or give a legal counterexample; do not assume a proposed simulator or a loss factor.

DDH*: x uniform in F_q*, r,z uniform in F_q. Given `(g,X=g^x,U=g^r,V)`, distinguish V=X^r from V=g^z. DDH advantage is the absolute output-probability difference. A group value encoding does not provide its logarithm. Standard DDH instead samples x in F_q; derive any conditioning correction explicitly.

First-stage questions:

1. What information suffices to answer an honest normal update when its migration scalar is hidden, including every bit of the actual ordinary tape and repeated-parent histories?
2. What joint distribution statement can be proved about all official challenge versions, adaptive current Get calls, repeated reads, local updates, normal queries and later legal keys?
3. Can complete future scalar keys be returned while preserving all previously delivered public-key vectors? Specify known/encoded/implicit quantities and every potential problematic query.
4. Establish any adaptive event decomposition on the original final-validity game. Check probability mass as well as the distribution inside an event, and prove the effect of every simulator stop. Give exact or conservative loss and sampling bounds.

The official challenge can be published at epoch 2, transition 3 kept hidden, token 4 exposed, while official versions 3/4 remain unreturned. Determine the status of K4 and then of separately publishing token 3, C3 or C4. Do not infer legality from the example text.

Allowed tools are primary-PDF reading and finite deterministic mathematical checks. Candidate cryptographic protocol implementation, contact with people/services for communication, email and native AS/RP calls remain zero. Save the first derivation, actual execution metadata and hash before seeing any project proof or verdict.

This packet itself makes no assertion that an isolated review has actually been executed.
