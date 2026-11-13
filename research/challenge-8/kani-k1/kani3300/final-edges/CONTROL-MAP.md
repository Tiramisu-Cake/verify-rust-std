# E1 controls

CONTROL-MAP.json pins all 17 singleton Rust/expected inputs and roots. Goldens are substring
smoke expectations, not an exact failure oracle. CI acceptance additionally requires the full
property inventory and semantic binding described in CI-REQUEST.md. No expectation was learned
from CI; no fixture has run under a compiler or verifier here.

| New control family | Legal | Hole/unsupported | Required discrimination |
|---|---|---|---|
| union-constant, union-variable | each legal root has zero failures, consume reads 0 | each hole root has only consume union-field uninit failure | actual Constant versus Copy; ordinary Byte, not MU; allocation mask [true] versus [false] |
| raw-field | value field read succeeds at offset4 | neighbor tail offset8 and padding byte1 each fail separately | same valid storage/alias/store; no initialized &Pair, no whole-parent setter |
| immutable-subrange | raw_eq requires zero failures | only left actual hole relative byte1, right byte checks succeed | allocation origin offset Some(1), extent2/size3; no hidden whole-allocation qualifying origin |
| immutable-relocation | both byte checks must pass | only left hole slot1; initialized pointer slot0 and right must pass | relocation slot0 in both; no equality assertion on pointer allocation identity; no invalid &u8 |
| immutable-static | raw_eq &SOURCE requires zero failures | only left hole byte1; right succeeds | actual GlobalAlloc::Static; determine which existing static path runs; do not assume M1 admission |
| dst-by-value | initialized input gets exact unsized-transfer Unsupported | hole input gets same exact boundary, before its payload read | actual by-value [MU<u8>] / Move(Deref), not Box/fat-pointer argument; compile errors/earlier Unsupported do not qualify |
| dst-by-reference | slice slot1 reads 0 | only slot1 payload read fails | by-reference sized argument remains legal with exact same storage shapes |

Reuse unchanged: maybe-uninit-initialized, maybe-uninit-transfers, maybe-uninit-reset-alias, maybe-uninit-reset-zst,
maybe-uninit-call-pairing, maybe-uninit-call-move, maybe-uninit-typed-* data/padding controls;
promoted-allocations/direct-{legal,left-hole,right-hole}, immutable-masks/{zero-bytes-legal,
zero-byte-hole,copy-hole,empty}; access-static-padding (independent prior static/padding path).
Actual exact existing directory names are checked in STATIC-CHECKS.json.

Reuse eight strong JSON oracles unchanged: p1, ordinary, pfc, lawful-modifies, p2,
postcondition-hole, frame, clause. CC1 real cycle Unsupported and nonrecursive/SimpleCheck
companions, CC2 ordinary argument slots, CC3 upvar layouts, M1 masks/S3 remain mandatory.
W15 files, manifest/property IDs and checker strength are unchanged.

A legal immutable falseFAIL means limitation / release HELD pending coordinator disposition,
not expected UB. A hole root with the same unqualified initialized-byte failures is unqualified.
No new immutable seed/domain or mutable-copy reseed is proposed. This is source preparation;
no B1/B2 or independent proof credit is claimed.
