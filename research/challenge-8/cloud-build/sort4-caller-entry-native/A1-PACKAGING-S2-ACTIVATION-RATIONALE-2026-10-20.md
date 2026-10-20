# A1 packaging S2 activation rationale, 2026-10-20

## Defect and applicability

R7 Build `025378b9-d36b-4837-bd19-6df8ed1471c4` reached the focused P0a
stage after successful evidence delivery, then failed because
`a1-focus-backend.py` still selected the R6 S3 profile by a hardcoded path and
authorization phase. The R7 recipe intentionally transports the fresh R7
profile instead of the historical S3 profile, so this stale adapter binding
rejects the exact R7 profile before focused proof execution.

## Change and controls

Allow only the existing R6 authorization paired with its S3 profile and the R7
authorization paired with its R7 profile. Keep exact profile file SHA, decoded
JSON equality, coordinator-owned run identity, environment and profile phase
agreement, Cloud opt-in, and `profile_accepted == false` checks. Unknown or
cross-paired phases and profiles must fail closed. The focused target, compiler,
domain, proof cases, and acceptance rules remain fixed.

Exercise the extracted profile-binding validator with temporary synthetic
profiles and a temporary proof root. Do not run compiler, preparation, tool
reconstruction, or proof code on the local host.
