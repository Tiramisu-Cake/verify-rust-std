# Merge tool chain for maintainer — R23

Observed published fork refs via `git ls-remote origin` on 2026-10-23.
Maintainer consolidates published patches in its integration branch; this
inventory assigns no proof work and changes no profile pins.

| Fork branch | Exact published head | Scope and gating | Status |
| --- | --- | --- | --- |
| merge/actual-glue-instance-20261011 | e1ee4415b711d1b368cbfaad27bda88ed0a216e1 | R8 experimental allocation domain and checked R9/R11/R19; R20 source metadata through57812076; exporter compile repairs8dab2665/e1ee4415 | Historical R22 Cloud compile failures recorded; no new acceptance |
| merge/r22-translator-fixtures-20261023 | 65f0bb35e4f188cf8ce405a67253127173c5c3a1 | Synthetic region constructor identity=Nothing; compile profile d2640ee7 | Compile-only route fix prepared in root R23; Cloud unverified |
| merge/r22-complete-region-fixtures-20261023 | 6755ae501ab2e4bdaba5760fcd16c3c166533c76 | Includes multiline synthetic region constructor identity=Nothing; translator same blob asfc0208d4 | Prepared; not selected by current root profile |
| merge/r22-owned-nll-capture-20261023 | fc0208d4f53583d458670cd07bd0370636d4b2eb | 6b7d43fa owned NLL diagnostic capture;961d9171 decoder default; e81c4640 unavailable derived relation;5ed5617a synchronized storage;bbf919a3 exact collision equality;419ff27d/fc0208d4 region fixtures | Current root profile3fec93b5; R23 root admission delta reviewed GO49e60ed7; P1 Build692c1943 compiled all tool stages at exit0 (SOURCE_REPORTED); B2 dispatch NOT_RUN from stale compatibility source pin; no mapping/proof credit |
| merge/r22-owned-nll-borrow-sites-20261023 | 0f4e336b52441e8f341a567250adba2b200c54d1 | 26d0ee13 typed capture-stage Ref sites and loan joins,0f4e336b multiline identity fixture | Reviewed preparatory candidate, NOT adopted by current profile; emitted-stage mapping UNESTABLISHED |

| merge/r23-source-borrow-adapter-20261024 | 74cebc3bd91b3f88edae3a0dde42061712119e2b | 80576cc6 candidate, compile fixes7a1dd1c9/966c6d23/1525292d, HIR7591e3a0, alias/type layers1ad47b6c/1e31357f region reader71a7fcc4, ref reads ef925c8a, epilogue grouping736c3d98, length constant decoder9639b5b9, local declaration representatione4ce779e, exact interleaved storage equivalence4d77ebcd, kind-preserving bounded receiver raw-address8d58286d/null-payload215b4696, exact marker slots35e11eee, selected-helper unwind guard54d0ddf5, Unsize constructor resulta7b28465, generated lemma ghost contexts37d92023, exact short lifetime start9679ae38, Continue runtime continuation74cebc3b; default-off exact u64/array3 Ref–Unsize–as_mut_ptr checked resource representation; complete actual callee descriptor and same-unit checked helper cast-body equivalence; existing unwind action retained | Published exact head; P20 925fadd6 all tool stages0; source adapter all3 targets/four stages0, source negatives/rawptr/R19 matched (SOURCE_REPORTED). Whole Build FAILURE, accepted/B2/independent creditfalse. R23 ledger CLOSED: spent13685, retired715/carry0; final HANDOFF document audit GO (R23-HANDOFF-DELTA-REVIEW-20261024.json) |

Current prepared GLUE-PROFILE SHA256:
`af1ac0bd60fc52bab189be46cad9a31807cba1e7530bccf6f045285384224ebf`.
It selects 74cebc3b and reverses byte-exactly to diagnostic profile3fec93b5
and toolfc0208d4. The nineteen-entry chain keeps its paths; the cumulative
r9 patch includes the source-preserving R23 delta. Kernel, prelude, std model,
R8 premise bounds, source std and actual caller runtime remain unchanged.
The new array representation is explicit and checked only for the admitted
marked u64 array3 chain; all other array/share paths keep their refusals.

The owned-NLL stop-loss exhausted two cycles: actual b2 capture/emitted mapping
remains UNESTABLISHED. Every further R23 Build must bind the exact false
R23-CAPTURE-POLICY card. NLL metadata grants no lifetime or ownership authority.
Source helper, actual callee equivalence, caller restoration, controls and full
matrix remain Cloud-UNVERIFIED. No independent proof credit.

R23 final source case remains exact u64/array3 and selected Continue only; the checked helper and caller are verified as source claims on the published tuple, not a general slice/32 theorem or independent proof credit. Owner policy926979f3 is recorded in CHECKPOINT. Subsequent mission priority is actual general-route insertion after sort8 (first len17/window9) and bidirectional_merge/W5; no fallback R5 redo, arbitrary-length induction, or anticipatory issue56 strengthening. See R23-HANDOFF-20261024.json and R23-CLOSEOUT-20261024.json; closed R23 authorizes no further Build.
