# Validation scope

FINAL-VALIDATE.json is the single exact-candidate final command receipt; its full
stdout/stderr contain Python unit/service output, not native verifier logs.
136 frozen legacy checks and56 protected S3-1 checks run against their exact
fixture requests/workflows, with only fixture locations/default request patched.
35 S3-2 checks reuse the existing framework: exact source/aliases/contracts,
role/producer IDs, eight-row schedule/singleton flags, cutoff/cleanup versus global
stop, protected snapshots/errors, real file/hash/canonical entry writers and
portable prefix replay, source/stage/target mismatch/missing/null/partial/NOT_RUN,
diagnostic no-promotion and misleading-init-role rejection. No dummy binary is
executed; only small owned Python children are used by process service tests.

SOURCE-PREFLIGHT and CONTROL-PREFLIGHT are the existing static CLI paths on exact
committed source/tool/control/request bytes. No compiler/expansion/MIR/native run.
SOURCE-GATES maps were derived during preparation and their source hashes match
the final preflight inputs. PRECURSORS separately records failed preparation
attempts and corrections; no failed native or historical evidence is rewritten.
No full suite or final Validate repeated after its pass.
