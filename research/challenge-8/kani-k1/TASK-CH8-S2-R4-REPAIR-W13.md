# W13 — localized r4 repair and relocated-call binding gate

ISSUED owner17:01/coordinator. Fresh /new13, current model/tier, Fast OFF;
no subagents. STOP only real blocker, not volume/context. Correctness verification.
No compiler/cargo/rustc/Kani/CBMC/expansion/verifier/full runner/CI execution.

Frozen inputs, preserve all old outputs/objects:
- Review f5dd71722f82ac59e37152927a5f4dd9eee6ea1a,
  kani3300/ch8-s2/review-batch-r4/REPORT.md/json, HANDOFF.md,
  ALIAS-DISCRIMINATOR.json and review_checks.py/additional_checks.py.
- Package4e2801660d89d75a1357a420c78cd435159c35b3, source
  16aa3557742e1b8a8b64b3b3d49da23d988027f8/tree135f4549d1e8d6f69f1935c817f4c42bb917b756,
  control db81e62d76cfa193b1d7fe8e8ebbecead7e20ef8/tree76b64915601e060fc79da7cc1410993283a6dcab.
  Exact worktrees/parents/stock/request hashes: frozen batch-r4/PINS.json.
- Source mechanism diagnostic04c61ba50a and original task043f659cb6 unchanged.

Fix only these findings plus the explicitly requested name gate:
1. CLOSE R14-01/P1: general_fault_scratch has two bare sort4_stable calls
   (old lines300-301) without an import/declaration in the relocated module.
   Restore the original binding by a correct import/qualification. Preserve
   the branch, operation-identical copied algorithm, domains/frame/init,
   fault meaning, six exact assertion tags and positive/negative scope.
   Update the finite copy-correspondence import expectation, not the algorithm.
2. CLOSE R14-02/P2: ordinary_contracts/cfg_pfc silently skip chained attribute
   aliases. Reproduce the review discriminator through BOTH ordinary and combined
   gates after resealing/bypassing only synthetic byte guards as in review:
   use crate::kani::stub as ordinary1;
   use self::ordinary1 as ordinary2;
   #[ordinary2(swap_if_less,weak_swap)]
   Resolve alias chains to full identity with ambiguity/cycle/missing-target
   protection, or explicitly fail closed on unsupported chains before dropping
   them. Include safe/contracted targets, two/three-level/function/module aliases,
   cycle/ambiguity/unresolved cases. Keep active/inactive cfg, wrappers, full-target,
   foreign same-basename and verified-target same-cfg PFC checks effective.
3. Add bounded PREBUILD name/visibility gate for every newly added/relocated r4
   function, deriving the complete function inventory from the r3->r4 delta.
   Inventory each called static path and its actual lexical binding: local fn,
   imported/reexported fn/module/type, generics/parameters/local callable values,
   or explicit pinned prelude/provider. Respect module scope, self/super/crate,
   aliases, active cfg and relevant visibility; do not accept a same basename
   elsewhere as the correct binding. No ad hoc allowlist of unbound call names.
   Reuse existing token/cfg machinery; do not implement a general Rust compiler.
   Distinguish lexical path visibility from type/method/MIR resolution. Unsupported
   required static path is a precise fail-closed result, not silently accepted.
   Methods/dispatch outside this bounded check must be explicitly inventoried with
   limits; do not claim full compile success from a source scanner.
4. Distinguishing name tests: frozen r4 missing import is rejected, repaired source
   accepted; removed/renamed/wrong-target/cfg-disabled import and foreign-basename
   mutations rejected; legitimate qualified path/alias/local callable cases handled.
   Check all branches, including the len>=8 path, regardless of selected input32.
   New check executes before stock setup/build in ALL11 effective contexts along
   with ordinary/PFC gates. Exercise semantic checks, not only immutable-byte guards.

Do not broaden the proof/model/source delta. Keep originals/S1/nonS2 unchanged,
both general32 same-cfg verified sort8 registration ONLY, DIAGNOSTIC_ASSUMED,
four removed ordinary contracted-target bindings, faithful local copies and their
explicit changed-identity coverage. Preserve11roots/20covers/6negatives/all caps,
stock0aac and protected collector/packer/diagnostic/error/B-01/B-02 bytes; runner
may change only identity literals/necessary gate integration. No issue publication.

Use NEW isolated source/control candidates; final source sole parent97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a,
control sole parent9e14e033f9ee31522b571c127609dcdff76d230b. Preserve checkout7/5/2.
Write only g0 kani3300/ch8-s2/batch-r4-r1/: full pins/source/control/request/workflow,
gate/name-resolution maps, FINDING-CLOSURE, bounded deltas from frozen r4,
source/control/full-stock-relative inventories/hashes/patches, final-object tests,
validator/replays/shallow checks/manifests, REVIEW14-REQUEST and HANDOFF.
Reuse package machinery; meaningful new regressions and affected existing checks
suffice, no unnecessary broad repeats. Clearly bind actual final tests or distinguish
precursor/final binding-only changes. Do not overwrite batch-r4/review-batch-r4.

Native compilation/causal repair NOT_RUN; actual R3 failing unit/body UNKNOWN.
29/29 +9/14=38/43 reference only, r0..r3 charged0; no ledger/reservation/budget.
No CI/rerun/cancel/push/PR/source publication. Ownpaths-only commit --only,
[skip ci], Tiramisu-Cake <igkharin@gmail.com>. READY full g0/source/control/tree/
parent/request pins, test scope and R14-01/R14-02 closure evidence.
Next: SAME reviewer14 delta review, then GO-request only after APPROVE/CLOSED.
