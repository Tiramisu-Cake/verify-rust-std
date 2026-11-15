# Handoff — coordinator only

This stage prepares a local reviewed package. It does not authorize a push, CI or ledger action.
Read CI-REQUEST.json for exact source/control/tool SHA/tree and manifest/request hashes.

Before any separately authorized dispatch, ensure source b5cf722e20f71c1f4f494ec4ad2af2970aa3bc9f
(tree bd6fdf1750e589a8fa5c63bfd445553df43adb8a) is published to Tiramisu-Cake/verify-rust-std.
Its existing source commit message includes [skip ci]. Suggested branch:
profiles/source-b5cf722e-skip-ci, from /root/verify-rust-std-ch8-profiles-w11. This worker did
not push or establish remote reachability; local remote-tracking refs do not establish it.
The source branch is outside the OFF trigger prefix. No new std source change is requested.

The supplied control commit also contains [skip ci], as required by this task; pushing it
as-is will not dispatch. After separate coordinator reservation/GO, create a same-tree,
single-parent sibling trigger commit with parent0aac16ef62da9e9d5645782d458593e5d78143ba,
without a skip marker, and publish that commit to uninit-ci/ch8-prof-off-a in Tiramisu-Cake/kani.
Check its exact tree against CI-REQUEST.json. Control binds github.sha and its parent dynamically,
so a same-tree sibling is supported. Keep author Tiramisu-Cake <igkharin@gmail.com>.
Only one OFF accepted dispatch is allocated; every rerun is blocked (attempt1 only).
ON remains separate and is not prepared here. Do not dispatch both std and kani hosts.

After CI, independently review all62 rows: exact source/mode/target/instance and per-cfg
inventory, negative IDs/descriptions, preceding successes/reachability, all cover IDs/counts,
original exits/signals/caps, compiler/driver/backend hashes, target and source cleanliness.
The export schema lacks named successful properties and mangled-wrapper correlation; these
remain explicit review obligations, not inferred from root names or success counts.
The final frame-negative receipt must retain UNKNOWN until its actual generated modifies
property is bound. Preserve all NOT_RUN, UNKNOWN and partial results; no automatic retry,
compiler patch, weaker property or KeyLess substitution is authorized.

Final control: 236bf75037fa4e56d0aa18f93df1d6b6965676b8; tree 89e69479b1fe981a24a37ad9822646e0d490f6f7.
Review: GO_STATIC_REVIEW_ONLY; REVIEW.json. All26 synthetic tests and YAML/actionlint PASS.
The exact rustc executable is resolved with bounded rustup which for the pinned toolchain,
then hashed without running it; missing binary hashes stop a row before Kani starts.
No whole-batch result or Rust compilation has been observed in this stage.
