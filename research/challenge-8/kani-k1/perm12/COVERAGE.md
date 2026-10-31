# PERM12 source correspondence and bounded obligations

The immutable baseline is `network::insertion_permutation_u64_n12` at source base
`e0ff82577d`; `manifest.json` records full identities. The original function item, generic
helper, macros, imports and all their dependency sources remain byte-identical.

## Trace partition and simulation

Let x be any `[u64;12]`, p any u64 probe, and b0,b1,... the Boolean results of the original
`volatile_reading_less::<u64>` invocations in their dynamic order. Neither input nor probe
has an ordering, sortedness, alphabet or equality-key restriction. Choose FF/FT/TF/TT from
(b0,b1). In the chosen adapter, initialize phase=0 and give its subsequent fresh `any::<bool>`
calls b2,b3,... in order. This selects dynamic invocations, never two fixed element pairs.

Induct on runtime steps and comparisons. The array and insertion pointers initially agree.
Both comparators volatile-read the actual `a` then `b` through the same ManuallyDrop pattern.
The selected result is equal, so each branch, value move, gap-guard restoration and subsequent
argument value agrees. Adapter phase is private, starts at 0, advances 0->1->2 and stays 2;
it neither aliases nor changes v/pre/probe. It has no indexed trace store, call bound, wrap,
assumption or termination shortcut. Every later invocation has its own nondeterministic call.
Distinct local stack objects correspond by their roles; literal pointer addresses need not agree.
Thus normal-return snapshots and full-value count expressions coincide. The post-return phase
assertion adds an obligation, never a pre-sort/path-filtering assumption.

Conversely, each fixed-prefix adapter trace is an allowed original arbitrary comparator trace:
choose the original first two results to match the case, then its remaining results to match
the adapter. Case selection is independent of x/p: every case retains all x/p choices.
For normal returns, exactly three insert_tail calls occur, each making its first comparison;
there are at least three results, hence a unique two-bit prefix and exactly one case.
An error before result two is still explored: select any extension of the observed prefix.
The wrappers do not assume phase/completion, and shared safety assertions remain enabled.
Such a short failing trace can occur in several cases; uniqueness is claimed for normal traces.

The unpartitioned baseline initializes the SAME adapter to phase=2; FIRST/SECOND are unused.
It makes fresh choices at every invocation, so its comparator trace set equals the original.
The fixture has a new closure F and generic/const instances, with extra phase/assert/cover code.
This source-level simulation does not assert identical Kani instances, solver cost or automatic
machine proof credit for an unchanged baseline that times out. Only all four accepted bounded
cases plus reviewed correspondence support coverage of the original bounded theorem's domain.
They establish neither a general insertion-sort theorem nor B2/full-CI/Mac proof credit.

## Runtime loop bounds, covers and control

At begin9, len12, the abort guard is false and outer tails are exactly 9,10,11 (three iterations).
For each tail k, the first comparison either returns immediately or moves k-1 into the gap.
The loop monotonically decrements sift, stops at v_base or on false, and moves at most k times.
There are at most k comparisons, for 9+10+11=30 total; 25 is a per-loop unwind, not a call limit.
The largest individual insertion loop has 11 bodies; shared count loops each have 12; the
movement predicate checks at most 12 positions. The guard Drop copies len1. Snapshot/array
initialization involve 12 u64 values. Unwind25 is retained on all wrappers; actual unwinding
assertions, lowered/instrumentation loops and safety must still pass G1, not inferred here.

Movement and end covers are the original predicates/messages in the shared fixture. Movement
is observed after real insertion and BEFORE corruption. Witnesses exist with distinct values:
FF leaves tails9/10 in place and may move tail11 using fresh true then false; FT moves tail10;
TF moves tail9 once; TT moves tail9 at least twice. Fresh remaining false results allow normal
completion in each case. These are existential source witnesses, not observed cover credit.
The baseline/control adapter can choose any of those traces. No constant case-bit cover is used.

Negative control performs the same real insertion, then flips v[0]'s low bit and covers reaching
the checker before calling the SAME check_permutation as positives. Full u64 equality uses
parent count_matching_values, not key equality. Choosing the arbitrary probe equal to v[0]
before its flip witnesses a count difference of one. A probe absent both before/after can also
reach the common end cover. G1 must show only the intended count assertion failing, with no
safety/OOB/phase/unwinding failures and all control covers satisfied.
Expected frozen source coordinates: network.rs:1518, assertion; phase assert:1536,
flip:1542 and post-flip/pre-checker cover:1543. Request matcher is the known lane placeholder
`This is a placeholder message`; actual G1 description/location/class are UNCONFIRMED.
A matcher mismatch stays explicit in the historical request/gate; coordinates alone do not
prove a property binding. Use bounded k1g evidence to resolve actual findings, never exit alone.
