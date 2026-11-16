# Phase-1 input: fixed algorithm and complete game

This is a self-contained problem specification for a possible fresh-session derivation. It contains definitions, not the project's proposed reduction or verdict. No implementation, external contact, email, or native AS/RP calls are authorized. Read only the phase-1 allowlisted files.

## Parameters and scalar tapes

G=<g> is an efficiently computable prime-order group of order q≥2^κ. Fix polynomial bounds L≥2 and Q. Keys and migration scalars use F_q*, encryption/pad exponents use F_q. Uniform scalar samplers use independent bit streams; a complete tape includes every consumed word, rejected words and boundaries. Different algorithm invocations have independent tapes. Key generation/Next tapes and all official challenge-chain tapes are hidden. The group family/description is public; no secret setup information is supplied.

Registry identifiers are fresh deterministic public counters; values/metadata are independent of the challenge branch. The only imported inputs are group messages and already registered normal ids. No arbitrary ciphertext registration is available.

## Fixed algorithm UNIUE-GP23-EG-CTX1

Modified ElGamal at key x∈F_q*: P=g^x,

    E_P(w;r)=(P^r,g^r w), r∈F_q;
    D_x(u,v)=v/u^(x^{-1});
    KHC(δ,P',(u,v);a)=(u^δ (P')^a,v g^a),
    where P'=P^δ, δ∈F_q*, a∈F_q*.

1. Setup: sample x11∈F_q*, set K1=(x11), P1=(g^x11).
2. Next from epoch e: for i≤e sample independent δ_{e+1,i}∈F_q*, set x_{e+1,i}=δ_{e+1,i}x_{e,i}; sample independent x_{e+1,e+1}∈F_q*. Output full K_{e+1} and Δ_{e+1}=(δ_{e+1,1},…,δ_{e+1,e},P_{e+1,e+1}). Current public-key vector has P_{e+1,i}=P_{e,i}^{δ_i}. Entire current P vector is publicly delivered when generated; future P vectors are not precommitted or delivered.
3. Enc at epoch e, M∈G: for i≤e sample z_i,r_i∈F_q, w_i=g^{z_i}; output C_e=(((u_i,v_i))_{i≤e},Z), where (u_i,v_i)=E_{P_{e,i}}(w_i;r_i), Z=M∏w_i.
4. Upd to e+1: validate epoch/length/group elements. For i≤e sample a_i∈F_q*; for i≤e+1 sample z_i,s_i∈F_q and set w_i=g^{z_i}. For old i output KHC(δ_i,P_{e+1,i},C_i;a_i) multiplied componentwise by E_{P_{e+1,i}}(w_i;s_i). For the new coordinate output E_{P_{e+1,e+1}}(w_{e+1};s_{e+1}). Set Z'=Z∏w_i. Return all e+1 coordinates and Z'. The token is an input, not part of Upd's tape.
5. Dec at epoch e: recover each w_i=D_{x_{e,i}}(u_i,v_i), output M=Z/∏w_i. Return ⊥ for malformed inputs.

Public target-key context, nonzero key domain, multiplicative message group and the all-field encryption domain are explicit normalizations of the GP23 Figure-5 instantiation. No omitted primitive has to be inferred.

## G-SELECT-ADAPT

Initial epoch is 1. The challenger records all generated keys/tokens, normal object identities and plaintexts. A hidden uniform bit b is used for at most one accepted challenge at an adaptively selected epoch c∈{2,…,L}. Query total is at most Q, generated epoch at most L.

- EncLeak(M): actual Enc at current epoch, return C, normal id and complete Enc tape; register its message/origin.
- UpdLeak(id): accepts a registered normal object from the preceding epoch, runs actual Upd with the privately held current token, returns a new normal id, C' and the complete newly consumed Upd tape. Keep the old object. Repeated updates of the same parent use independent tapes.
- Next: generate next key/token, publicly deliver current P vector, retain the token privately, and internally update the official challenge if it exists. No official version becomes public solely because of this internal operation.
- Challenge(M0,parent): accepts once, with a preceding-epoch registered normal parent containing known M1. Return Enc_c(M0) if b=0 or Upd(Δ_c,parent) if b=1. Hide its tape. Publish the same-format opaque id and public epoch, with no branch flag. Mark it as challenge lineage, outside the normal registry.
- GetChallenge: if a challenge exists return its current cached official version and register that epoch as public. Repeated same-epoch reads return the same object. Previously returned versions can be retained; an unreturned old epoch cannot later be queried retroactively.
- CorruptKey(j): for an existing epoch return the complete scalar key vector K_j; record j. No seed/Gen tape/Next tape is part of this key object.
- CorruptToken(j): for an existing transition j≥2 return the complete token Δ_j; record j. A future-object request returns ⊥ without adding exposure. There is no arbitrary future-key oracle.
- No decryption oracle, no arbitrary ciphertext import, and no challenge re-registration under another id. Invalid format/identity queries return ⊥. A run with no accepted challenge contributes zero advantage.

Full ordinary tapes, all old normal/challenge ciphertexts, public P vectors and exposed tokens are retained. Algorithms and public representations use no shared RNG seed/state exposure or side-channel interface.

## Least fixed-point closure and final validity

K,T,C are direct exposed key epochs, direct token target epochs, and actually returned official challenge epochs. At each prefix, compute the least triple (K*,T*,C*) containing them and closed under:

    j∈K* and j∈T*       => j-1∈K*, j≥2;
    {j-1,j}⊆K*          => j∈T*;
    j-1∈C* and j∈T*     => j∈C*.

The sets include all earlier queries. A post-challenge intersection K*∩C* makes the history invalid, and monotonicity prevents later repair. Existing requested objects are still returned in the real game. At final scoring, replace the adversary's output by an independent fair bit on invalid history. This convention concerns the final score, not equality of invalid full transcripts with an early-rejection game.

For the full run define

    S=1_{accepted challenge and valid history}(1_{b'=b}-1/2),
    Adv=|E S|.

This is half the two-world output-probability difference convention. Local forward updates using known tokens are included in C* even if their intermediate official versions were never queried. Partial-coordinate information and arbitrary public computations are available to the adversary; a newly discovered attack is not excluded by adding a semantic oracle to the validity rule.

## ALL control game

G-ALL-ADAPT differs only in making every generated full token public. Challenge time and historical corruptions remain adaptive, and final validity is unchanged. It can be used as a control for derivation and closure checking.
