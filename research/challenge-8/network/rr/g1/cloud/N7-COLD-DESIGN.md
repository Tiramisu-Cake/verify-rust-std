# N7 cold image design

## Defect and applicability

The inherited N6 candidate cannot build the authorized N7 image: it requires a preassembled Debian bundle, Cargo vendor archive, and offline Cargo config, while the N7 owner directions explicitly authorize networked Cloud Build with pinned Rust archives and crates fetched from crates.io under the exact RefinedRust lockfile. It also builds with `--offline`, so removing only the input checks would still leave the candidate unusable.

This applies only to the cold `network-rr-g1` image build in Cloud Build. It does not change the RefinedRust source, warm G1 runner, other lanes, or local execution policy.

## Invariants

- Pin the Ubuntu base by its existing digest, each nightly-2026-08-28 archive by the SHA-256 in `IMAGE-INPUTS.json`, the RR checkout to commit `332d945fafa14bf55c0c8390cb35ec4b0c012cff` and tree `b33bcccb…`, and `rr_frontend/Cargo.lock` to its recorded SHA-256.
- Fetch/build crates with Cargo `--locked`; do not patch RR or substitute project sources.
- Preserve compiler and Cargo executables at `/opt/rust/bin/rustc` and `/opt/rust/bin/cargo`; set `CARGO_HOME=/opt/g1-cargo` for warm offline core dependencies.
- The in-image receipt records compiler, lockfile, clean RR identity, installed apt package inventory, archive and binary hashes, and Cargo home configuration state. The registry digest is bound externally after push to avoid circular image hashing.
- Cold image construction, archive downloads, apt, Git clone, and Cargo compilation run only inside authorized Cloud Build.

## Distinguishing controls

Validate each archive checksum before extraction; reject wrong compiler `-Vv`, RR commit/tree/dirty state, lockfile hash, and missing built binaries; require Cargo's locked resolution. Receipt handling must preserve the original build/push failure and any partial evidence. The script must reject execution unless both Cloud Build identity variables are present. Synthetic helper coverage must include success, error, timeout, partial, missing, null, wrong type, explicit `NOT_RUN`, and source-stage mismatch where a helper parses service results.

## Chosen route

Use the owner-approved online image route: install build prerequisites from Ubuntu apt, download the pinned official Rust archives, clone the exact RR commit, fetch locked crates online and build them with the pinned compiler. Cargo's runtime home remains `/opt/g1-cargo`; its config is optional and is reported as absent unless the build context explicitly provides one. The external image digest and registry receipt remain the responsibility of the Cloud build wrapper after a successful push.
