# C-01 preparation request

Exact frozen identities, manifest SHA256 and upload branch names: [CI-REQUEST.json](CI-REQUEST.json).
This package authorizes no dispatch, push, publication or ledger entry.

Coordinator upload list (not executed):

1. Repository `Tiramisu-Cake/verify-rust-std`: exact source commit from
   `/root/verify-rust-std-ch8-c-ctl-w14`, remote branch `work/ch8-c-ctl-w14`.
   Commit message: `Add isolated C frame and lifetime controls [skip ci]`.
2. Repository `Tiramisu-Cake/kani`: exact control commit from
   `/root/kani-ch8-c-ctl-w14`, remote branch `uninit-ci/ch8-c-ctl-w14`.
   Commit message: `[skip ci] Prepare CH8 C controls on Kani host`.

The source commit changes only two test paths relative to production std
`872d5a43380752786415bc00d2a12ce0e930cb37`. The control commit has sole parent
`0aac16ef62da9e9d5645782d458593e5d78143ba`; only workflows and `ch8-c-control/`
change, and stock workflows are deleted. The workflow checks out the exact source
SHA from the std fork and exact stock tool SHA into sibling directories.
It does not use the source repository's older tool pin for execution.

A later separately authorized activation needs a same-tree sibling commit without
`[skip ci]` and the same sole tool parent, on a fresh branch such as
`uninit-ci/ch8-c-ctl-w14-c01`; preserve the original upload branch. A child activation
commit is rejected.
Exactly one dispatch is contemplated for C-01, bucket C (cap 1–2); no reservation
or consumption is claimed here. Attempt 1 is mandatory. Caps: 600s/root, 6GiB
process-group RSS, jobs1, 60min/job. Partial/setup/resource failures remain UNKNOWN
or NOT_RUN, retaining original exit/termination information; they do not satisfy
the negative oracle. N2 successful stock execution is an ALIAS_GAP observation,
subject to body/write/coverage qualification, and never closes C.

The exact root rows, source descriptions, target names, flags and caps live in the
control's `ch8-c-control/CI-REQUEST.json`, included in the payload manifest.
Generated property IDs/descriptions are not preinvented. Source-level oracle names
require runtime correlation before any independent proof credit is considered.
