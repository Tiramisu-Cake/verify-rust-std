# O26 independent diagnostics and wrapper rebase — Cloud-only card

Lane `o26-independent-tests` preserves the frozen O26 production twenty-patch
profile, the two reviewed refresh patches, and the actual std
`select_unpredictable` source. The baseline source pair, complete normal and
readonly typed MIR, refinement, ten historical Marshal fingerprints and full
production proof are rerun because the following TEST comparisons require
fresh same-Build evidence. No new verifier rule or proof acceptance follows
from the TEST and PROBE results.

The new source-only hypothesis is that the selector's current two
`MaybeUninit<*Element>` wrapper values need their indexed empty pointer-value
ownership re-established after the prior wrappers are consumed. The candidate
inserts exactly two ghost blocks and preserves ghost-stripped runtime source.
Its exact domain is the actual outer helper specialized to
`T = *const Element`, with unrestricted implicit-Sized `Element`; it is not a
generic helper proof. The exact outer pre is `thread_token(t)` and
`t == currentThread`; its full normal post is `thread_token(t)`,
`result as pointer == (if condition { true_val as pointer } else {
false_val as pointer })`, and `raw_ptr_own<Element>(t,result)`.
Its full unwind post is **false** in this pointer-only specialization. All
internal storage/guard resources must discharge under normal return/leak checks;
no resource is hidden by this post. The generic nested Drop has its separate
unchanged normal/unwind optional-cell ownership contract. These targets are
not claimed by the source-only capture.
See [wrapper candidate](../../overnight-assume-actual/CLOUD-WRAPPER-REBASE-CARD.md)
for the precise chunks and insertion points.

Expected wrapper capture: a new verified source hash, the same original source
hash, exact ghost-strip identity, complete normal/readonly/refinement capture,
an intended old-certificate fingerprint refusal, ten independently hashed
Marshal files, eight canonical body snapshots byte-identical and only the
outer body 7 plus unit snapshot different. These new identities are observed
from Cloud; no value is assumed in advance. An unchanged outer body/unit,
changed other body, missing resource or setup failure is `INCONCLUSIVE`, not a
proof-negative. A later refreshed certificate and actual ownership proof need
a separate within-phase decision after inspecting the new full graph.

The isolated nested-order TEST permits only its reviewed translator-only
permutation and asks whether the generic nested Drop is reached before the
outer body. The print-only sort4 AST PROBE permits only its reviewed scope
trace; its off/on verifier runs must retain the same reserved first-call
refusal. Neither result admits a frontend semantic change. The coordination
regression exercises the real orchestration functions with synthetic API
responses in a private Cloud workspace and must pass all ten cases. All three
keep independent logs, source/profile hashes and helper exit codes. An
ambiguous AST scope is recorded as such and does not imply proof acceptance.

The compound audit requires each requested helper's exact diagnostic gate,
the canonical source/MIR/profile checks and unchanged production proof stage.
It always sets `verification_accepted=false` for this lane. The archive and
separate text logs must publish even when a helper is inconclusive. Inspect
the full evidence before a new source pin or profile decision. The client
must also preserve one global Build reservation, the distinct phase ledger,
deadline and remaining budget; the old migration account stays closed.
