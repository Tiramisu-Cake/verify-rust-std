# Nine-body A1 linkage: review before implementation

2026-10-08. This is a separate, default-off 26.10 frontend component for the
exact nine-body actual-helper fixture captured in O24 (run `37760135524`).
It does not change Rust runtime source, generic signatures, the std functions,
the kernel, the stock `FnMut` or `MaybeUninit` specifications, or the
`select_unpredictable` safety proof. The complete verified source SHA-256 is
`8629849c2d2ddde1eeb90fadb6a151dc52e626385578f89f0d86fce842c61eb8`;
the ghost-stripped original is
`466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5`.
NORMAL/readonly export, decode, and refinement passed; this is source/MIR
calibration, not a whole-unit proof. The old A1 two-body gate pins only a
1,751-byte source prefix and therefore cannot admit this nine-body unit.

The desired narrow behavior is two typed call redirects in one exact unit:
`checked_assume_init_pointer` calls std `transmute_neo` with
`MaybeUninit<*const Element>` and redirects to the existing independently
checked `checked_transmute_neo_pointer`; the actual safe
`select_unpredictable` calls std
`MaybeUninit::<*const Element>::assume_init` and redirects to
`checked_assume_init_pointer`. Each local callee retains its existing
precondition `thread_token(tid)`, `tid == currentThread`,
`MaybeUninit::inner(input) == some(p)` and
`MaybeUninit_pointer_own<Element>(tid,input)`, and postcondition the same
thread, `result == p`, and `raw_ptr_own<Element>(tid,result)`, with
`on_unwind_ens false`. This does not give permission to dereference `p`,
prove ownership of `Element`, or generalize to a nonpointer `T`.

The O24 outer call is line 223, columns 80–93. NORMAL uses
`Move(_37)` into `_0`, normal successor 21 and shared cleanup 24;
readonly uses `Move(_26)` into `_0`, successor 10 and cleanup 13. The local
`transmute_neo` call in both modes uses `Move(_3)` into `_0`, direct
`Continue`, successor 2. The first redirect may reuse the old A1 exact
local body contract, generic, type and graph checks, but only after the new
nine-body gate. The outer redirect must leave the original cleanup action,
successor and all other cleanup predecessors untouched. `FnCallOutcome`
keeps those edges; replacing the call with an unconditional result expression
would be unsound. Both counters must equal one after translation.

The new activation requires a dedicated environment opt-in, the same root as
the separately enabled whole-unit nine-body owner gate, its successful exact
verified/original source and complete decoded unit/body hashes, and matching
ordered nine DefPaths. It then checks the two local A1 contracts, typed
locals and exact MIR graphs, the outer typed call substitution/Move/return
place/cleanup, and same source unit. Missing or partial opt-ins, changed
source/MIR/call shape, duplicate calls, wrong element type, changed cleanup,
or a six/seven/two-body source fail before body proof. The existing two-body
A1 path remains unchanged and separate.

This adds a trusted call-correspondence rule for two exact sites. The local
bodies still need to verify in this new whole unit before their summaries
can justify the actual call; the actual safe helper must then verify its
complete normal/unwind, owner, nested Drop, forget, return/leak, and safety
proof. A green call redirect alone is not a SAFE proof. Hosted acceptance
requires positive full body logs under the exact patch chain, NORMAL and
readonly typed MIR plus refinement, and targeted controls: wrong unit/source
hash, wrong typed substitution, changed local operand, duplicate/missing
call, outer Move-to-Copy, changed cleanup target, wrong return place, and
changed `some(p)`/owner/unwind contract. Each negative counts only at its
intended admission or resource obligation after valid setup. Stock ordinary
and shared-cleanup controls must show no effect when the component is off.
