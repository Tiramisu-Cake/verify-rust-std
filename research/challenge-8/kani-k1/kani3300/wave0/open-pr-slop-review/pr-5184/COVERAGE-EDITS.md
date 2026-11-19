# PR5184 named retention and minimal edit matrix

Head f99713506f7ba91f971f3b7359ebbe41ca373adf; all outcomes are source intentions, native NOT_RUN. T = tests/expected/uninit/recursive-delayed/. Retain all three harnesses. No removal, merge, new test framework or harness quota is justified.

## Every changed file

| File | Exact recommendation |
| --- | --- |
| `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` | KEEP byte-exact. RefCell import, active_calls field/comment, fresh per-entry set, insert/remove lifecycle, call-site error/abort and shared child-set argument are all required. No functional/compiler-comment rewrite. |
| T `recursive-delayed.rs` | KEEP code, flags and helper boundary. Optional one-line comment before recurse(...,0) as specified below. Do not delete the later tuple target/store/read. |
| T `recursive-delayed.expected` | KEEP EXACT two lines: supported-recursion diagnostic and recursive call-site source text. No stack-overflow/internal-error golden or generic failure replacement. |
| T `repeated-calls.rs` | KEEP EXACT. Different-allocation negative, same-allocation positive and full reinitialization cover distinct alias/state behavior after sequential calls. |
| T `repeated-calls.expected` | KEEP EXACT all nine lines, including the adjacent named failure triple, initialized marker/SUCCESSFUL, named failing harness and 1/1/2 summary. |

## Every Rust test helper and harness

| Symbol / source | Disposition and preserved obligation |
| --- | --- |
| `recurse(value: *mut u8, depth: u8)` / recursive-delayed.rs:8–16 | KEEP EXACT signature, inline(never), conditional store and recursive call with depth-1. Active resolved-instance recurrence triggers a call-site diagnostic. Caller depth0 avoids requiring actual runtime recursion; its analyzed body still contains the recursive edge. |
| `recursive_call_reached_from_delayed_ub` / recursive-delayed.rs:18–27 | KEEP code/flags. Preserve value:u128, recurse pointer argument and depth0, tuple cast/write and full read that activates delayed analysis. Compile-time rejection is the intended fixture result. Optional comment before the call: `// The helper's recursive call remains in the analyzed body at depth zero.` |
| `write_tuple(value: *mut (u8, u32, u64))` / repeated-calls.rs:8–13 | KEEP EXACT inline boundary, pointer signature and tuple write. One helper shared by both source controls; no duplicate helper is needed. |
| `repeated_calls_uninitialized` / repeated-calls.rs:15–22 | KEEP EXACT. Call write_tuple once for first and once for second, then read second as u128. Expected uninit FAILURE is bound to this harness's safety_check property prefix. This rejects both a permanent-visited-set error and a skip-on-seen scheme that loses the second call's argument effects. |
| `repeated_calls_initialized` / repeated-calls.rs:24–31 | KEEP EXACT. Two calls for the same allocation, then value=42 and result assertion. It requires acyclic repeated calls to compile and the complete value write to restore initialization; expected verification success complements the unsafe control. |

The recursion fixture must stay in a separate Rust file: compilation intentionally aborts before native verification. Combining its source with the acyclic controls would hide them behind the first diagnostic. The two acyclic harnesses already share their helper and compile together. Splitting them further would duplicate setup and increase invocations without a distinct obligation.

## Every current compiler helper/change

| Symbol / addition | Recommendation |
| --- | --- |
| `PointsToAnalysis::active_calls` and RefCell import | KEEP. Shared set contains currently analyzing resolved Instances, including generic arguments; the new field comment is accurate. |
| `run_points_to_analysis` | KEEP fresh empty set per public entry and pass it to run. No state leaks between separate entry analyses. |
| `PointsToAnalysis::run` | KEEP insert before solving/cursor state collection and remove before return. Do not replace with a permanent visited cache or skip analysis of a finished callee. |
| `apply_primary_terminator_effect` | KEEP membership guard on the regular nonforeign/nonintrinsic resolved callee, span_err at the call and abort_if_errors before descent. A partial graph must not produce a successful checking result. |
| `apply_regular_call_effect` | KEEP the same active-set reference passed into nested run; retain fresh argument graph and joining of return information. No summary memoization or framework change. |
| `try_resolve_instance` (unchanged context) | KEEP full monomorphized Instance identity. Do not compare only names/DefIds or replace with a lexical source-call heuristic. |

## Oracles, flags and discovery that must survive

| Component | Required behavior |
| --- | --- |
| Both source headers | Preserve Copyright/SPDX, compile-flags --edition2021, -Z ghost-state and -Z uninit-checks. No ignore/platform filter, should_panic, fail-fast or check suppression. |
| Recursion expected file | Require exact user-facing unsupported-recursion error and `recurse(value, depth - 1);`. This is a legitimate unsupported-analysis diagnostic, not an ICE baseline. The matcher does not prove a native span relationship; do not claim that without actual evidence. |
| Repeated-calls expected failure triple | Keep trailing-backslash adjacency for property prefix `repeated_calls_uninitialized.safety_check.`, FAILURE and the u128 uninit description. An unrelated compiler/backend/runtime failure cannot replace it. |
| Repeated-calls expected success and summary | Keep initialized-harness marker, SUCCESSFUL fragment, named bad-harness failure and exact 1successful/1failure/2total summary. Source has exactly these two harnesses; together these requirements distinguish both intended results. |
| Directory and companion names | Preserve standard expected-suite recursive .rs discovery and same-stem .expected pairing. No Cargo package, shell/Python driver or JSON schema framework is needed. |

Existing generic uninit baselines are not used to justify a deletion: none of these new obligations is removed. A later task may add the optional explanatory comment and use the review-only concise PR wording. New native validation, a main/fixed comparison, compiler architecture changes and additional recursion/diamond/generic test variants remain separately scoped rather than being silently added here.
