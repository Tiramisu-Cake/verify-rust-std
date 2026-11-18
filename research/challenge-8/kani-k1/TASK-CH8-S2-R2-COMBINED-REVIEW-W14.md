# W14 — combined S2 r2 source + diagnostic runner review

ISSUED per owner14:08: combined review of the immutable component pair below,
while13 prepares exact final composition. Fresh /new14, current model/service tier;
Fast is OFF by owner, do not toggle. No subagents. STOP only real blocker, not volume/context. Correctness
verification, not security work. Contract TASK-CH8-S2-R2-COMPOSE-W13.md.

Exact source component: g0 **714c1ca56dd7cf352ae6feebe5e252178cdb63b2**,
`kani3300/ch8-s2/batch-r2/`, source **efb1aba7fc6445cba6cd75154713b598c9e2579d** /
tree **4563e06722871ae5eafdf6d288afa21a406b6ba8**, parent97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a.
This is a source/model draft; its old composed control2d00/b678 is NOT the repaired
runner and cannot be the final GO candidate.

Exact repaired runner: g0 **a8e3cb30c617a6dee07fa847f1f23470d59783e3**,
`kani3300/ch8-s2/runner-diagnostics-r2-r1/`, control
**472be8c3794d7a4530760ab7d5eae4ce950aa01c**, tree
**4835c615d20e6606ddcdc64bbb8314973cec141b**, parent9e14e033f9ee31522b571c127609dcdff76d230b.
Root verified28 committed runner files/27 manifest hashes and40 source packet files.
Independently close B-01/P1 and B-02/P2 from review5db34a9243; author-reported
32/32+isolatedpreview1/1 does not replace your verdict. Retain earlier33-test preview
timing failure and assess its relevance; no repeat-until-green/hidden omission.
Use TASK-CH8-RUSTC-DIAGNOSTICS-DELTA-W14.md for the narrow closure criteria.

Begin reviewing these components now.13 is instructed to compose the repaired
runner with the unchanged efb source in a new immutable sibling batch-r2-r1/;
coordinator will deliver its exact full g0/control/tree/request pins. Until that
binding arrives, return a precise component verdict/pending integration gate, not
final combined APPROVE/GO. Final composition needs same14 integration delta review;
reuse established component conclusions by byte identity, no broad repeated audit.

Review one combined immutable batch-r2 against source9fd/control2ec and runner
ac956bdf4db98a95e2da988ccd2c527582d3d32f/b678fb6cdd5edf69a4e952167422f36a45a3d6cb.
Source: remove13line sort8 registration and ordinary model stubs in BOTH
general32_assumed and general32_weak; source/map evidence showed both verified
uses in same cfg. Exact generic signature/domain/init/frame/topology and full-value
sortedness/multiplicity summary, useful-return/nonvacuity, expected weak_merge-only
negative preserved. No weakened premise, vacuity, production runtime change or
qualification from an explicit diagnostic summary. All11 cfg contexts/remaining
verified registrations/ordinary replacements and distinguishing static controls.

Runner: reuse exact prior scope-B APPROVE by byte invariance if available. Otherwise
review diagnostic delta per TASK-CH8-S2-DIAGNOSTICS-REVIEW-W14.md scopeB: all error
blocks/context retained independently of previews, stdout/stderr/chunk/ANSI/EOF,
explicit partial/cap/producer completeness, normal/failure/fallback/packing,29tests
and relevant service/error controls. Review source/hash/fixture/request integration
even if runner code itself is inherited; new native diagnostics remain NOT_RUN.

Verify full candidate/delta patch replay, manifest/source/tool/control hashes,
control required parent9e14, all selection11roots/20covers/6negative oracles,
existing resource/time/output caps and checkout7/5/2. No new compiler/toolchain
audit or local compiler/verifier/full runner. Relevant Python/static checks only;
don't repeatedly rerun broad unchanged suites.

Historical run44284869572 error/cause remains UNKNOWN; no verified compilation or
causal fix claim. sort13/general32 DIAGNOSTIC_ASSUMED, proof credit NONE.
Output new `kani3300/ch8-s2/review-batch-r2/`: REVIEW.md/json, validation/pins/
provenance, findings with original owner13(source/composition) or11(runner),HANDOFF.
Localized findings return owner via coordinator; preserve old candidates/reviews,
new immutable repair + same14 delta review. No author edits by reviewer.

APPROVE plus all blockers closed -> coordinator GO-request exact combined pins,
owner alone decides retry/accounting. No CI/push/PR/cancel/rerun/source/ledger/
reservation/budget; item1 28/29,item2 provisional10/14,total38/43 reference only.
Paths from `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.
Exact ownpaths commit --only, `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Final `READY <full g0 SHA> <verdict>`.
