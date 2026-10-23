# Merge tool chain for maintainer — R23

Observed published fork refs via `git ls-remote origin` on 2026-10-23.
Maintainer consolidates published patches in its integration branch; this
inventory assigns no proof work and changes no profile pins.

| Fork branch | Exact published head | Scope and gating | Status |
| --- | --- | --- | --- |
| merge/actual-glue-instance-20261011 | e1ee4415b711d1b368cbfaad27bda88ed0a216e1 | R8 experimental allocation domain and checked R9/R11/R19; R20 source metadata through57812076; exporter compile repairs8dab2665/e1ee4415 | Historical R22 Cloud compile failures recorded; no new acceptance |
| merge/r22-translator-fixtures-20261023 | 65f0bb35e4f188cf8ce405a67253127173c5c3a1 | Synthetic region constructor identity=Nothing; compile profile d2640ee7 | Compile-only route fix prepared in root R23; Cloud unverified |
| merge/r22-complete-region-fixtures-20261023 | 6755ae501ab2e4bdaba5760fcd16c3c166533c76 | Includes multiline synthetic region constructor identity=Nothing; translator same blob asfc0208d4 | Prepared; not selected by current root profile |
| merge/r22-owned-nll-capture-20261023 | fc0208d4f53583d458670cd07bd0370636d4b2eb | 6b7d43fa owned NLL diagnostic capture;961d9171 decoder default; e81c4640 unavailable derived relation;5ed5617a synchronized storage;bbf919a3 exact collision equality;419ff27d/fc0208d4 region fixtures | Current root profile3fec93b5; R23 root admission delta reviewed GO49e60ed7; P1 Build692c1943 in flight, Cloud/proof outcome UNKNOWN |
| merge/r22-owned-nll-borrow-sites-20261023 | 0f4e336b52441e8f341a567250adba2b200c54d1 | 26d0ee13 typed capture-stage Ref sites and loan joins,0f4e336b multiline identity fixture | Reviewed preparatory candidate, NOT adopted by current profile; emitted-stage mapping UNESTABLISHED |

Current root GLUE-PROFILE SHA256:
`3fec93b5237d534b69eb3be59d11ea4abde3588f07c6e9437b1c09bf8533ac88`.
It selects fc0208d4, not tool-worktree HEAD0f4e336b. Capture is default-off
`VF_EXPORT_OWNED_NLL_FACTS=1`, only exact registered positive full-body original
local caller and raw local caller cases. Controls and body isolation are
ineligible. NLL metadata supplies no lifetime/ownership authority and no B2
credit; array/slice borrow and normal/unwind restoration remain OPEN.

R23 root source pin fixes leave this profile and all tool patches unchanged.
See R23-RUNNER-FIX-DESIGN and R23-ADMISSION-DESIGN for the reviewed tuple once
review completes. Earlier admissions/receipts remain historical records.
