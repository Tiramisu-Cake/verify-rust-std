# Owner-preserving exact-body forget adapter: before hosted experiment

2026-10-08. This is an independent, bounded diagnostic under the resumed
26.10 phase. The pinned std `library/core/src/mem/mod.rs` contains
`pub const fn forget<T>(t: T) { let _ = ManuallyDrop::new(t); }` (body whitespace
as stored in source), and pinned `manually_drop.rs` contains the direct-field
`ManuallyDrop::new`. The experiment extracts and checks both whole std files
and exact function bodies. It does not edit std or verify its SAFE `forget`
contract. The local function is deliberately `pub unsafe fn` with the same
runtime parameter/body but its own stronger ghost contract; that unsafe
boundary is explicit and cannot be silently substituted for a SAFE call.

## Obligation, hypothesis, target and domain

The stock SAFE `forget<T>` consumes `<T>.own` and returns thread only.
Existing G1 evidence proves a thread-only public unsafe exact-body adapter
and a separate framed call lane, but does not establish an owner-preserving
callee post. The hypothesis here is that the exact `ManuallyDrop::new(t)`
move suppresses destructor execution while a checked source-level proof can
return the **same** linear `<T>.own(tid,t)` that entered. A first baseline
with only the contract may reveal whether this follows from the existing
model; if it fails, inspect the actual owned chunk and local result before
proposing any ghost unpacking. Do not assert owner retention, weaken leak
checking, assume a new owner, or modify the stock `ManuallyDrop` model.

Target for unrestricted sized generic `T` (no `Copy`, `Freeze`, purity or
nonpanic bound):

```text
req thread_token(?tid) &*& tid == currentThread &*& <T>.own(tid, t);
ens thread_token(tid) &*& <T>.own(tid, t);
on_unwind_ens false;
```

The body is the whole exact std runtime body, including its one
`ManuallyDrop::new(t)` call. No caller, helper, nominal guard, Element pointee
right, or actual SAFE redirect is included. The full normal post must retain
the input value's owner once, with the same `tid`; unwind must be impossible
under the proved callee summary. Full return, leak, dead-code, type validity,
NORMAL/readonly exporter and refinement checks remain enabled.
The local adapter is intentionally `unsafe fn` rather than std's `const fn`;
this difference remains part of the unproved SAFE-link correspondence even
though the extracted runtime body and generic input are exact.

## Source, trust and controls

Pin std `cd371e035c7e573760c43bf934d53e8118ee3e7d`, VF
`f76012fb518703b1d98e243ac4f487f16877cfcb`, nightly 2026-09-25,
the complete `mem/mod.rs` and `manually_drop.rs` SHA-256 values, exact
signature/body bytes, unchanged source pair after ghost stripping, and the
active stock `ManuallyDrop`/FnMut-related tool profile. Capture the complete
typed MIR for the local adapter in NORMAL and readonly modes: generic T,
one `ManuallyDrop::new` callee, plain move of `t`, destination/cleanup and
unwind action, and no extra runtime operation. The trusted boundary is the
compiler/source correspondence and pinned `ManuallyDrop` identity/destructor
semantics, not a new axiom or global SAFE spec. The adapter's contract must
be checked by ordinary verifier rules; a positive is not acceptance of its
use at the actual SAFE call.

Run isolated variants, each keeping the same runtime body and signature:

| Variant | First intended observation |
| --- | --- |
| owner positive | full generic normal owner/thread post, false unwind, return/leak/dead-code and refinement pass |
| false normal post | extra `false` in `ens` fails at that post after a valid body |
| duplicate owner | second `<T>.own(tid,t)` in `ens` fails at that extra post chunk |
| wrong value | an owner of a distinct ghost value is demanded and fails at that relationship or owner post, never at source setup |
| duplicate thread | second `thread_token(tid)` fails at the extra post chunk |
| dead-code sentinel | contradictory `false` precondition fails at the verifier's mandatory dead-code obligation |
| false-unwind certificate | the positive's `on_unwind_ens false` must remain in force; a source mutant that changes it to `true` is an admission rejection, not a supposed proof negative |

A separate loss-owner post (`ens thread_token(tid)`) may be used to check
leak behavior but cannot stand in for owner preservation. A pointer-
`Element`-rights overclaim is optional only if a concrete well-typed caller
setup reaches the intended extra right; no such right appears in the generic
target. Do not use a caller with a known synthetic dead unwind CFG edge as
the baseline: verify the callee and all named post controls as separate
one-function units. Require one error at the named post or dead-code span for
each negative after both MIR modes and refinement pass. Source/export/setup,
unrelated proof failures or a positive that cannot return `<T>.own` are
inconclusive for those negatives. The positive must pass before counting
negatives.

`prepare.py` emits the exact original/verified pair and certificate only on
GitHub-hosted Linux. `run.py` accepts the existing hosted profile arguments
`--tool-home`, `--schema`, `--compiler-sysroot`, `--evidence`,
`--deadline-epoch`, and optional `--s6-specs`. It leaves each full log and
complete decoded MIR in the evidence directory. Its strict summary can say
`UNSAFE_ADAPTER_COMPONENT_CANDIDATE` only after the positive and all intended
controls. The unwind mutation is rejected by the fixture target certificate
before verifier invocation; it is not counted as a failing proof obligation.
The runner has not been executed locally or on Actions at this checkpoint.

If owner retention fails, preserve the exact trace and classify this route
unproved. A subsequent checked ghost recovery or SAFE `safety_proof` variant
would be a new separately reviewed source fixture, still with the exact
runtime body, the same full contract and no owner assumption. No patch or
trusted redirect follows from this experiment. The guard/call-site team
retains responsibility for any actual SAFE linkage and shared-cleanup gate.
