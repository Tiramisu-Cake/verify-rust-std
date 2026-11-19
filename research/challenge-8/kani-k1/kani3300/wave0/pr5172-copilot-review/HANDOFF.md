# HANDOFF — independent review of PR #5172 Copilot fixes

2026-11-19. Coordinator task, one stage. **Verdict: APPROVE.**

No required code changes found. The compile fix, visited-set optimization, and checked-body reuse are correct on static inspection against the pinned nightly sources. Formatting is expected to pass for the reviewed changes; this is a source-based prediction, not an executed format check. One optional wording clarification for the MEDIUM reply appears below.

## Scope and identities

- PR: https://github.com/model-checking/kani/pull/5172
- Candidate worktree: `/root/kani-pr5172-copilot-w15`.
- Candidate branch: `fix/pr5172-copilot-20261119`.
- Reviewed commit: `cea872ac973f98daef320e056987b6d5365d9e8b`.
- Verified immediate parent: `ac0304a8bfde3002ef0411ae0e73f94ce0cd7878`.
- Merged main parent and PR comparison base: `0997d11c14cb2da0824efc34e2c4001e53ac0faf`. Verified it is the merge base with `ac0304a8bf`.
- Candidate delta: two compiler files, 31 insertions / 25 deletions. Reviewed the complete delta and the six compiler files changed by the PR relative to that merged main. The PR also adds 22 Rust regression fixtures and their expected outputs; these are unchanged by the candidate.
- Author package: `../pr5172-copilot/HANDOFF.md`. Its reasoning and draft replies were checked against code, rather than accepted as evidence of correctness.
- Read the live GitHub review comments through the GitHub connector, including inline comments `4633384394` and `4633384489`. Nothing posted.

