# A1 packaging R7 activation rationale, 2026-10-20

## Defect and applicability

The terminal S3 Build `0be85097-5764-4838-8e3b-fea09420213e` failed during
external evidence upload because the manifest exceeded the fixed 8 MiB limit.
The missing-summary exception was secondary. The R6 release records that the
Brief/catalogue were unavailable and all 26 matrix results remain UNKNOWN;
there is no proof credit to carry forward. The administrative diagnosis found
no retained evidence payload to republish.

The reviewed infrastructure candidate `8e4da6f232ebdddd7419c2f83ee5c68eb74c2b03`
reduces manifest serialization overhead, references the archived config by
canonical path/SHA/size, preserves complete audit and inventory, and reports
the primary packaging error. Its isolated fixtures and Luna HIGH review do
not establish production Cloud behavior or proof acceptance. R7 therefore
uses the existing `o26-sort4-c1-current-recovery` lane and a fresh authorization
phase/profile under a separate budget account.

## Preserved semantic inputs and controls

R7 is based on the S3 profile and release. Preserve the compiler and std
revisions, VeriFast tool revision, R2 and C patch pins, domain/contracts,
equality/refinement inputs, normal and unwind checks, target, and all 26
required matrix cases. Only the packaging implementation and the fresh R7
authorization/profile/entry/runner bindings may differ. Recipe and source
closure pins must bind those exact files and the packaging candidate.

The R7 entry is a separately pinned adapter. Its small runner wrapper checks
the R7 profile and the original S3 runner SHA, then delegates to that unchanged
runner with only the R7 authorization phase and profile path selected.

The existing 8 MiB limit, full raw-audit and inventory integrity checks,
complete payload retention, no-truncation behavior, stale-summary rejection,
and primary-error preservation remain active. The actual Cloud preflight,
ordinary Evidence Brief, and formal proof stages remain required; synthetic
or static checks alone cannot establish any of them. R6 profile, release,
budget, and historical verdicts remain unchanged.
