# PASS — static and synthetic review validation

Run `python3 research/challenge-8/kani-k1/kani3300/wave0/f4-fix-review/validate_review.py`
from `/root/verify-rust-std-kani3300-g0`.

Seven independent check groups pass, with one confirmed blocking CI-plan finding.
The exact source/tree/parent, nine-file scope,
14 package files, input hashes, patches, test-only main patch, workflow preservation
and native CI event/job/label coverage were inspected. Enumerating all 16 native
trigger sets finds seven PR workflows; CI-REQUEST lists six. `release.yml` requires
four PR builds and two five-OS test matrices; release/Docker publication skips are
intended. F4-R14-1 is recorded with review verdict CHANGES_REQUIRED.
Full patch replay reproduces
the source tree using an isolated index; regression-only replay changes seven tests
and preserves the main compiler.

The author's eleven static/synthetic check groups were replayed with only temporary
and output destinations redirected into this review directory. `AUTHOR-REPLAY.json`
is byte-identical to the input package's VALIDATION.json. The original package was
checked byte-for-byte against commit7485 before and after. Source remains clean.

Independent mocked entry-point checks cover all seven native invocation slots:
retained main data fail at the initialized SUCCESS requirement; synthetic expected-fixed
data pass. Cfg arguments, exact singleton/paired selections, distinct target paths and
inherited-flag cleanup were checked. Native probe was replaced with in-memory data.

`VALIDATION.json` records machine-readable identities and limits. No local compiler,
verifier, rustfmt, full runner, dependency install, CI or raw evidence download ran.
Actual new-test main execution, fixed compiler/runtime and full standard CI: NOT_RUN.
Actual compilation order/causality: UNKNOWN. General proof credit: NONE.

Concurrent g0 commit `1ce52e417eedcd43d200f358ce2ef7c911dbfe21` added S2 GO-request
files while review was active. It is preserved; review inputs remain exact7485 and
the F4 package/source remained unchanged. All review writes are confined here.