The expected `/root/.rustup` directory is absent in this execution environment; `HOME=/root` and `RUSTUP_HOME` is unset. No installed toolchain source was available there. Instead, read the official [nightly manifest](https://static.rust-lang.org/dist/2026-11-18/channel-rust-nightly.toml), which identifies `rustc 1.102.0-nightly (59cbdee2e 2026-11-17)` and full Rust commit **`59cbdee2e7b3ee50e44b460561c43c9e3023d9f0`**, then inspected upstream source files at that exact commit through the GitHub connector. This resolves the author's unavailable-source limitation without installing or running a toolchain. All upstream Rust references below use that commit.

## 1. Compile fix and API sweep — PASS, static

At `uninit_visitor.rs:790–795`, matching `ty.kind()` borrows the `TyKind`. The inherent `Ty::kind(self)` returns `&'tcx TyKind<'tcx>` ([sty.rs:1123](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_middle/src/ty/sty.rs#L1123)). Consequently the `Adt` arm binds `args: &GenericArgs<'tcx>`.

The nightly's [FieldDef::ty](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_middle/src/ty/mod.rs#L1594) takes `args: GenericArgs<'tcx>` by value and returns `Unnormalized<'tcx, Ty<'tcx>>`. `GenericArgs` is a `Copy` wrapper, not an alias that makes another reference interchangeable ([generic_args.rs:383](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_middle/src/ty/generic_args.rs#L383)). Thus `field.ty(tcx, *args).skip_normalization()` is the correct fix; the old `field.ty(tcx, args)` mismatches the argument type. Preserving `skip_normalization()` preserves the existing classification semantics. Merged main's `intrinsics.rs:91–98` independently uses the same dereference and normalization pattern.

Searched all six PR-changed compiler files, and inspected both the candidate delta and PR delta against merged main, for `FieldDef`, field `.ty(...)`, `GenericArgs`, instantiation, closure arguments, stable/internal conversions, and resolution calls. There is only one internal `FieldDef::ty` call in this scope: the corrected one. No other borrowed-versus-by-value `GenericArgs` mismatch was found.

The other superficially similar calls use different APIs:

- The two `rustc_public::mir::mono::Instance::resolve(def, &args)` paths correctly borrow **public** `GenericArgs`. The pinned [public API](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_public/src/mir/mono.rs#L125) still takes `&GenericArgs`; applying the internal API's dereference rule here would be wrong.
- `args.as_closure()` takes its internal `GenericArgs` receiver by value; method-call autodereferencing can copy the `Copy` receiver from the borrowed binding. Its `tupled_upvars_ty()` result remains the child type to inspect.
- Internal tuple elements iterate as type values; array and pattern bindings remain borrowed child types and are correctly dereferenced. The stable operand/place `.ty(&locals)` calls are separate local-declaration APIs, not `FieldDef::ty`.
- The other four compiler-file deltas are an export adjustment, fallible public instance resolution, removal of delayed visitor state/checking, and passing context to the local visitor. No additional nightly API incompatibility was found there.

This is not a claim that the entire compiler or all fixtures have been compiled.

## 2. Visited-set soundness — PASS

Reviewed `uninit_visitor.rs:780–814`, including every recursive edge. The set is fresh for each top-level classification, is shared by every recursive call, and keys the complete instantiated internal type, including generic arguments. It does not key only the ADT definition or share results between roots.

The pinned internal [Ty definition](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_middle/src/ty/mod.rs#L514) derives `Copy, Clone, PartialEq, Eq, Hash`. Its `Interned` representation uses pointer equality and pointer hashing under the interner uniqueness invariant ([intern.rs:70–85](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_data_structures/src/intern.rs#L70)). `HashSet<Ty<'tcx>>` therefore has the required compatible, inexpensive `Hash + Eq` operations.

For every valid type graph on which the old classifier returns a Boolean, the new classifier returns the same Boolean:

1. Every parent combines child results with short-circuiting OR / `any`, or directly returns the child's result. A `true` at any depth immediately propagates to the classification root. There is no later sibling traversal after such a result.
2. A repeated node encountered while traversal continues therefore cannot be a completed `true` node; a completed previous visit returned `false`, so returning `false` again is exact.
3. An in-progress ancestor cannot recur through valid by-value storage. References and raw pointers are leaves, and valid Rust storage does not contain an infinite by-value cycle. This excludes the remaining way a repeated node could lack a completed answer. No equivalence claim is needed for malformed/infinite graphs where the old recursion fails to return.

The type decisions are unchanged: unions return `true` before inspecting fields; other ADTs OR their instantiated fields; tuples OR their elements; arrays and patterns inspect their element; closures inspect tupled upvars. The listed scalars, never type, function items/pointers, references and raw pointers return `false`; every unknown/unhandled kind still returns `true`. Even the previous treatment of zero-length arrays and unused enum variants is retained. Repeated unions or unknown kinds cannot hide a positive result, because the first positive visit already terminates the root traversal.

Expected traversal work is O(V + E), with O(V) set storage, for the distinct instantiated types and traversed child edges. This is a traversal bound, not a bound on all rustc type instantiation or compiler work. The repeated union-free tuple example now inspects each distinct tuple once instead of recursively expanding every repeated subtree. Stack depth is still the longest traversed path; this patch does not make recursion iterative.

## 3. Resolver, callers, effects and diagnostics — PASS

There are two direct call sites for the shared `resolve_call`: `points_to_analysis.rs:197` and `uninit_visitor.rs:774`. Both consume the new tuple correctly. The local wrapper maps it back to `Instance`, so its call at `uninit_visitor.rs:283` retains its previous result and error handling. `points_to/mod.rs` is only a re-export. The delayed initial-target visitor has its own separate resolver, and the delayed instrumentation visitor does not call this shared function. There is one caller of `apply_regular_call_effect`, and it passes the checked body.

For successful resolution at `points_to_analysis.rs:352–376`:

| Resolved kind | Returned body | Subsequent points-to path |
| --- | --- | --- |
| Intrinsic | `None` | `InstanceKind::Intrinsic` arm at lines 204–308 handles it; cannot fall through to the regular-call arm. |
| Foreign Item | `None` | Non-intrinsic arm first tests `tcx.is_foreign_item` at line 310. Alloc / alloc_zeroed add heap edges; other foreign functions do nothing here. Both stay inside this branch. |
| Ordinary Item / Shim with available MIR | `Some(checked_body)` | Non-foreign regular-call branch consumes that body at lines 330–331. |
| Bodyless Item / Shim, failed resolution, Virtual, LlvmIntrinsic, non-FnDef | No successful tuple | Existing rejection paths return `Err`; points-to leaves accumulated graph state intact. |

In particular, the new `let Some(body) = body else { return };` is **after** the intrinsic branch and **inside the else of** the foreign-item branch. Intrinsics, including those with fallback bodies, never reached `apply_regular_call_effect` in the parent. Foreign calls never reached it either. Therefore the guard does not bypass any previous intrinsic handling, allocation edge creation, or foreign-call effects. The pinned public `is_foreign_item` delegates to the same `tcx.is_foreign_item` query ([bridge context:345](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_public_bridge/src/context/impls.rs#L345)).

The bodyless error text and other rejection reasons are unchanged. A successful ordinary resolution already establishes body availability; the new guard is defensive under that invariant. No graph-reset operation was added.

`checked_body` is still called at the same resolution point before any ordinary call effects. At `kani_middle/mod.rs:143–150`, it checks tail-call spans when definition-level `has_body()` is true, reports them, and only then requests `instance.body()`. At lines 210–220, an empty span list emits nothing; a nonempty list emits each tail-call error and immediately aborts. Thus removing the later repeated request loses no diagnostic and does not remove previously duplicated diagnostics: the first nonempty scan prevented reaching the second request. Shims that skip the definition-level scan still obtain their generated body. The pinned bridge distinguishes item availability from generated instance availability ([context:77–90](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_public_bridge/src/context/impls.rs#L77)); no incorrect `has_body()` shortcut was substituted.

At `points_to_analysis.rs:456`, `body.internal_mir(self.tcx)` invokes the same `RustcInternalMir for Body` implementation at `transform/internal_mir.rs:633–667`. Previously it converted a second checked body for the stable round-trip of the same resolved instance. Now it converts the body returned by the first lookup. The instance, compiler context, body contents and conversion are equivalent; no argument mapping or graph-transfer code changed.

For N successful regular-call transfers, the relevant path now performs N checked-body requests instead of 2N. Where `has_body()` is true, it also removes N redundant scans. The local visitor still makes its own request; fixpoint iterations, caller recursion and multiple harnesses can still repeat requests. There is no per-instance cache, and the patch does not claim one.

## 4. Formatting — expected PASS, not executed

Read the actual `rustfmt.toml`: edition and style edition `2024`, `use_small_heuristics = "Max"`, `merge_derives = false`, default maximum width 100. Checked the changed layouts against the pinned rustfmt's `items.rs`, `pairs.rs`, `matches.rs`, `closures.rs`, and configuration code.

- The full single-line `resolve_call` signature would be 109 columns, including ` {`; it must retain its multiline parameter layout. The local wrapper's full signature would be 104 columns and also stays multiline. The nested `inspect` signature exceeds the limit too. `Max` does not make these signatures fit within 100 columns.
- The tuple, array/pattern and closure match arms occupy 93, 99 and exactly 100 columns, respectively, including indentation and trailing comma. The last one fits; it should not be wrapped merely because it is at the limit. Rustfmt's match-body budget reserves the comma.
- The ADT branch retains the multiline OR and closure. Combining the closure's call with its `any` prefix exceeds the width; combining the multiline RHS with `def.is_union() ||` is rejected by rustfmt's binary-pair layout rule when the preceding prefix exceeds one indentation level. The candidate's operator and closure-body indentation match the resulting layout.
- The new short `let Some(body) = body else { return };` fits on one line under the `Max` let-else heuristic. The tuple destructuring resolver call still requires its current split after `=`. The `map` adaptation, final `inspect` call and body conversion fit on their current lines.
- The added `std::collections::HashSet` import is consistent with the existing import ordering and grouping.

No formatting defect identified. `git diff --check` passes for both the candidate delta and the complete PR delta against merged main. That whitespace check is not a substitute for running rustfmt, which was explicitly prohibited.

## 5. Clippy — no likely configured warning found

Read workspace lints, compiler crate lint inheritance, `.cargo/config.toml`, compiler crate attributes and `.github/workflows/format-check.yml`. The workflow denies warnings, but the repository does not enable the pedantic group for this code.

- `needless_pass_by_value`: the new `body: StableBody` is only borrowed by `internal_mir`, so a borrow could be an optional API refinement if pedantic checking were enabled. In this pinned Clippy the lint belongs to **pedantic**, not the default warning set ([lint declaration](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/src/tools/clippy/clippy_lints/src/needless_pass_by_value.rs#L58)). Moving the owned result into its sole consumer is valid and creates no correctness problem.
- `type_complexity`: the new `Result<(StableInstance, Option<StableBody>), String>` scores 150 using the pinned visitor: Result 10, tuple 20, Instance 30, Option 30, Body 40, String 20. Aliases are not expanded by this syntax visitor. The default threshold is 250; no local threshold override was found. A new return-struct/type alias is unnecessary solely to avoid this lint.
- `apply_regular_call_effect` now has six parameters including `self`, below the default `too_many_arguments` threshold of seven. `inspect` has three. No unnecessary clone, pass-by-reference of a Copy `Ty`, or needless collection was introduced.

These are source-based lint predictions; Clippy was not run.

## Draft replies — accurate, suitable tone

**HIGH:** Approve as drafted. It directly explains the chosen fix, the short-circuit justification and the traversal bound without claiming a benchmark or executed test. "Shared fields are inspected once" is understood within one classification, as its opening sentence specifies. The AI disclosure is retained.

**MEDIUM:** The chosen body-reuse option directly addresses Copilot's alternative to caching. The request-count reduction, absence of cross-analysis caching, and first-nonempty-scan abort are accurate. Tone is concise and cooperative. For strict precision about generated shims, optionally qualify the scan sentence; some regular-call transfers have no definition-level scan to remove. Suggested complete reply:

> The resolver now returns the checked body with the instance, and points-to analysis reuses it in `apply_regular_call_effect`. This removes the second body request per regular-call transfer and, when `has_body()` is true, the second tail-call scan. The tail-call diagnostic aborts on the first nonempty scan, so repeated requests did not duplicate it. Iterations can still repeat body checks; caching across analyses can follow after profiling.
>
> *Disclosure: this comment was prepared with the help of AI assistants.*

This wording clarification is optional and does not block approval. Neither reply should imply that compilation, format checking, Clippy or regression tests ran.

## Validation, limits and stop

Performed read-only Git/source inspection, live GitHub comment reads, exact-nightly upstream API/rustfmt/Clippy source inspection, static line-width calculation and `git diff --check`. Candidate HEAD and source files remain unchanged. No cargo, rustc, rustfmt, Clippy, Kani, CBMC, push, CI or external message/review submission was executed. No toolchain files were modified. No build success, performance measurement or formal proof credit is claimed.

Only this review HANDOFF is authorized for writing and committing. Unrelated concurrent work in the report repository is preserved and excluded from the review commit.

**Next coordinator action:** accept this static review, optionally use the qualified MEDIUM reply, and arrange separately authorized compilation, formatting/Clippy and targeted generated-shim/unresolved-call regressions before publication. This review grants no push or CI authorization. One-stage review complete; stop at **HANDOFF**.
