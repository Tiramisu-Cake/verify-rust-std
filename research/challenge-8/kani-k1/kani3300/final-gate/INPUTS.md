# GATE-P — frozen C1 binding, worker15, 2026-11-14

Authority: owner instruction + `../../TASK-KANI3300-FULLGATE-REPLAY.md`.
Git/Python/static preparation only; no cargo, Kani, push, Actions or Cloud run.
Preparation Cloud cap $0. All final Gate A/B execution results remain NOT_RUN.
Research branch `experiment/kani-k1-kani3300g0-20261111` was pulled with
`git pull --ff-only` (up to date). Original GATE-P package: `3ec0512858`.
The pre-existing untracked worker14 r4 directory is outside this write scope.

Frozen C1: read-only `/root/kani-fix-3300-worker14`, clean HEAD
`1658f4cadfa83139e41180ce3865e23f79d889aa`, tree
`bfb5eb9db13ffb91ec4585b7c7ef41ddfe0008fb`;
publication reference `Tiramisu-Cake/kani:freeze/kani-3300-part1-c1`.
Local branch is `worker14-m3-final`; bindings use the exact commit.
Owner-provided lineage: C0 `53d883add` → M3 `34d54caf1`, `dc9c77db6`,
`aac27ed95` → M3-R3 `d36cfa00c`, `6c29e38c5`, `3a29b3323`, `ada5c7bd4`
→ readable-cycle `585768eb1` → composition bindings `3912b8e03`, `1658f4cad`.
Full identities and frozen hashes/subtrees are in EXPORT-MANIFEST.json.
The earlier C0 `478aad601` baseline is retained as history only.

Owner-reported C1 Quick `43509654772`: PASS, kani22/0, expected202/0,
ui14/0, script1/0, json3/0. This report was not independently fetched and
is neither the full Gate A nor SmallSort Gate B nor independent proof credit.
Eight strong oracle bindings, six mode expectations and seven composition
roots are pinned to C1. Composition preserves T1b allowance and
ORDER_UNCONTROLLED; selector ordering does not establish producer ordering.

SmallSort selected read-only snapshot remains
`/root/verify-rust-std-kani-traitpfc` @ `70ba5befc617627073738e26cb1466bd4fb76e41`,
library tree `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`.
Its separate test-only overlay is REPLAY-OVERLAY.json; final library-pin
confirmation remains with the coordinator. It is not claimed to be current PR#752.
Historical G3 source `2f1c45e519cc89e1dae532ad0f44243255a514d7`
(uninit/valid-value OFF, another Kani) is inventory only, no ON replay credit.

Both final CI-only overlays have C1 as their direct parent, and separate exact
C1 execution checkouts. No compiler/runtime/tests/production source edit enters
C1. CI builds must emit binary/model/dependency hashes; those bytes cannot be
known from static preparation. Run/publication limits and exact push refs are
in CI-REQUEST.md. Historical evidence/ledgers/download_verified are untouched.
