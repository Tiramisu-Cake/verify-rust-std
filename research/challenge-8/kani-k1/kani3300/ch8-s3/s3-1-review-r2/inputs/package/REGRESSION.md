# Distinguishing real-writer regression

FIXTURE-REGRESSION.py is an exact copy of committed test_s3_paths.py, bound by
PINS.json and TARGETED.json. The unchanged s3_validate.py legacy-suite wrapper
still runs its136 legacy tests; the S3 suite adds this new module to the existing
46 tests. Final test counts/timing come only from FINAL-VALIDATE.json and its
stdout/stderr, not from precursor estimates.

Fixtures create bounded, non-executed kani-driver/kani-compiler/cbmc files and
materialize exact S3-SOURCE source files. Hashing, fingerprint serialization,
controller snapshots, invoke's actual worker argv, worker, runner._run_group,
compile/source-under-test receipt writers, strict local readers, packer and
upload-only reader are real. No fixed /tool/<name> fingerprint mock is used.
Only Git identity responses, memory telemetry and native execution/supervision
are fixture substitutes. verify_source itself checks sibling boundaries, every
source hash/location anchor and runtime dependency hashes. Dummy executables
are never launched. Native metadata/results are explicitly synthetic and carry
no proof credit.

The workflow regression parses the actual frozen workflow and extracts --tool
tool and --std export. It runs the real campaign/controller/invoke/worker path
and checks E0/pre/BEFORE/AFTER/post equality and each dummy file's real SHA256,
then checks local/upload-only equality. Additional inputs cover absolute paths,
./tool, nested/../tool and a known directory symlink alias. The unrepaired shape
is captured directly: relative controller versus resolved worker with equal
file hashes still rejects. run_targeted.py also reconstructs the complete fc29
control import closure from pinned Git blobs, adds only this test file, and runs
the same workflow case: exit1 with recorded worker binary drift: before. That
failure is expected and retained in FROZEN-DEFECT.*; the frozen writer is never
edited, and this is not a transformed historical artifact.

Negative controls retain two sealed roots and stop before later launches:
wrong directory with byte-identical binaries; real file mutation; missing file;
PermissionError(EACCES) at the actual file-open boundary; all COMPLETE/FAILED/
IN_PROGRESS/INTERRUPTED/null/UNKNOWN worker states with recorded real-file drift.
Original worker reason/exit/signal survive, and a matching controller post cannot
erase recorded drift. Real mutation also checks portable prefix/global-stop
preservation. Reader controls cover missing/null/wrong-type/error/state tamper,
required hashes, missing keys and unfinished/incomplete snapshots.

A separate actual forked Python worker is stopped in the substituted native
callback after the real BEFORE receipt publication, then killed with SIGKILL and
waited/reaped. Its untouched on-disk record genuinely has no AFTER/source_after/
binary_identity. Real controller E0/pre/post pass; protected accepts only the
narrow verified-interruption recovery and rejects success or unverified shutdown.
The child runs no descendants/native process. A separate campaign fixture
models missing AFTER and checks original exit-15/signal15/exception and UNKNOWN
qualification through the finalizer. The actual killed-worker test validates the
protected recovery boundary; it does not claim that incomplete output accounting
would qualify a whole killed campaign. No recorded errors are cleared or ignored.

PRECURSORS.json retains the initial fixture failure: the real memory preflight
correctly refused the host's less-than2GiB reserve before native execution. Only
synthetic fixture telemetry was then supplied, leaving production caps unchanged.
TARGETED.json records20 passing exact-final targeted tests, frozen expected
rejection and exact fixture/import-closure hashes. Final Validate is invoked once
after actual control freeze, with original exits and measured timing/margin.
