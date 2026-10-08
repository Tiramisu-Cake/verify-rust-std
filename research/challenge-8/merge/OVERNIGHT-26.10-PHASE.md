# OVERNIGHT-MERGE-26.10

Authorized by owner on 2026-10-08, until 09:30 Moscow (06:30 UTC).
Own branch `overnight/merge-26.10`, entry b0af5613e18699c877ef9b7a7ea27b00c7827dda.
New independent budget: 21600 summed GitHub-hosted job seconds, including all
setup, failures, cancelled jobs and artifact steps. Historical603/1800 (1197
remaining) is preserved separately and does not constrain this phase.

Scope: exact wrapping support, complete pointer/index trace bridge, unchanged
actual merge_up/merge_down/bidirectional_merge bodies, memory/copy/ownership,
callback normal/unwind resources, and conditional G2/A/B composition. Necessary
frontend/spec/model/exporter/decoder/refiner changes are authorized after a short
design, trust review and matrix. Each semantic dependency is separately pinned.
Historical design-only/CI0/STOP requirements are superseded in this scope. Kernel
checks, leak/validity/unwind/dead-code/refinement remain enabled. No runtime std
changes, main/upstream changes, other agent worktree writes, or external messages.

## Dependency plan

1. W1: exact 0/1 wrapping pointer profile, independently tested. Preserve the
   pointer constructor's provenance AND metadata; modular address only. No memory
   resources in the contract. Link method lowering to actual wrappers and
   arith_offset source; reject unsupported counts at the primitive precondition.
2. W2: checked terminal/reentry and full signed-index G2 pointer trace. Ordinary
   add/sub stay distinct. Positive stride only for index/address injectivity;
   ZST wrapping is required, ZST functional guard bridge remains explicitly open.
3. M2: source-linked merge_up, then merge_down, with initialized source cells,
   writable scratch, callback effects and both normal/unwind posts. Prove callee
   bodies before summaries. Safety permits arbitrary comparator normal answers.
4. M3: paired resource/trace invariant and actual bidirectional loop, final odd
   copy and panic guard. Compose occurrence/stable ordering only under the
   separate A/B premises (finite SWO, immutable keys, faithful normal answers).
5. Combined regressions and minimized trust extension; independent actual
   network obligations may be used if a main dependency is temporarily blocked.

## W1 design and trust boundary (before implementation)

Base: official VeriFast26.10 f76012fb518703b1d98e243ac4f487f16877cfcb,
nightly-2026-09-25; stock archive/schema/exporter/refiner pins from M1 unchanged.
New explicit profile `experimental-merge-wrapping-01-v1`. Only translator dispatch
and Rust primitive specs are initially changed; no kernel, pointer constructor,
ownership, alias model, exporter or refinement changes. Ordinary ptr_add_ is
nonmodular and must not implement wrapping.

M=usize::MAX+1; s=size_of(T). Valid pointer addresses lie in[0,M). For count c
in{0,1} and0<=s<M, plus uses x=A+c*s, result address is x-M if x>=M else x;
minus uses x=A-c*s, result is x+M if x<0 else x. Signed arith_offset/wrapping_offset
admit only[-1,1] and use the corresponding branch. These are exact modulo M in
this bounded interval. Reconstruct `pointer_ctor(P,address,metadata)` unchanged.
This handles numerical wrap, allocation escape and reentry without allocation
premises. General usize high-bit cast and isize::MIN wrapping_neg are explicitly
unsupported, not approximated. Actual merge uses only bool casts and literal1.
Wrappers' count casts/negation are exact in the admitted domain; arith_offset's
two's-complement address semantics is a TRUSTED primitive specification justified
against pinned std source, not a proved Rust body or an ownership theorem.

Review: piecewise arithmetic avoids relying on uninterpreted truncate helpers;
preserves complete pointer metadata; cannot produce points_to, allocation facts
or ownership. Out-of-allocation values are arithmetic values only. Pointer Rust
comparison uses addresses (and metadata where appropriate), whereas internal
constructor equality retains provenance. A same-address foreign chunk must not
match the source-derived pointer. Primitive spec trust and checked lemma bodies
will be reported separately. Thin Sized merge is the admitted application.

## W1 acceptance matrix

Positive: count0 identity; plus/minus1 with and without numerical wrap; escape at
logical-1 and exact reentry; terminal cursor/index association; metadata and
provenance retention; independent frame preservation; size0 identity (symbolic
ZST premise, concrete compiler-backed ZST remains separate); read base after
reentry with an existing initialized cell. Test const/mut wrappers and signed
wrapping_offset/arith_offset independently.

Negatives: unsupported count2 and signed count outside[-1,1] at primitive req;
false provenance/address/metadata result at intended assertion; out-of-bounds
read at-1 at actual read permission obligation; foreign same-address resource
does not transfer to wrapped P. Setup/unsupported unrelated errors are never
intended negatives. Full export/decode/refinement/source integrity and own-body
return/leak/dead-code gates stay mandatory; exact coordinates recorded per card.

Regression: stock G2/A/B plus nine projections and existing intended controls,
separate Rust/C/C++ baselines, ordinary potentially-panicking call normal/unwind,
false unwind post and unreachable body checks. Combined matrix before accepting
the new profile. A partial diagnostic remains unaccepted until its missing gates
are run. After evidence-driven fixes, proceed without routine owner approval.

One active workflow from this agent, workflow_dispatch only, GitHub-hosted only.
Reserve the end of the window for completing runs, downloading evidence and
reporting. Historical night cutoff was06:25UTC. Owner renewed on2026-10-08 until14:30MSK
(11:30UTC), with a7200 summed hosted-job-seconds continuation cap. Historical
night3971/21600 and old603/1800 stay separate. Stop new dispatches early enough
to finish jobs/evidence/report by the renewed deadline; debit every job.
