# Synthetic tool facade archival rationale

## Applicability

The S3 packaging diagnostic identified `synthetic-tool/.devcontainer` as a
rejected symlink. The backend creates that link through a generic loop over
all top-level entries of the candidate tool (except `bin`); another loop links
all `bin` support entries. The adjacent code comment says the disposable
facade exists because `rust_fe.run_vf_mir_exporter` resolves an exporter sibling
of `Sys.executable_name`: the candidate console bytes are copied there and the
unchanged support tree is linked for the translator invocation. The
`.devcontainer` link is included by that generic support-tree loop, not added
as a separate special case. The code does not establish whether that particular
entry is individually needed, so links remain available during invocation and
are archived only afterward.

## Bounded archival behavior

A `finally` path covers facade creation through synthetic invocation. It writes
`synthetic-tool-facade-manifest.json` with each generated facade-relative
symlink path, its exact `readlink` target, and kind, then unlinks only those
links inside the facade. It does not open, traverse, hash, copy, or delete any
symlink target. Regular console and transport-wrapper files stay in the facade
at their original paths; their actual and expected SHA-256 values are recorded.
The manifest records no proof credit. The disposable facade directory and other
evidence such as decoded and encoded inputs, AST, and stage records remain in
place.

If setup only partially creates the facade, the finalizer records and removes
links already created; absent console/wrapper hashes are represented as null.
If invocation already failed, cleanup failure is attached as an exception note
and does not mask the primary error. A cleanup failure after a successful
invocation remains an error. This archive is synthetic transport evidence only
and does not change production checks, classification, or proof-credit rules.

## Validation limits

AST-extracted unit tests exercise the archive and finalizer helpers without
importing the backend or invoking the translator. They check exact target
recording, only unlinking facade links, unchanged external target and regular
file bytes, partial setup, and primary-versus-cleanup exception behavior. A
local package-evidence fixture rejects the synthetic `.devcontainer` link
before archival and accepts the same evidence tree after link accounting and
cleanup; the facade contains no symlinks afterward. These checks establish
local filesystem and packager behavior, not a Cloud package upload result or
proof acceptance.
