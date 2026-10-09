# O26 shadow evidence packaging repair — 2026-10-09

Build `546547c0` ran the refreshed component-17 controls but its upload stage
refused `allprooflogs/cases/owner17-controls/forget_cleanup_to_bb23/nine-body-a1-owned-forget/mutation-profile/bin/**`.
The packager reported no identity manifest at the adjacent
`mutation-profile.json`; no archive or complete published evidence exists for
that build. Its verifier output is diagnostic only.

**Hypothesis.** Both new shadow generators call the historical `make_shadow`,
which creates an adjacent regular JSON manifest with the four required SHA-256
identities. The packager indexes only manifests whose immediate grandparent is
named `cases`. The new owner17 and isolated A1 cases have additional case
directories, so their valid manifests are not indexed. The tree exclusion then
fails despite an adjacent manifest.

**Repair scope.** Index manifests at any depth strictly below
`allprooflogs/cases/` when their adjacent `mutation-profile/bin` exists, and
retain the existing four-field SHA-256 validation and missing-manifest refusal.
Do not alter the proof, shadow generator, source/typed-MIR contracts, or the
list of excluded files. Every exclusion must still name its own adjacent
validated manifest and preserve the manifest itself in the archive.

**Falsifiable next hosted check.** With a newly committed infrastructure SHA,
the next build must package the complete archive and separately published text
logs. The manifest must record each excluded owner17/A1 tool-tree path with its
own case manifest hash and four identities. A missing or malformed manifest
must still fail packaging. The lost artifact from `546547c0` cannot be inferred
from the new run; all proof and diagnostic classifications require inspection
of that run's complete evidence.
