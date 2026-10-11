# Fresh raw review: unstable public-guard build `00e90a4b`

## Collector, artifact integrity, and stage profiles

Reviewed Cloud Build `00e90a4b-b7ed-4b92-8b07-bbf168dbc820`, proof/infra SHA
`4871e8a6b47d9f863d42df802233496a051a7242`, lane
`o26-sort4-c1-current-recovery`. Collector summary: process exit 0,
`diagnostic_complete=true`, `evidence_complete=true`, and
`verification_accepted=false`. Archive SHA-256
`2c3e5c6870d51c605221f875abf87d7d21e7ef814b53614d2f84fefde7782760` matches
receipt. All 748 `files-sha256.json` entries were independently checked: 748
match, none missing. All 478 indexed text chunks are present; index SHA is
`6004ed02701a0e73caf3935924151d878d1ac294a8195a7b8ce09e8339d2763a`.

The tool is still experimental and unaccepted. Pins: VeriFast HEAD
`f76012fb518703b1d98e243ac4f487f16877cfcb`; kernel
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`; parser
`7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2`; RSSpec
`d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf`; refiner
`b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28`; MIR
exporter `b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796`.
The public-guard fixtures run **before** the slice binding, on translator
`66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124` and
console `b73d563b88727846581ab33d425a2fd57ff736fa52e580addde930da33bb01fc`.
Canonical components and the first helper prefix are also pre-binding. The
pointer consumer controls run **after** binding, on translator
`21ca026ae3279ef7da9a8a482b5355fab4c39250dec553854509b1f8923f52c4` and
console `6d20c76fbd49c9ad2700ada5bf9e4ab5c218f82c5a32727daf2a3d3fb86b0ae9`.
The actual helper prefix was checked under both profiles. These are staged
diagnostics, not a single combined public-caller-to-consumer proof. No fresh
model, native C1, or native C4 prerequisite gates ran in this Build.

Source pins include `[T]::as_mut_ptr` implementation SHA
`e3a45814fc07497d6e85d182d6b30782711e4b77752fa817988ec6da12e2cb6f`, SmallSort
SHA `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`, the
unstable public entry SHA `23fa044fde8d3542f5f298654923ed2426930373259e6f71670c75b80501cf9a`,
and `SizedTypeProperties` SHA
`b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2`.

## Pointer and helper case results

Before binding, both canonical native-reference fixtures pass source admission,
paired normal/read-only MIR, refinement, AST and verifier: 53 statements each,
all 55 registered physical IDs execute, full normal/unwind posts, lifetime,
free and leak checks. After binding, `consumer-positive` passes the same gates
with 63 statements, all 65 registered IDs executed, full posts and cleanup /
leak check. Wrong-pointer, missing-raw-rights, and forbidden
`MaybeUninit<T>`-to-initialized-`T` controls fail at their exact intended
assertions after paired support/refinement. The default-off and source/phase
mutation controls refuse before proof. This validates the isolated
source-versioned consumer rule only; it grants no authority to the actual
caller.

Both unfiltered `small_sort_general_with_scratch` prefixes pass paired
normal/read-only export and refinement, and fail at their first VC in
`verified/lib.rs(20,24-32)`: `Potential arithmetic overflow. (Cannot prove
(ptr_len(fn_outcome_result(outcome)) + 16) <= 18446744073709551615.)` This maps
to `library/core/src/slice/sort/shared/smallsort.rs:230`,
`scratch.len() < len + 16`, after `len = v.len()` at line 225. It precedes
both pointer calls. The verified/original source digests are
`f7bfcb41fa6fd5784649fab8d5ee06de890f019391e7f6b7ddd67887e713ee64` /
`7a3124bfa59fd207a1c6b1a583b10c1e9b8828b2336338a9a65c8a80c17dd1a7`;
normal/read-only full MIR roots are
`9929cb2bb0134d810828639594792696ecc21b6033c81d1a3062e3ac06ec132a` /
`27c206c36f0c5ff08c1d233b4eb54bb2d3a2a937126a7018c13cf39c28f67a54`.
The AST root is `small_sort_general_with_scratch<T,F>` at
`verified/lib.rs(10,1-57,2)`, with `v`, `scratch`, `is_less`, three lifetime
parameters, one function root, and 14 distinct `VarPat` binders (17
occurrences). The caller, callable summary and actual sort4 proof remain
unproved; there is no abort-alias or pointer/permission credit.

## Unstable public ZST guard

The new source-specific route is `library/core/src/slice/sort/unstable/mod.rs`:
`sort<T,F>` at line 22, with arguments `v: &mut [T]` and `is_less: &mut F`.
The exact ZST guard is `if T::IS_ZST { return; }` at lines 27–29; the fixture
cuts before `len = v.len()` at line 33 and `intrinsics::likely` at line 34.
Source SHA is `23fa044fde8d3542f5f298654923ed2426930373259e6f71670c75b80501cf9a`.
Unlike the stable `BufGuard<T>` fixture in the prior Build, this source has
no `BufT` trait/method dependency. Its saved AST contains one root
`sort<T,F>` at `verified/lib.rs(5,1-24,2)`, two slice/callback arguments, two
translated lifetimes, and 10 distinct `VarPat` binders (12 occurrences).

One public negative is a valid intended failure: `public-guard-zst-branch-false`
passes paired support and refinement, then fails at the deliberately false
assertion in the reachable ZST arm, `verified/lib.rs(10,20-25)`:
`Assertion might not hold. (Cannot prove false.)` It is classified as an
intended assertion negative and demonstrates that the ZST branch is not
vacuous. It does **not** prove the guard's continuation nonzero fact.

The positive continuation and false-zero-continuation control both stop at
`verified/lib.rs(12,28-29)`, `No such function: size_of`, despite normal/read-only
export, paired support, refinement and captured AST. The positive gate is
false; the false-zero control is classified wrong/inconclusive. Neither earns
public nonzero-size proof credit. The exact saved AST and output identities are:

| Case | Verified source SHA | Normal / read-only full MIR SHA | AST SHA | Physical IDs; verifier log / first error |
| --- | --- | --- | --- | --- |
| `public-guard-positive` | `b99262ac790aaa327ef5bac9e31d8c0ed63eef2fd778f83ff4afe4adb79804f4` | `2d64badd886b44c7662d9f0cfbf4943d65b0670758efdda4754f90fc64fbf055` / `ab1a20a816f718ec3dc97ca2a2d1648fd82a18d9c41152b6cf7506c82472767c` | `8ddce505434bc14ead283850ae1a962e8b16879f9cb7f87a13db2a984bb9b67f` | 67 registered, 55 EXEC; log `d8180dda3c6b2d2446a4c49b819f25aa165d29e1d1d20ef7a925e562755d88c8`, unresolved `size_of` |
| `public-guard-false-positive-size` | `c41f97b0423fd5ce3fac842576f85cca8bfc01d9a9e3c06be2e3d947d423ef55` | `f90b2d988cb8da5a879781a3405cabc490e74cb4d67bb58f3e979abe2b44ec5b` / `f782ccfb24843342016515a1e50434e75bc44c6be0a55d2425668dbcba0419dd` | `a2ab4a00aa975e1ae1c520ed7ab5967a2a8fcc2229583eb6ea5d70cddc6c2912` | 56 registered, 55 EXEC; log `85edc2b9af74c25dc4412df525dede72b236b9004c7d1095112eda4cdba03199`, unresolved `size_of` |
| `public-guard-zst-branch-false` | `e304097acfed74383e789012453f068ffc075600ab6316c5e95297e7ad605385` | `17965039d8fb0279a9367d603a96273eb9d00f9ec91fbac6b6661597c0f00d04` / `db5227b329861134b7d4bbee204bf90c8c1204072594b7bdea2267e93706a9eb` | `c1296960112c6bb50fa11871ca832b453e63ee77f2501d5c374da503e2a618d5` | 55 registered, 52 EXEC; intended false assertion at `verified/lib.rs(10,20-25)`, log `5f5a5ac32866cad89c9ccaa0ea28eb84a0a6821ec038f0d7cec8a2cb9cf8dfca` |

The audit records `public_guard_candidate_raw_review_required=false`,
`public_guard_transfer_to_helper_proved=false`, `actual_caller_proved=false`,
`actual_sort4_proved=false`, `callable_summary=false`, and
`profile_accepted=false`. The public guard cases use the **pre-binding**
translator; consumer proofs use the **post-binding** translator. No composition
or inherited C4/C1 proof transfer follows from these separate runs.

## Remaining obligations

The established result is limited to reachability of the public unstable ZST
branch at its intended false assertion, plus independent pointer-component
and consumer diagnostics. The matching positive continuation is unproved
because of the unresolved `size_of` ghost name. Any later proof must establish
the `T::IS_ZST` to `size_of::<T>() == 0` relation under an accepted model and
prove the continuation across the exact public guard. Transfer through
dispatch, scratch construction and the helper call is still open; the
helper's `len + 16` overflow is independently open. The second sort4 call,
sort8 route, full five-comparison sort4 contract, tail/merge/panic behavior,
full SmallSort contract, and trust/admissibility of the entire experimental
profile are all unproved.
