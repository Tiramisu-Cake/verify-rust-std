# Kani #5172 follow-up handoff

The candidate is local in `/root/kani-5172-followup-w11` on `fix/uninit-resolver-followup`.

| Git object | SHA |
| --- | --- |
| Commit | `3d042972b8e69868fa1d61a3eca4613ca175eb8d` |
| Tree | `e9a901f493ba353514721a459bbcb9f5c8655d25` |
| Parent (upstream main) | `87c87010eda7797d7fa14033ca68bcbe17184a63` |

## Review follow-ups

1. The visitor uses the shared resolver to check availability without constructing stable MIR. The resolver accepts intrinsics, foreign items, shims, and items with `has_body()`. Points-to loads regular callees through `checked_body`, which still diagnoses explicit tail calls when loading a body. Reachability also uses `checked_body` when loading each callee for transformation. Per-instance caching is deferred because sharing converted bodies across recursive dataflow analyses would add cache ownership and lifetime management to this patch.
2. The resolver and both visitor shim guards use the same `unsupported_call_reason` helper, preserving the diagnostic wording.
3. Points-to uses `expect` to enforce that an accepted non-foreign regular callee has a MIR body before applying its call effect.

`git diff --check` and `/root/rustfmt-toolchains/bin/kani-fmt-check.sh` passed. Fork quick CI is pending for the existing `tests/expected/uninit` suite (including `unresolved-calls`) and `tests/kani/Uninit`.

## Overlap with #5196

A `git merge-tree --write-tree` comparison of upstream main and the candidate against #5196 head `bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a` found the same two conflict hunks in both cases.

- In `ptr_uninit/uninit_visitor.rs`, #5196 adds a guarded `Item` arm that loads union-bearing return values just before the regular call arm. That insertion conflicts with #5172's `Item | Shim` arm and its comment. The follow-up changes only the resolver invocation at the start of the call arm. #5196's volatile-store, union-argument and `Return` edits apply outside the conflict. Integration should preserve the #5172 shim guard and operand checks when combining the call arms.
- In `check_uninit/mod.rs`, both branches add entries at the end of `SKIPPED_ITEMS`. Main adds the three panic-permission models and #5196 adds `InitializeMemoryInitializationState`.

## Draft PR

**Avoid building MIR when resolving memory initialization calls**

Follow-up to the review of #5172. The initialization visitor checks whether a callee has MIR without building it. Points-to loads the body for regular calls and enforces that it exists. Both passes share the unsupported-call diagnostic.

Testing: [fork quick CI results pending]

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
